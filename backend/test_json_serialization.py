import requests
import json
from database import get_db_manager

def test_json_serialization():
    print("🧪 Testing JSON serialization of list components...")
    
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
        
        # 4. Test JSON serialization of database result
        print("4. Testing JSON serialization...")
        first_component = db_components[0]
        
        # Test direct JSON serialization
        try:
            json_str = json.dumps(first_component, default=str)
            print("✅ Direct JSON serialization successful")
            print(f"JSON length: {len(json_str)}")
            
            # Parse back to check if all fields are preserved
            parsed = json.loads(json_str)
            print(f"Parsed fields: {list(parsed.keys())}")
            
            # Check for missing fields
            expected_fields = [
                'amc_id', 'amc_dev_name', 'amc_label', 'amc_notes', 
                'amc_content', 'amc_ai_summary', 'amc_ai_model',
                'amc_last_modified', 'amc_api_version', 'amc_created_timestamp',
                'metadata_type_name'
            ]
            
            missing_fields = []
            for field in expected_fields:
                if field not in parsed:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing fields in JSON: {missing_fields}")
            else:
                print("✅ All expected fields present in JSON")
                
        except Exception as e:
            print(f"❌ JSON serialization failed: {str(e)}")
            return
        
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
        
        # 6. Compare API response with database
        api_component = api_components[0]
        print("6. Comparing API response with database...")
        
        # Check if API response has all database fields
        db_keys = set(first_component.keys())
        api_keys = set(api_component.keys())
        
        missing_in_api = db_keys - api_keys
        if missing_in_api:
            print(f"❌ Missing in API: {missing_in_api}")
        else:
            print("✅ All database fields present in API")
        
        # 7. Check specific fields that should be present
        print("7. Checking specific fields...")
        for field in ['amc_id', 'amc_notes', 'amc_ai_model', 'amc_last_modified', 'amc_api_version', 'amc_created_timestamp']:
            db_value = first_component.get(field)
            api_value = api_component.get(field)
            print(f"  {field}: DB={db_value}, API={api_value}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_serialization() 