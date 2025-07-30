import requests
import json

def create_test_data():
    print("🧪 Creating test data for list object details test...")
    
    try:
        # 1. Create a test list using existing user and org
        print("1. Creating test list...")
        list_data = {
            "org_id": 1,  # Use org ID 1
            "user_id": 1,  # Use user ID 1
            "integration_id": 26,  # Use existing integration ID 26
            "name": "Test List for Summary Generation",
            "description": "A test list to verify list summary generation",
            "notes": "Test list created for testing list summaries",
            "created_user_id": 1  # Use user ID 1
        }
        
        list_response = requests.post('http://localhost:5000/api/mylists', json=list_data)
        if list_response.status_code != 200:
            print(f"❌ Failed to create test list: {list_response.status_code}")
            return False
            
        list_result = list_response.json()
        if not list_result.get('success'):
            print(f"❌ Failed to create test list: {list_result.get('error')}")
            return False
            
        list_id = list_result.get('list_id')
        print(f"✅ Created test list with ID: {list_id}")
        
        # 2. Get some metadata components to add to the list
        print("2. Getting metadata components...")
        components_response = requests.get('http://localhost:5000/api/metadata-components/1')
        if components_response.status_code != 200:
            print(f"❌ Failed to get metadata components: {components_response.status_code}")
            return False
            
        components_data = components_response.json()
        if not components_data.get('success'):
            print(f"❌ Failed to get metadata components: {components_data.get('error')}")
            return False
            
        components = components_data.get('components', [])
        if not components:
            print("❌ No metadata components found")
            return False
            
        print(f"✅ Found {len(components)} metadata components")
        
        # 3. Add first 3 components to the list
        print("3. Adding components to test list...")
        for i, component in enumerate(components[:3]):
            add_data = {
                "org_id": 1,
                "component_id": component['amc_id'],
                "notes": f"Added for testing list summary - component {i+1}",
                "created_user_id": 1
            }
            
            add_response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
            if add_response.status_code != 200:
                print(f"❌ Failed to add component {i+1}: {add_response.status_code}")
                continue
                
            add_result = add_response.json()
            if not add_result.get('success'):
                print(f"❌ Failed to add component {i+1}: {add_result.get('error')}")
                continue
                
            print(f"✅ Added component {i+1}: {component['amc_dev_name']}")
        
        print("✅ Test data created successfully!")
        print(f"📋 Test list ID: {list_id}")
        print("🔧 You can now run the list summary generation test")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test data: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_test_data()
    if success:
        print("\n🎉 Test data created successfully!")
    else:
        print("\n💥 Failed to create test data!") 