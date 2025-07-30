#!/usr/bin/env python3
"""
Debug script to test dependency network functionality
"""

import requests
import json

def debug_dependency_network():
    """Debug the dependency network endpoint"""
    try:
        print("🔍 Debugging Dependency Network...")
        print("=" * 50)
        
        # Test 1: Get a MyList
        print("\n🔍 Step 1: Getting MyList 1...")
        response = requests.get('http://localhost:5000/api/mylists/1')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                mylist = data.get('mylist')
                print(f"✅ Retrieved MyList: {mylist.get('aml_name')}")
                
                # Test 2: Get components in the MyList
                print("\n🔍 Step 2: Getting components in MyList 1...")
                response = requests.get('http://localhost:5000/api/mylists/1/components')
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        components = data.get('components', [])
                        print(f"✅ Found {len(components)} components in MyList")
                        for comp in components:
                            print(f"   - {comp['amc_dev_name']} (ID: {comp['almm_component_id']})")
                        
                        # Test 3: Get dependency network
                        print("\n🔍 Step 3: Getting dependency network...")
                        response = requests.get('http://localhost:5000/api/mylists/1/dependency-network')
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                network = data.get('network', {})
                                stats = data.get('stats', {})
                                print(f"✅ Dependency network retrieved")
                                print(f"   Components: {stats.get('total_components', 0)}")
                                print(f"   Relationships: {stats.get('total_relationships', 0)}")
                                print(f"   Nodes: {len(network.get('nodes', []))}")
                                print(f"   Edges: {len(network.get('edges', []))}")
                            else:
                                print(f"❌ Failed to get dependency network: {data.get('error')}")
                        else:
                            print(f"❌ Failed to get dependency network: {response.status_code}")
                            print(f"Response: {response.text}")
                    else:
                        print(f"❌ Failed to get components: {data.get('error')}")
                else:
                    print(f"❌ Failed to get components: {response.status_code}")
            else:
                print(f"❌ Failed to get MyList: {data.get('error')}")
        else:
            print(f"❌ Failed to get MyList: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error debugging dependency network: {e}")

if __name__ == "__main__":
    debug_dependency_network() 