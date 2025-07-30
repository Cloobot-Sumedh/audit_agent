import requests
import json

def setup_list_data():
    print("🔧 Setting up list data...")
    
    try:
        # 1. Create an integration first
        print("1. Creating integration...")
        integration_data = {
            "org_id": 1,
            "name": "Test Integration for Lists",
            "instance_url": "https://test.salesforce.com",
            "org_type": "sandbox",
            "token": "test_token",
            "ext_app_id": 1,
            "created_user_id": 243
        }
        
        integration_response = requests.post('http://localhost:5000/api/integrations', json=integration_data)
        if integration_response.status_code != 200:
            print(f"❌ Failed to create integration: {integration_response.status_code}")
            return False
            
        integration_result = integration_response.json()
        if not integration_result.get('success'):
            print(f"❌ Failed to create integration: {integration_result.get('error')}")
            return False
            
        integration_id = integration_result.get('integration_id')
        print(f"✅ Created integration with ID: {integration_id}")
        
        # 2. Create a list
        print("2. Creating list...")
        list_data = {
            "org_id": 1,
            "user_id": 243,
            "integration_id": integration_id,
            "name": "My Test List",
            "description": "A test list with existing metadata components",
            "notes": "Test list created for demonstration",
            "created_user_id": 243
        }
        
        list_response = requests.post('http://localhost:5000/api/mylists', json=list_data)
        if list_response.status_code != 200:
            print(f"❌ Failed to create list: {list_response.status_code}")
            return False
            
        list_result = list_response.json()
        if not list_result.get('success'):
            print(f"❌ Failed to create list: {list_result.get('error')}")
            return False
            
        list_id = list_result.get('list_id')
        print(f"✅ Created list with ID: {list_id}")
        
        # 3. Get existing metadata components
        print("3. Getting existing metadata components...")
        components_response = requests.get('http://localhost:5000/api/metadata-components/1')
        if components_response.status_code != 200:
            print(f"❌ Failed to get components: {components_response.status_code}")
            return False
            
        components_data = components_response.json()
        components = components_data.get('components', [])
        
        if not components:
            print("❌ No components found")
            return False
            
        print(f"✅ Found {len(components)} components")
        
        # 4. Add first few components to the list
        print("4. Adding components to list...")
        for i, component in enumerate(components[:3]):  # Add first 3 components
            component_id = component.get('amc_id')
            if component_id:
                add_data = {
                    "component_id": component_id,
                    "notes": f"Added component {i+1} to test list"
                }
                
                add_response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
                if add_response.status_code == 200:
                    print(f"✅ Added component {component_id} to list")
                else:
                    print(f"❌ Failed to add component {component_id}")
        
        # 5. Test the list components
        print("5. Testing list components...")
        list_components_response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
        if list_components_response.status_code == 200:
            list_components_data = list_components_response.json()
            if list_components_data.get('success'):
                components = list_components_data.get('components', [])
                print(f"✅ List now has {len(components)} components")
                
                # Test the object details
                if components:
                    first_component = components[0]
                    print(f"  First component details:")
                    print(f"    Name: {first_component.get('amc_dev_name', 'Unknown')}")
                    print(f"    Type: {first_component.get('metadata_type_name', 'Unknown')}")
                    print(f"    Created: {first_component.get('amc_created_timestamp', 'Unknown')}")
                    print(f"    Notes: {first_component.get('amc_notes', 'Unknown')}")
            else:
                print(f"❌ Failed to get list components: {list_components_data.get('error')}")
        else:
            print(f"❌ Failed to get list components: {list_components_response.status_code}")
        
        print("\n🎉 Setup complete! You can now test the list functionality.")
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        return False

if __name__ == "__main__":
    setup_list_data() 