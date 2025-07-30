import requests
import json
from database import get_db_manager

def test_list_object_details_simple():
    print("🧪 Testing list object details consistency (simple version)...")
    
    try:
        # 1. Get database manager and test the query directly
        print("1. Testing database query for list components...")
        db = get_db_manager()
        
        # First, let's check if there are any lists in the database
        lists_query = """
            SELECT aml.*, i.i_name as integration_name
            FROM ids_audit_mylist aml
            JOIN ids_integration i ON aml.aml_integration_id = i.i_id
            WHERE aml.aml_status = 1
            LIMIT 1
        """
        
        lists = db.execute_query(lists_query, fetch_all=True)
        if not lists:
            print("❌ No lists found in database")
            print("💡 This test requires at least one list with components")
            return False
            
        list_id = lists[0]['aml_id']
        print(f"✅ Found list with ID: {list_id}")
        
        # 2. Test the get_list_components query
        print("2. Testing get_list_components query...")
        components = db.get_list_components(list_id)
        
        if not components:
            print("❌ No components found in list")
            print("💡 This test requires at least one component in the list")
            return False
            
        print(f"✅ Found {len(components)} components in list")
        
        # 3. Check the structure of the first component
        print("3. Checking component structure...")
        first_component = components[0]
        
        expected_fields = [
            'amc_id', 'amc_dev_name', 'amc_label', 'amc_notes', 
            'amc_content', 'amc_ai_summary', 'amc_ai_model',
            'amc_last_modified', 'amc_api_version', 'amc_created_timestamp',
            'metadata_type_name'
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in first_component:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields in component: {missing_fields}")
            return False
            
        print("✅ All expected fields present in component")
        
        # 4. Test API endpoints with the component
        component_id = first_component['amc_id']
        print(f"4. Testing API endpoints for component ID: {component_id}")
        
        # Test details endpoint
        details_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
        if details_response.status_code != 200:
            print(f"❌ Failed to get component details: {details_response.status_code}")
            return False
            
        details_data = details_response.json()
        if not details_data.get('success'):
            print(f"❌ Failed to get component details: {details_data.get('error')}")
            return False
            
        print("✅ Component details endpoint working")
        
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
        
        # 5. Test the list components API endpoint
        print("5. Testing list components API endpoint...")
        list_components_response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
        if list_components_response.status_code != 200:
            print(f"❌ Failed to get list components: {list_components_response.status_code}")
            return False
            
        list_components_data = list_components_response.json()
        if not list_components_data.get('success'):
            print(f"❌ Failed to get list components: {list_components_data.get('error')}")
            return False
            
        list_components = list_components_data.get('components', [])
        if not list_components:
            print("❌ No components returned from API")
            return False
            
        print(f"✅ List components API returned {len(list_components)} components")
        
        # 6. Verify the API response has the same structure as database
        print("6. Verifying API response structure...")
        api_component = list_components[0]
        
        api_missing_fields = []
        for field in expected_fields:
            if field not in api_component:
                api_missing_fields.append(field)
        
        if api_missing_fields:
            print(f"❌ Missing fields in API response: {api_missing_fields}")
            return False
            
        print("✅ API response has all expected fields")
        
        print("✅ All tests passed! List object details are consistent with metadata details")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_list_object_details_simple()
    if success:
        print("\n🎉 All tests passed! List object details are working correctly.")
    else:
        print("\n💥 Tests failed! There are issues with list object details.") 