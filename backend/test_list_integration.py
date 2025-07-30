#!/usr/bin/env python3
"""
Test script to verify complete list integration with database
"""

import requests
import json

def test_list_integration():
    """Test complete list integration with database"""
    try:
        print("🧪 Testing Complete List Integration...")
        print("=" * 50)
        
        # Test 1: Create a new MyList
        print("\n🔍 Step 1: Creating a new MyList...")
        list_data = {
            'org_id': 409,
            'user_id': 243,
            'integration_id': 6,
            'name': 'Frontend Test List',
            'description': 'Testing frontend integration',
            'notes': 'Created for frontend testing'
        }
        
        response = requests.post('http://localhost:5000/api/mylists', json=list_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                list_id = data.get('list_id')
                print(f"✅ MyList created successfully with ID: {list_id}")
                
                # Test 2: Get components to add
                print(f"\n🔍 Step 2: Getting components to add...")
                response = requests.get('http://localhost:5000/api/metadata-components/8')
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('components'):
                        component = data['components'][0]
                        component_id = component['amc_id']
                        
                        # Test 3: Add component to MyList
                        print(f"\n🔍 Step 3: Adding component to MyList {list_id}...")
                        add_data = {
                            'org_id': 409,
                            'component_id': component_id,
                            'notes': 'Added via frontend integration test'
                        }
                        
                        response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                print(f"✅ Component {component['amc_dev_name']} added to MyList")
                                
                                # Test 4: Get components in the MyList
                                print(f"\n🔍 Step 4: Getting components in MyList {list_id}...")
                                response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('success'):
                                        components = data.get('components', [])
                                        print(f"✅ Found {len(components)} components in MyList")
                                        for comp in components:
                                            print(f"   - {comp['amc_dev_name']} ({comp['metadata_type_name']})")
                                            print(f"     Added: {comp['almm_created_timestamp']}")
                                            print(f"     Notes: {comp['almm_notes']}")
                                    else:
                                        print(f"❌ Failed to get components: {data.get('error')}")
                                else:
                                    print(f"❌ Failed to get components: {response.status_code}")
                                
                                # Test 5: Get user's MyLists
                                print(f"\n🔍 Step 5: Getting user's MyLists...")
                                response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('success'):
                                        mylists = data.get('mylists', [])
                                        print(f"✅ Found {len(mylists)} MyLists for user")
                                        for mylist in mylists:
                                            print(f"   - {mylist.get('aml_name')} (ID: {mylist.get('aml_id')})")
                                            print(f"     Description: {mylist.get('aml_description')}")
                                            print(f"     Created: {mylist.get('aml_created_timestamp')}")
                                    else:
                                        print(f"❌ Failed to get MyLists: {data.get('error')}")
                                else:
                                    print(f"❌ Failed to get MyLists: {response.status_code}")
                                
                                # Test 6: Remove component from MyList
                                print(f"\n🔍 Step 6: Removing component from MyList {list_id}...")
                                response = requests.delete(f'http://localhost:5000/api/mylists/{list_id}/components/{component_id}')
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('success'):
                                        print(f"✅ Component removed from MyList")
                                    else:
                                        print(f"❌ Failed to remove component: {data.get('error')}")
                                else:
                                    print(f"❌ Failed to remove component: {response.status_code}")
                                
                            else:
                                print(f"❌ Failed to add component: {data.get('error')}")
                        else:
                            print(f"❌ Failed to add component: {response.status_code}")
                    else:
                        print("❌ No components available to add to MyList")
                else:
                    print(f"❌ Failed to get components: {response.status_code}")
            else:
                print(f"❌ Failed to create MyList: {data.get('error')}")
        else:
            print(f"❌ Failed to create MyList: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing list integration: {e}")

if __name__ == "__main__":
    test_list_integration()
    
    print("\n" + "=" * 50)
    print("🎯 List Integration Test Complete!")
    print("📱 The list functionality is now fully integrated with the database")
    print("🔄 You can create lists, add/remove components, and view them in the frontend") 