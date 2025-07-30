#!/usr/bin/env python3
"""
Test script to verify metadata component endpoints
"""

import requests
import json

def test_metadata_components_endpoints():
    """Test the metadata component endpoints"""
    try:
        # First, get a job ID from the dashboard
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
        
        # Test 1: Get all metadata components for the job
        print("\n🔍 Testing: Get all metadata components")
        response = requests.get(f'http://localhost:5000/api/metadata-components/{job_id}')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ All components: {data.get('count', 0)} found")
            if data.get('components'):
                print(f"   First component: {data['components'][0].get('amc_dev_name', 'Unknown')}")
        else:
            print(f"❌ Failed to get all components: {response.status_code}")
        
        # Test 2: Get components by type (CustomObject)
        print("\n🔍 Testing: Get CustomObject components")
        response = requests.get(f'http://localhost:5000/api/metadata-components/{job_id}/type/CustomObject')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CustomObject components: {data.get('count', 0)} found")
            if data.get('components'):
                print(f"   First CustomObject: {data['components'][0].get('amc_dev_name', 'Unknown')}")
        else:
            print(f"❌ Failed to get CustomObject components: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test 3: Search components
        print("\n🔍 Testing: Search components")
        response = requests.get(f'http://localhost:5000/api/metadata-components/{job_id}/type/CustomObject/search?search_term=Account')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search results: {data.get('count', 0)} found")
            if data.get('components'):
                print(f"   First result: {data['components'][0].get('amc_dev_name', 'Unknown')}")
        else:
            print(f"❌ Failed to search components: {response.status_code}")
        
        # Test 4: Get specific component
        if data.get('components'):
            component_id = data['components'][0]['amc_id']
            print(f"\n🔍 Testing: Get specific component {component_id}")
            response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}')
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Component details retrieved")
                print(f"   Name: {data.get('component', {}).get('amc_dev_name', 'Unknown')}")
                print(f"   Type: {data.get('component', {}).get('metadata_type_name', 'Unknown')}")
            else:
                print(f"❌ Failed to get component: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing metadata components: {e}")

if __name__ == "__main__":
    print("🧪 Testing Metadata Component Endpoints...")
    print("=" * 50)
    
    test_metadata_components_endpoints()
    
    print("\n" + "=" * 50)
    print("🎯 Metadata explorer should now show components when you click on types!")
    print("📱 Try clicking on 'CustomObject' in the metadata explorer") 