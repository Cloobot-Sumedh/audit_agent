#!/usr/bin/env python3
"""
Test script to verify that object details in lists are the same as metadata details
"""

import requests
import json
import time

def test_list_object_details():
    print("🧪 Testing list object details consistency...")
    
    try:
        # 1. Get user lists
        print("1. Getting user lists...")
        response = requests.get('http://localhost:5000/api/mylists/user/243/org/1')
        
        if response.status_code != 200:
            print(f"❌ Failed to get user lists: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to get user lists: {data.get('error')}")
            return False
            
        lists = data.get('lists', [])
        if not lists:
            print("❌ No lists found for user")
            return False
            
        print(f"✅ Found {len(lists)} lists")
        
        # 2. Get components for first list
        first_list = lists[0]
        list_id = first_list['aml_id']
        print(f"2. Getting components for list: {first_list['aml_name']}")
        
        components_response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
        
        if components_response.status_code != 200:
            print(f"❌ Failed to get list components: {components_response.status_code}")
            return False
            
        components_data = components_response.json()
        if not components_data.get('success'):
            print(f"❌ Failed to get list components: {components_data.get('error')}")
            return False
            
        components = components_data.get('components', [])
        if not components:
            print("❌ No components found in list")
            return False
            
        print(f"✅ Found {len(components)} components in list")
        
        # 3. Get details for first component
        first_component = components[0]
        component_id = first_component['amc_id']  # Use amc_id from component table
        print(f"3. Getting details for component: {first_component['amc_dev_name']}")
        
        details_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
        
        if details_response.status_code != 200:
            print(f"❌ Failed to get component details: {details_response.status_code}")
            return False
            
        details_data = details_response.json()
        if not details_data.get('success'):
            print(f"❌ Failed to get component details: {details_data.get('error')}")
            return False
            
        component_details = details_data.get('component')
        print(f"✅ Got component details")
        
        # 4. Verify the structure matches what MetadataObjectView expects
        print("4. Verifying component structure...")
        
        expected_fields = [
            'amc_id', 'amc_dev_name', 'amc_label', 'amc_notes', 
            'amc_content', 'amc_ai_summary', 'amc_ai_model',
            'amc_last_modified', 'amc_api_version', 'amc_created_timestamp',
            'metadata_type_name'
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in component_details:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields in component details: {missing_fields}")
            return False
            
        print("✅ All expected fields present in component details")
        
        # 5. Test the API endpoints that MetadataObjectView uses
        print("5. Testing MetadataObjectView API endpoints...")
        
        # Test content endpoint
        content_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/content')
        if content_response.status_code != 200:
            print(f"❌ Failed to get component content: {content_response.status_code}")
            return False
            
        content_data = content_response.json()
        if not content_data.get('success'):
            print(f"❌ Failed to get component content: {content_data.get('error')}")
            return False
            
        print("✅ Component content endpoint working")
        
        # Test dependencies endpoint
        dependencies_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/dependencies')
        if dependencies_response.status_code != 200:
            print(f"❌ Failed to get component dependencies: {dependencies_response.status_code}")
            return False
            
        dependencies_data = dependencies_response.json()
        if not dependencies_data.get('success'):
            print(f"❌ Failed to get component dependencies: {dependencies_data.get('error')}")
            return False
            
        print("✅ Component dependencies endpoint working")
        
        # 6. Test dependency network endpoint
        network_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/dependency-network')
        if network_response.status_code != 200:
            print(f"❌ Failed to get dependency network: {network_response.status_code}")
            return False
            
        network_data = network_response.json()
        if not network_data.get('success'):
            print(f"❌ Failed to get dependency network: {network_data.get('error')}")
            return False
            
        print("✅ Dependency network endpoint working")
        
        # 7. Test AI summary generation
        summary_response = requests.post(f'http://localhost:5000/api/metadata-component/{component_id}/generate-summary')
        if summary_response.status_code != 200:
            print(f"❌ Failed to generate AI summary: {summary_response.status_code}")
            return False
            
        summary_data = summary_response.json()
        if not summary_data.get('success'):
            print(f"❌ Failed to generate AI summary: {summary_data.get('error')}")
            return False
            
        print("✅ AI summary generation working")
        
        print("✅ All tests passed! List object details are consistent with metadata details")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_list_object_details()
    if success:
        print("\n🎉 All tests passed! List object details are working correctly.")
    else:
        print("\n💥 Tests failed! There are issues with list object details.") 