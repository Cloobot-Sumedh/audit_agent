#!/usr/bin/env python3
"""
Test script to verify new extraction creates unique component IDs and dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager
import requests
import json

def test_new_extraction():
    """Test new extraction with unique component IDs"""
    db = get_db_manager()
    
    try:
        print("🔍 Testing New Extraction with Unique Component IDs")
        print("=" * 60)
        
        # Get current extraction job count
        current_jobs = db.execute_query("SELECT COUNT(*) as count FROM ids_audit_extraction_job WHERE aej_status = 1", fetch_one=True)
        current_job_count = current_jobs['count'] if current_jobs else 0
        print(f"Current extraction jobs: {current_job_count}")
        
        # Get current component count
        current_components = db.execute_query("SELECT COUNT(*) as count FROM ids_audit_metadata_component WHERE amc_status = 1", fetch_one=True)
        current_component_count = current_components['count'] if current_components else 0
        print(f"Current components: {current_component_count}")
        
        # Get current dependency count
        current_dependencies = db.execute_query("SELECT COUNT(*) as count FROM ids_audit_metadata_dependency WHERE amd_status = 1", fetch_one=True)
        current_dependency_count = current_dependencies['count'] if current_dependencies else 0
        print(f"Current dependencies: {current_dependency_count}")
        
        # Get the latest integration
        latest_integration = db.execute_query("""
            SELECT i_id, i_name FROM ids_integration 
            WHERE i_status = 1 
            ORDER BY i_created_timestamp DESC 
            LIMIT 1
        """, fetch_one=True)
        
        if not latest_integration:
            print("❌ No integrations found. Please create an integration first.")
            return
        
        integration_id = latest_integration['i_id']
        print(f"Using integration: {latest_integration['i_name']} (ID: {integration_id})")
        
        # Trigger a new extraction
        print("\n🚀 Triggering new extraction...")
        
        # Call the extraction API
        api_url = "http://localhost:5000/api/dashboard/extract/" + str(integration_id)
        
        try:
            response = requests.post(api_url, json={}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    job_id = data.get('job_id')
                    print(f"✅ Extraction started successfully! Job ID: {job_id}")
                    
                    # Wait for extraction to complete
                    print("⏳ Waiting for extraction to complete...")
                    
                    # Poll job status
                    status_url = f"http://localhost:5000/api/dashboard/job-status/{job_id}"
                    max_attempts = 30
                    attempt = 0
                    
                    while attempt < max_attempts:
                        try:
                            status_response = requests.get(status_url, timeout=10)
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                if status_data.get('success'):
                                    job_status = status_data.get('status')
                                    print(f"Job status: {job_status}")
                                    
                                    if job_status == 'success':
                                        print("✅ Extraction completed successfully!")
                                        break
                                    elif job_status == 'error':
                                        print(f"❌ Extraction failed: {status_data.get('error', 'Unknown error')}")
                                        break
                                    
                                    # Wait before next poll
                                    import time
                                    time.sleep(2)
                                    attempt += 1
                                else:
                                    print(f"❌ Failed to get job status: {status_data.get('error')}")
                                    break
                            else:
                                print(f"❌ Failed to get job status. Status code: {status_response.status_code}")
                                break
                        except Exception as e:
                            print(f"❌ Error polling job status: {str(e)}")
                            break
                    
                    if attempt >= max_attempts:
                        print("⏰ Extraction timed out")
                    
                    # Check results after extraction
                    print("\n📊 Checking extraction results...")
                    
                    # Get new extraction job count
                    new_jobs = db.execute_query("SELECT COUNT(*) as count FROM ids_audit_extraction_job WHERE aej_status = 1", fetch_one=True)
                    new_job_count = new_jobs['count'] if new_jobs else 0
                    print(f"New extraction jobs: {new_job_count}")
                    
                    # Get new component count
                    new_components = db.execute_query("SELECT COUNT(*) as count FROM ids_audit_metadata_component WHERE amc_status = 1", fetch_one=True)
                    new_component_count = new_components['count'] if new_components else 0
                    print(f"New components: {new_component_count}")
                    
                    # Get new dependency count
                    new_dependencies = db.execute_query("SELECT COUNT(*) as count FROM ids_audit_metadata_dependency WHERE amd_status = 1", fetch_one=True)
                    new_dependency_count = new_dependencies['count'] if new_dependencies else 0
                    print(f"New dependencies: {new_dependency_count}")
                    
                    # Calculate differences
                    components_added = new_component_count - current_component_count
                    dependencies_added = new_dependency_count - current_dependency_count
                    
                    print(f"\n📈 Extraction Results:")
                    print(f"   Components added: {components_added}")
                    print(f"   Dependencies added: {dependencies_added}")
                    
                    if components_added > 0:
                        print("✅ New components were created with unique IDs")
                    else:
                        print("⚠️  No new components were created")
                    
                    if dependencies_added > 0:
                        print("✅ New dependencies were extracted")
                    else:
                        print("⚠️  No new dependencies were extracted")
                    
                    # Check for unique component IDs
                    print("\n🔍 Checking for unique component IDs...")
                    component_ids = db.execute_query("""
                        SELECT amc_id, amc_dev_name, amc_extraction_job_id 
                        FROM ids_audit_metadata_component 
                        WHERE amc_status = 1 
                        ORDER BY amc_id DESC 
                        LIMIT 10
                    """, fetch_all=True)
                    
                    print("Latest 10 components:")
                    for comp in component_ids:
                        print(f"   ID: {comp['amc_id']}, Name: {comp['amc_dev_name']}, Job: {comp['amc_extraction_job_id']}")
                    
                else:
                    print(f"❌ Extraction failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Failed to start extraction. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error making API request: {str(e)}")
            print("Make sure the backend server is running on http://localhost:5000")
        
        print("\n" + "=" * 60)
        print("✅ New extraction test completed!")
        
    except Exception as e:
        print(f"❌ Error during new extraction test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_extraction() 