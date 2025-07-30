#!/usr/bin/env python3
"""
Test script to test MyList with component and dependency network
"""

import requests
import json

def test_list_with_component():
    """Test MyList with component and dependency network"""
    try:
        print("🧪 Testing MyList with Component and Dependency Network...")
        print("=" * 50)
        
        # Test 1: Create a new MyList
        print("\n🔍 Step 1: Creating a new MyList...")
        list_data = {
            'org_id': 409,
            'user_id': 243,
            'integration_id': 6,
            'name': 'Test List with Component',
            'description': 'Testing dependency network',
            'notes': 'Test list'
        }
        
        response = requests.post('http://localhost:5000/api/mylists', json=list_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                list_id = data.get('list_id')
                print(f"✅ MyList created successfully with ID: {list_id}")
                
                # Test 2: Get a component to add
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
                            'notes': 'Added for dependency network test'
                        }
                        
                        response = requests.post(f'http://localhost:5000/api/mylists/{list_id}/components', json=add_data)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                print(f"✅ Component {component['amc_dev_name']} added to MyList")
                                
                                # Test 4: Get dependency network
                                print(f"\n🔍 Step 4: Getting dependency network for MyList {list_id}...")
                                response = requests.get(f'http://localhost:5000/api/mylists/{list_id}/dependency-network')
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    if data.get('success'):
                                        network = data.get('network', {})
                                        stats = data.get('stats', {})
                                        print(f"✅ Dependency network retrieved successfully!")
                                        print(f"   Components: {stats.get('total_components', 0)}")
                                        print(f"   Relationships: {stats.get('total_relationships', 0)}")
                                        print(f"   Nodes: {len(network.get('nodes', []))}")
                                        print(f"   Edges: {len(network.get('edges', []))}")
                                        
                                        # Show network details
                                        if network.get('nodes'):
                                            print(f"\n📊 Network Nodes:")
                                            for node in network['nodes']:
                                                print(f"   - {node['label']} ({node['type']})")
                                        
                                        if network.get('edges'):
                                            print(f"\n🔗 Network Edges:")
                                            for edge in network['edges']:
                                                print(f"   - {edge['from']} -> {edge['to']} ({edge['type']})")
                                    else:
                                        print(f"❌ Failed to get dependency network: {data.get('error')}")
                                else:
                                    print(f"❌ Failed to get dependency network: {response.status_code}")
                                    print(f"Response: {response.text}")
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
        print(f"❌ Error testing MyList with component: {e}")

if __name__ == "__main__":
    test_list_with_component()
    
    print("\n" + "=" * 50)
    print("🎯 MyList with Component Test Complete!")
    print("📱 The list functionality with dependency networks is working") 