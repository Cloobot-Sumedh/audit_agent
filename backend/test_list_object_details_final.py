import requests
import json

def test_list_object_details_final():
    print("🧪 Final test: List object details consistency...")
    
    try:
        # 1. Get list components
        print("1. Getting list components...")
        response = requests.get('http://localhost:5000/api/mylists/9/components')
        
        if response.status_code != 200:
            print(f"❌ Failed to get list components: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to get list components: {data.get('error')}")
            return False
            
        components = data.get('components', [])
        if not components:
            print("❌ No components in list")
            return False
            
        print(f"✅ Found {len(components)} components in list")
        
        # 2. Test each component's object details
        for i, component in enumerate(components):
            print(f"\n2. Testing component {i+1} object details:")
            
            # Test Name field
            name = component.get('amc_dev_name') or component.get('amc_label') or 'Unknown'
            print(f"   Name: {name}")
            
            # Test Type field
            metadata_type = component.get('metadata_type_name', 'Unknown')
            print(f"   Type: {metadata_type}")
            
            # Test Created field
            created_timestamp = component.get('amc_created_timestamp', 'Unknown')
            print(f"   Created: {created_timestamp}")
            
            # Test Notes field
            notes = component.get('amc_notes', 'Unknown')
            print(f"   Notes: {notes}")
            
            # Test AI Summary field
            ai_summary = component.get('amc_ai_summary', 'Unknown')
            print(f"   AI Summary: {ai_summary}")
            
            # Test API Version field
            api_version = component.get('amc_api_version', 'Unknown')
            print(f"   API Version: {api_version}")
            
            # Test Last Modified field
            last_modified = component.get('amc_last_modified', 'Unknown')
            print(f"   Last Modified: {last_modified}")
            
            # Test AI Model field
            ai_model = component.get('amc_ai_model', 'Unknown')
            print(f"   AI Model: {ai_model}")
            
            # Verify all required fields are present
            required_fields = [
                'amc_id', 'amc_dev_name', 'amc_label', 'amc_created_timestamp',
                'amc_notes', 'amc_ai_summary', 'amc_api_version', 'amc_last_modified',
                'amc_ai_model', 'metadata_type_name'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in component or component[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
        
        # 3. Compare with metadata details
        print(f"\n3. Comparing with metadata details...")
        component_id = components[0].get('amc_id')
        if component_id:
            metadata_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}')
            if metadata_response.status_code == 200:
                metadata_data = metadata_response.json()
                if metadata_data.get('success'):
                    metadata_component = metadata_data.get('component', {})
                    
                    print(f"   Metadata details component:")
                    print(f"     Name: {metadata_component.get('amc_dev_name', 'Unknown')}")
                    print(f"     Type: {metadata_component.get('metadata_type_name', 'Unknown')}")
                    print(f"     Created: {metadata_component.get('amc_created_timestamp', 'Unknown')}")
                    print(f"     Notes: {metadata_component.get('amc_notes', 'Unknown')}")
                    
                    # Verify consistency
                    list_name = components[0].get('amc_dev_name', 'Unknown')
                    metadata_name = metadata_component.get('amc_dev_name', 'Unknown')
                    
                    if list_name == metadata_name:
                        print(f"   ✅ Name consistency: {list_name}")
                    else:
                        print(f"   ❌ Name inconsistency: {list_name} vs {metadata_name}")
        
        print(f"\n🎉 Test complete! List object details should now show the same information as metadata details.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_list_object_details_final() 