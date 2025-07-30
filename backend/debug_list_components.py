import requests
import json
from database import get_db_manager

def debug_list_components():
    print("🔍 Debugging list components data...")
    
    try:
        # 1. Get database manager
        db = get_db_manager()
        
        # 2. Get a list
        lists_query = """
            SELECT aml.*, i.i_name as integration_name
            FROM ids_audit_mylist aml
            JOIN ids_integration i ON aml.aml_integration_id = i.i_id
            WHERE aml.aml_status = 1
            LIMIT 1
        """
        
        lists = db.execute_query(lists_query, fetch_all=True)
        if not lists:
            print("❌ No lists found")
            return
            
        list_id = lists[0]['aml_id']
        print(f"✅ Found list with ID: {list_id}")
        
        # 3. Get components directly from database
        print("3. Getting components from database...")
        db_components = db.get_list_components(list_id)
        
        if not db_components:
            print("❌ No components found in database")
            return
            
        print(f"✅ Found {len(db_components)} components in database")
        
        # 4. Check first component structure
        first_db_component = db_components[0]
        print("4. Database component structure:")
        for key, value in first_db_component.items():
            print(f"  {key}: {type(value).__name__} = {value}")
        
        # 5. Test API endpoint
        print("5. Testing API endpoint...")
        api_response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
        
        if api_response.status_code != 200:
            print(f"❌ API failed: {api_response.status_code}")
            return
            
        api_data = api_response.json()
        if not api_data.get('success'):
            print(f"❌ API error: {api_data.get('error')}")
            return
            
        api_components = api_data.get('components', [])
        if not api_components:
            print("❌ No components in API response")
            return
            
        print(f"✅ API returned {len(api_components)} components")
        
        # 6. Check API component structure
        first_api_component = api_components[0]
        print("6. API component structure:")
        for key, value in first_api_component.items():
            print(f"  {key}: {type(value).__name__} = {value}")
        
        # 7. Compare structures
        print("7. Comparing structures...")
        db_keys = set(first_db_component.keys())
        api_keys = set(first_api_component.keys())
        
        missing_in_api = db_keys - api_keys
        missing_in_db = api_keys - db_keys
        
        if missing_in_api:
            print(f"❌ Missing in API: {missing_in_api}")
        else:
            print("✅ All database fields present in API")
            
        if missing_in_db:
            print(f"❌ Extra in API: {missing_in_db}")
        else:
            print("✅ No extra fields in API")
        
        # 8. Check specific missing fields
        expected_fields = [
            'amc_id', 'amc_dev_name', 'amc_label', 'amc_notes', 
            'amc_content', 'amc_ai_summary', 'amc_ai_model',
            'amc_last_modified', 'amc_api_version', 'amc_created_timestamp',
            'metadata_type_name'
        ]
        
        missing_expected = []
        for field in expected_fields:
            if field not in first_api_component:
                missing_expected.append(field)
        
        if missing_expected:
            print(f"❌ Missing expected fields in API: {missing_expected}")
        else:
            print("✅ All expected fields present in API")
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_list_components() 