#!/usr/bin/env python3
"""
Test script to verify that lists are properly loaded with their components
"""

import requests
import json

def test_list_loading():
    """Test that lists are properly loaded with their components"""
    try:
        print("🧪 Testing List Loading with Components...")
        print("=" * 50)
        
        # Test 1: Get user's MyLists
        print("\n🔍 Step 1: Getting user's MyLists...")
        response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                mylists = data.get('mylists', [])
                print(f"✅ Found {len(mylists)} MyLists for user")
                
                # Test 2: Get components for each list
                for mylist in mylists:
                    list_id = mylist.get('aml_id')
                    list_name = mylist.get('aml_name')
                    
                    print(f"\n🔍 Step 2: Getting components for '{list_name}' (ID: {list_id})...")
                    response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            components = data.get('components', [])
                            print(f"✅ Found {len(components)} components in '{list_name}'")
                            
                            if components:
                                print("   Components:")
                                for comp in components:
                                    print(f"   - {comp['amc_dev_name']} ({comp['metadata_type_name']})")
                                    print(f"     Added: {comp['almm_created_timestamp']}")
                                    print(f"     Notes: {comp['almm_notes']}")
                            else:
                                print("   (No components in this list)")
                        else:
                            print(f"❌ Failed to get components: {data.get('error')}")
                    else:
                        print(f"❌ Failed to get components: {response.status_code}")
                
                # Test 3: Test adding a component to a list
                if mylists:
                    test_list = mylists[0]
                    list_id = test_list.get('aml_id')
                    list_name = test_list.get('aml_name')
                    
                    print(f"\n🔍 Step 3: Testing add component to '{list_name}'...")
                    
                    # Get a component to add
                    response = requests.get('http://localhost:5000/api/metadata-components/8')
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success') and data.get('components'):
                            component = data['components'][0]
                            component_id = component['amc_id']
                            
                            # Add component to list
                            add_data = {
                                'org_id': 409,
                                'component_id': component_id,
                                'notes': 'Added via list loading test'
                            }
                            
                            response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get('success'):
                                    print(f"✅ Component {component['amc_dev_name']} added to '{list_name}'")
                                    
                                    # Verify the component was added
                                    response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
                                    if response.status_code == 200:
                                        data = response.json()
                                        if data.get('success'):
                                            components = data.get('components', [])
                                            print(f"✅ List now has {len(components)} components")
                                            
                                            # Remove the test component
                                            response = requests.delete(f'http://localhost:5000/api/mylists/{list_id}/components/{component_id}')
                                            if response.status_code == 200:
                                                print(f"✅ Test component removed from '{list_name}'")
                                            else:
                                                print(f"⚠️ Could not remove test component: {response.status_code}")
                                        else:
                                            print(f"❌ Failed to verify component addition: {data.get('error')}")
                                    else:
                                        print(f"❌ Failed to verify component addition: {response.status_code}")
                                else:
                                    print(f"❌ Failed to add component: {data.get('error')}")
                            else:
                                print(f"❌ Failed to add component: {response.status_code}")
                        else:
                            print("❌ No components available to add")
                    else:
                        print(f"❌ Failed to get components: {response.status_code}")
                else:
                    print("❌ No lists available for testing")
            else:
                print(f"❌ Failed to get MyLists: {data.get('error')}")
        else:
            print(f"❌ Failed to get MyLists: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing list loading: {e}")

if __name__ == "__main__":
    test_list_loading()
    
    print("\n" + "=" * 50)
    print("🎯 List Loading Test Complete!")
    print("📱 Lists should now load with their components automatically")
    print("🔄 The frontend should display all lists with their components when you click 'My Lists'") 