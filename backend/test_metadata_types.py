#!/usr/bin/env python3
"""
Test script to check metadata types in database
"""

import requests
import json

def test_metadata_types():
    """Check what metadata types are available"""
    try:
        # Get metadata types from the database
        response = requests.get('http://localhost:5000/api/metadata-types/org/409')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Metadata types found:")
            for mt in data.get('metadata_types', []):
                print(f"   - {mt.get('amt_name')} (ID: {mt.get('amt_id')})")
        else:
            print(f"❌ Failed to get metadata types: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error checking metadata types: {e}")

def test_components_by_job():
    """Check what components exist for a job"""
    try:
        # Get a job ID first
        response = requests.get('http://localhost:5000/api/dashboard/user/243/org/409')
        
        if response.status_code != 200:
            print("❌ Could not get dashboard data")
            return
            
        data = response.json()
        if not data.get('success') or not data.get('integrations'):
            print("❌ No integrations found")
            return
            
        # Get the first integration with a completed job
        integration = data['integrations'][0]
        latest_job = integration.get('latest_job')
        
        if not latest_job or latest_job.get('aej_job_status') != 'completed':
            print("❌ No completed jobs found")
            return
            
        job_id = latest_job['aej_id']
        print(f"✅ Using job ID: {job_id}")
        
        # Get all components for this job
        response = requests.get(f'http://localhost:5000/api/metadata-components/{job_id}')
        
        if response.status_code == 200:
            data = response.json()
            components = data.get('components', [])
            print(f"\n✅ Found {len(components)} components")
            
            # Group by metadata type
            type_counts = {}
            for comp in components:
                type_name = comp.get('metadata_type_name', 'Unknown')
                if type_name not in type_counts:
                    type_counts[type_name] = []
                type_counts[type_name].append(comp.get('amc_dev_name'))
            
            print("\n📊 Components by type:")
            for type_name, components_list in type_counts.items():
                print(f"   {type_name}: {len(components_list)} components")
                if len(components_list) <= 5:
                    for comp_name in components_list:
                        print(f"     - {comp_name}")
                else:
                    print(f"     - {components_list[0]} (and {len(components_list)-1} more)")
        else:
            print(f"❌ Failed to get components: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error checking components: {e}")

if __name__ == "__main__":
    print("🔍 Checking Metadata Types and Components...")
    print("=" * 50)
    
    test_metadata_types()
    print()
    test_components_by_job()
    
    print("\n" + "=" * 50)
    print("💡 This will help us understand the correct metadata type names to use") 