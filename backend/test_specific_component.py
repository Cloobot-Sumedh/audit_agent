import requests
import json

def test_specific_component():
    print("🧪 Testing specific component (ProductConfigMetadataUpdater)...")
    
    try:
        # 1. Get the specific component details
        print("1. Getting component 4703 details...")
        component_response = requests.get('http://localhost:5000/api/metadata-component/4703')
        if component_response.status_code != 200:
            print(f"❌ Failed to get component: {component_response.status_code}")
            return False
            
        component_data = component_response.json()
        if not component_data.get('success'):
            print(f"❌ Failed to get component: {component_data.get('error')}")
            return False
            
        component = component_data.get('component', {})
        print(f"✅ Component details:")
        print(f"   Name: {component.get('amc_dev_name', 'Unknown')}")
        print(f"   Type: {component.get('metadata_type_name', 'Unknown')}")
        print(f"   Created: {component.get('amc_created_timestamp', 'Unknown')}")
        print(f"   Notes: {component.get('amc_notes', 'Unknown')}")
        
        # 2. Add this component to list 9
        print("\n2. Adding component to list 9...")
        add_data = {
            "org_id": 1,
            "component_id": 4703,
            "notes": "Added ProductConfigMetadataUpdater for testing"
        }
        
        add_response = requests.post('http://localhost:5000/api/mylists/9/components', json=add_data)
        print(f"Response status: {add_response.status_code}")
        
        if add_response.status_code == 200:
            result = add_response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Failed to add component: {add_response.text}")
            return False
        
        # 3. Check the list components
        print("\n3. Checking list components...")
        list_response = requests.get('http://localhost:5000/api/mylists/9/components')
        if list_response.status_code == 200:
            list_data = list_response.json()
            components = list_data.get('components', [])
            print(f"✅ List now has {len(components)} components")
            
            # Find the ProductConfigMetadataUpdater component
            target_component = None
            for comp in components:
                if comp.get('amc_id') == 4703:
                    target_component = comp
                    break
            
            if target_component:
                print(f"\n   ProductConfigMetadataUpdater details:")
                print(f"     ID: {target_component.get('amc_id')}")
                print(f"     Name: {target_component.get('amc_dev_name', 'Unknown')}")
                print(f"     Type: {target_component.get('metadata_type_name', 'Unknown')}")
                print(f"     Created: {target_component.get('amc_created_timestamp', 'Unknown')}")
                print(f"     Notes: {target_component.get('amc_notes', 'Unknown')}")
                print(f"     AI Summary: {target_component.get('amc_ai_summary', 'Unknown')}")
                print(f"     API Version: {target_component.get('amc_api_version', 'Unknown')}")
                print(f"     AI Model: {target_component.get('amc_ai_model', 'Unknown')}")
                
                # Check if all required fields are present
                required_fields = [
                    'amc_id', 'amc_dev_name', 'amc_label', 'amc_created_timestamp',
                    'amc_notes', 'amc_ai_summary', 'amc_api_version', 'amc_last_modified',
                    'amc_ai_model', 'metadata_type_name'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in target_component or target_component[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"     ⚠️ Missing fields: {missing_fields}")
                else:
                    print(f"     ✅ All required fields present")
            else:
                print("❌ ProductConfigMetadataUpdater not found in list")
        else:
            print(f"❌ Failed to get list components: {list_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_specific_component() 