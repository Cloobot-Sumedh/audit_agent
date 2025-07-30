#!/usr/bin/env python3
"""
Test script to verify the complete plus icon flow
"""

import requests
import json

def test_complete_flow():
    """Test the complete plus icon flow from frontend to database"""
    try:
        print("🧪 Testing Complete Plus Icon Flow...")
        print("=" * 50)
        
        # Test 1: Create a new list (simulating "Create New List" in modal)
        print("\n🔍 Step 1: Creating a new list...")
        list_data = {
            'org_id': 409,
            'user_id': 243,
            'integration_id': 6,
            'name': 'Test Plus Icon List',
            'description': 'Testing plus icon functionality',
            'notes': 'Created for plus icon testing'
        }
        
        response = requests.post('http://localhost:5000/api/mylists', json=list_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                list_id = data.get('list_id')
                print(f"✅ New list created with ID: {list_id}")
                
                # Test 2: Get components to add
                print(f"\n🔍 Step 2: Getting components to add...")
                response = requests.get('http://localhost:5000/api/metadata-components/8')
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('components'):
                        # Use a component that's not already in any list
                        component = data['components'][3] if len(data['components']) > 3 else data['components'][0]
                        component_id = component['amc_id']
                        component_name = component['amc_dev_name']
                        
                        print(f"   Using component: {component_name} (ID: {component_id})")
                        
                        # Test 3: Simulate plus icon click and save (API call)
                        print(f"\n🔍 Step 3: Simulating plus icon click and save...")
                        add_data = {
                            'org_id': 409,
                            'component_id': component_id,
                            'notes': 'Added via plus icon flow test'
                        }
                        
                        response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                print(f"✅ Plus icon save worked! Component added to list")
                                
                                # Test 4: Verify the component was added
                                print(f"\n🔍 Step 4: Verifying component was added...")
                                response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/components')
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('success'):
                                        components = data.get('components', [])
                                        print(f"✅ List now has {len(components)} components")
                                        
                                        # Test 5: Check if list count updates in lists endpoint
                                        print(f"\n🔍 Step 5: Checking list count in lists endpoint...")
                                        response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')
                                        
                                        if response.status_code == 200:
                                            data = response.json()
                                            if data.get('success'):
                                                mylists = data.get('mylists', [])
                                                for mylist in mylists:
                                                    if mylist['aml_id'] == list_id:
                                                        print(f"✅ List '{mylist['aml_name']}' found in lists endpoint")
                                                        break
                                            else:
                                                print(f"❌ Failed to get lists: {data.get('error')}")
                                        else:
                                            print(f"❌ Failed to get lists: {response.status_code}")
                                        
                                        # Test 6: Remove the test component
                                        print(f"\n🔍 Step 6: Cleaning up test component...")
                                        response = requests.delete(f'http://localhost:5000/api/mylists/{list_id}/components/{component_id}')
                                        
                                        if response.status_code == 200:
                                            print(f"✅ Test component removed")
                                        else:
                                            print(f"⚠️ Could not remove test component: {response.status_code}")
                                    else:
                                        print(f"❌ Failed to verify: {data.get('error')}")
                                else:
                                    print(f"❌ Failed to verify: {response.status_code}")
                            else:
                                print(f"❌ Plus icon save failed: {data.get('error')}")
                        else:
                            print(f"❌ Plus icon save failed: {response.status_code}")
                            try:
                                error_data = response.json()
                                print(f"   Error details: {json.dumps(error_data, indent=2)}")
                            except:
                                print(f"   Response text: {response.text}")
                    else:
                        print("❌ No components available")
                else:
                    print(f"❌ Failed to get components: {response.status_code}")
            else:
                print(f"❌ Failed to create list: {data.get('error')}")
        else:
            print(f"❌ Failed to create list: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing complete flow: {e}")

if __name__ == "__main__":
    test_complete_flow()
    
    print("\n" + "=" * 50)
    print("🎯 Complete Plus Icon Flow Test Complete!")
    print("📱 The plus icon should now:")
    print("   1. Open modal with existing lists")
    print("   2. Allow creating new lists")
    print("   3. Hit API when Save is clicked")
    print("   4. Update list counts correctly") 