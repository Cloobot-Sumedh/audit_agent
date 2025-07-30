#!/usr/bin/env python3
"""
Test script to verify AI summary generation and dependency analysis during extraction
"""

import requests
import json
import time

def test_extraction_with_ai():
    """Test extraction with AI summary generation and dependency analysis"""
    try:
        print("🧪 Testing Extraction with AI Summary and Dependency Analysis...")
        print("=" * 60)
        
        # Test 1: Trigger a new extraction
        print("\n🔍 Step 1: Triggering new metadata extraction...")
        
        # Get an integration to use for extraction
        response = requests.get('http://localhost:5000/api/integrations/user/243')
        if response.status_code != 200:
            print("❌ Could not get integrations")
            return
            
        data = response.json()
        if not data.get('success') or not data.get('integrations'):
            print("❌ No integrations found")
            return
            
        integration = data['integrations'][0]
        integration_id = integration['i_id']
        print(f"✅ Using integration ID: {integration_id}")
        
        # Trigger extraction
        response = requests.post(f'http://localhost:5000/api/dashboard/extract/{integration_id}')
        if response.status_code != 200:
            print("❌ Failed to trigger extraction")
            return
            
        data = response.json()
        if not data.get('success'):
            print("❌ Extraction failed to start")
            return
            
        job_id = data['job_id']
        print(f"✅ Extraction started with job ID: {job_id}")
        
        # Test 2: Monitor job status
        print("\n🔍 Step 2: Monitoring extraction progress...")
        max_attempts = 30  # 5 minutes max
        for i in range(max_attempts):
            response = requests.get(f'http://localhost:5000/api/dashboard/job-status/{job_id}')
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                progress = data.get('progress', [])
                
                print(f"   Status: {status}")
                if progress:
                    print(f"   Latest: {progress[-1]}")
                
                if status == 'success':
                    print("✅ Extraction completed successfully!")
                    break
                elif status == 'error':
                    print(f"❌ Extraction failed: {data.get('error', 'Unknown error')}")
                    return
                elif i == max_attempts - 1:
                    print("❌ Extraction timed out")
                    return
                    
            time.sleep(10)  # Wait 10 seconds between checks
        
        # Test 3: Check for AI summaries and dependencies
        print("\n🔍 Step 3: Checking for AI summaries and dependencies...")
        
        # Get the latest job for this integration
        response = requests.get(f'http://localhost:5000/api/extraction-jobs/integration/{integration_id}')
        if response.status_code == 200:
            data = response.json()
            if data.get('jobs'):
                latest_job = data['jobs'][0]
                job_id = latest_job['aej_id']
                print(f"✅ Latest job ID: {job_id}")
                
                # Get components from this job
                response = requests.get(f'http://localhost:5000/api/metadata-components/{job_id}')
                if response.status_code == 200:
                    data = response.json()
                    components = data.get('components', [])
                    print(f"✅ Found {len(components)} components")
                    
                    # Check a few components for AI summaries
                    for i, component in enumerate(components[:3]):
                        print(f"\n   Component {i+1}: {component.get('amc_dev_name', 'Unknown')}")
                        print(f"   Type: {component.get('metadata_type_name', 'Unknown')}")
                        
                        # Check AI summary
                        ai_summary = component.get('amc_ai_summary', '')
                        if ai_summary and ai_summary != "This is a placeholder AI summary for ":
                            print(f"   ✅ AI Summary: {len(ai_summary)} characters")
                        else:
                            print(f"   ❌ No AI summary found")
                        
                        # Check dependencies
                        component_id = component['amc_id']
                        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/dependencies')
                        if response.status_code == 200:
                            dep_data = response.json()
                            dep_count = dep_data.get('count', 0)
                            print(f"   📊 Dependencies: {dep_count} found")
                        else:
                            print(f"   ❌ Could not check dependencies")
                
                # Test 4: Check dependency network
                print("\n🔍 Step 4: Testing dependency network...")
                if components:
                    test_component = components[0]
                    component_id = test_component['amc_id']
                    
                    response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/dependency-network')
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            network = data.get('network', {})
                            nodes = network.get('nodes', [])
                            edges = network.get('edges', [])
                            stats = data.get('stats', {})
                            
                            print(f"   ✅ Network data retrieved")
                            print(f"   📊 Nodes: {len(nodes)}")
                            print(f"   📊 Edges: {len(edges)}")
                            print(f"   📊 Total relationships: {stats.get('total_relationships', 0)}")
                        else:
                            print(f"   ❌ Network data failed: {data.get('error')}")
                    else:
                        print(f"   ❌ Could not get network data")
        
        print("\n" + "=" * 60)
        print("🎯 AI Summary and Dependency Analysis Test Complete!")
        print("📱 Try clicking on metadata components to see AI summaries and dependencies")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing extraction with AI: {e}")

if __name__ == "__main__":
    test_extraction_with_ai() 