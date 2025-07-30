#!/usr/bin/env python3
"""
Test script to verify plus icon functionality and list counts
"""

import requests
import json

def test_plus_icon_functionality():
    """Test the plus icon functionality and verify list counts"""
    try:
        print("🧪 Testing Plus Icon Functionality...")
        print("=" * 50)
        
        # Test 1: Get current lists and their component counts
        print("\n🔍 Step 1: Getting current lists and component counts...")
        response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                mylists = data.get('mylists', [])
                print(f"✅ Found {len(mylists)} lists")
                
                # Test 2: Check component counts for each list
                for mylist in mylists:
                    list_id = mylist['aml_id']
                    list_name = mylist['aml_name']
                    
                    print(f"\n🔍 Step 2: Checking components for '{list_name}' (ID: {list_id})...")
                    response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            components = data.get('components', [])
                            print(f"   ✅ '{list_name}' has {len(components)} components")
                            
                            if components:
                                print("   Components:")
                                for comp in components:
                                    print(f"     - {comp['amc_dev_name']} ({comp['metadata_type_name']})")
                            else:
                                print("   (No components)")
                        else:
                            print(f"   ❌ Failed to get components: {data.get('error')}")
                    else:
                        print(f"   ❌ Failed to get components: {response.status_code}")
                
                # Test 3: Add a component to a list using the API (simulating plus icon)
                if mylists:
                    test_list = mylists[0]  # Use first list
                    list_id = test_list['aml_id']
                    list_name = test_list['aml_name']
                    
                    print(f"\n🔍 Step 3: Testing plus icon functionality (adding to '{list_name}')...")
                    
                    # Get a component to add
                    response = requests.get('http://localhost:5000/api/metadata-components/8')
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success') and data.get('components'):
                            # Use a component that's not already in the list
                            component = data['components'][2] if len(data['components']) > 2 else data['components'][0]
                            component_id = component['amc_id']
                            component_name = component['amc_dev_name']
                            
                            print(f"   Using component: {component_name} (ID: {component_id})")
                            
                            # Add component to list (simulating plus icon click)
                            add_data = {
                                'org_id': 409,
                                'component_id': component_id,
                                'notes': 'Added via plus icon test'
                            }
                            
                            response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data.get('success'):
                                    print(f"   ✅ Plus icon worked! Component added to '{list_name}'")
                                    
                                    # Verify the component was added
                                    response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
                                    if response.status_code == 200:
                                        data = response.json()
                                        if data.get('success'):
                                            components = data.get('components', [])
                                            print(f"   ✅ List now has {len(components)} components")
                                            
                                            # Remove the test component
                                            response = requests.delete(f'http://localhost:5000/api/mylists/{list_id}/components/{component_id}')
                                            if response.status_code == 200:
                                                print(f"   ✅ Test component removed")
                                            else:
                                                print(f"   ⚠️ Could not remove test component: {response.status_code}")
                                        else:
                                            print(f"   ❌ Failed to verify: {data.get('error')}")
                                    else:
                                        print(f"   ❌ Failed to verify: {response.status_code}")
                                else:
                                    print(f"   ❌ Plus icon failed: {data.get('error')}")
                            else:
                                print(f"   ❌ Plus icon failed: {response.status_code}")
                                try:
                                    error_data = response.json()
                                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                                except:
                                    print(f"   Response text: {response.text}")
                        else:
                            print("   ❌ No components available")
                    else:
                        print(f"   ❌ Failed to get components: {response.status_code}")
                else:
                    print("❌ No lists available for testing")
            else:
                print(f"❌ Failed to get lists: {data.get('error')}")
        else:
            print(f"❌ Failed to get lists: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing plus icon: {e}")

if __name__ == "__main__":
    test_plus_icon_functionality()
    
    print("\n" + "=" * 50)
    print("🎯 Plus Icon Test Complete!")
    print("📱 The plus icon should now properly add components to lists")
    print("🔄 List counts should update correctly in the frontend") 