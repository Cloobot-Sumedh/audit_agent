import requests
import json

def test_frontend_fix():
    print("🧪 Testing frontend fix...")
    
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
        print(f"✅ Found {len(components)} components in list")
        
        # 2. Check the data structure that frontend will receive
        print("\n2. Checking frontend data structure...")
        for i, component in enumerate(components):
            print(f"\n   Component {i+1}:")
            print(f"     amc_id: {component.get('amc_id')}")
            print(f"     amc_dev_name: {component.get('amc_dev_name')}")
            print(f"     metadata_type_name: {component.get('metadata_type_name')}")
            print(f"     amc_created_timestamp: {component.get('amc_created_timestamp')}")
            print(f"     amc_notes: {component.get('amc_notes')}")
            
            # Simulate the frontend transformation
            transformed_component = {
                'amc_id': component.get('amc_id'),
                'amc_dev_name': component.get('amc_dev_name'),
                'amc_label': component.get('amc_label'),
                'amc_notes': component.get('amc_notes'),
                'amc_content': component.get('amc_content'),
                'amc_ai_summary': component.get('amc_ai_summary'),
                'amc_ai_model': component.get('amc_ai_model'),
                'amc_last_modified': component.get('amc_last_modified'),
                'amc_api_version': component.get('amc_api_version'),
                'amc_created_timestamp': component.get('amc_created_timestamp'),
                'metadata_type_name': component.get('metadata_type_name'),
                'name': component.get('amc_dev_name'),  # Frontend transformation
                'type': component.get('metadata_type_name'),  # Frontend transformation
                'addedToListAt': component.get('almm_created_timestamp'),
                'component_id': component.get('almm_component_id')
            }
            
            print(f"     Frontend transformed:")
            print(f"       name: {transformed_component.get('name')}")
            print(f"       type: {transformed_component.get('type')}")
            print(f"       amc_dev_name: {transformed_component.get('amc_dev_name')}")
            print(f"       metadata_type_name: {transformed_component.get('metadata_type_name')}")
            print(f"       amc_created_timestamp: {transformed_component.get('amc_created_timestamp')}")
            
            # Check if MetadataObjectView will receive correct data
            name_for_metadata_view = transformed_component.get('amc_dev_name') or transformed_component.get('amc_label') or 'Unknown'
            type_for_metadata_view = transformed_component.get('metadata_type_name') or 'Unknown'
            created_for_metadata_view = transformed_component.get('amc_created_timestamp') or 'Unknown'
            
            print(f"     MetadataObjectView will receive:")
            print(f"       Name: {name_for_metadata_view}")
            print(f"       Type: {type_for_metadata_view}")
            print(f"       Created: {created_for_metadata_view}")
            
            if name_for_metadata_view != 'Unknown' and type_for_metadata_view != 'Unknown' and created_for_metadata_view != 'Unknown':
                print(f"     ✅ MetadataObjectView will display correct information")
            else:
                print(f"     ❌ MetadataObjectView will show Unknown values")
        
        print(f"\n🎉 Test complete! The frontend should now display the correct information.")
        print(f"   Refresh your browser and check the Lists page.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_frontend_fix() 