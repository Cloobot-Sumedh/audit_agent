#!/usr/bin/env python3
"""
Test script to verify the complete dependency flow
"""

import requests
import json

def test_dependency_flow():
    """Test the complete dependency flow from frontend to database"""
    try:
        print("🧪 Testing Complete Dependency Flow...")
        print("=" * 50)
        
        # Test 1: Get a component to test dependencies
        print("\n🔍 Step 1: Getting a component to test...")
        response = requests.get('http://localhost:5000/api/metadata-components/8')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('components'):
                component = data['components'][0]  # Use first component
                component_id = component['amc_id']
                component_name = component['amc_dev_name']
                
                print(f"   Using component: {component_name} (ID: {component_id})")
                
                # Test 2: Get dependency network for the component
                print(f"\n🔍 Step 2: Getting dependency network...")
                response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/dependency-network')
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        network = data.get('network', {})
                        nodes = network.get('nodes', [])
                        edges = network.get('edges', [])
                        
                        print(f"✅ Dependency network retrieved successfully!")
                        print(f"   Nodes: {len(nodes)}")
                        print(f"   Edges: {len(edges)}")
                        
                        if nodes:
                            node_names = [node.get('id', 'Unknown') for node in nodes[:3]]
                            print(f"   Sample nodes: {node_names}")
                        
                        if edges:
                            edge_names = []
                            for edge in edges[:3]:
                                from_node = edge.get('from', 'Unknown')
                                to_node = edge.get('to', 'Unknown')
                                edge_names.append(f"{from_node} -> {to_node}")
                            print(f"   Sample edges: {edge_names}")
                        
                        # Test 3: Get component details
                        print(f"\n🔍 Step 3: Getting component details...")
                        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                print(f"✅ Component details retrieved successfully!")
                                component_data = data.get('component', {})
                                print(f"   Name: {component_data.get('amc_dev_name', 'Unknown')}")
                                print(f"   Type: {component_data.get('metadata_type_name', 'Unknown')}")
                                print(f"   Content length: {len(component_data.get('amc_content', ''))}")
                            else:
                                print(f"❌ Failed to get component details: {data.get('error')}")
                        else:
                            print(f"❌ Failed to get component details: {response.status_code}")
                        
                        # Test 4: Generate AI summary
                        print(f"\n🔍 Step 4: Generating AI summary...")
                        response = requests.post(f'http://localhost:5000/api/metadata-component/{component_id}/generate-summary')
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                summary = data.get('summary', '')
                                print(f"✅ AI summary generated successfully!")
                                print(f"   Summary length: {len(summary)} characters")
                                print(f"   Preview: {summary[:100]}...")
                            else:
                                print(f"❌ Failed to generate summary: {data.get('error')}")
                        else:
                            print(f"❌ Failed to generate summary: {response.status_code}")
                        
                        # Test 5: Get component content
                        print(f"\n🔍 Step 5: Getting component content...")
                        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/content')
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('success'):
                                content = data.get('content', '')
                                print(f"✅ Component content retrieved successfully!")
                                print(f"   Content length: {len(content)} characters")
                                print(f"   Preview: {content[:100]}...")
                            else:
                                print(f"❌ Failed to get content: {data.get('error')}")
                        else:
                            print(f"❌ Failed to get content: {response.status_code}")
                        
                    else:
                        print(f"❌ Failed to get dependency network: {data.get('error')}")
                else:
                    print(f"❌ Failed to get dependency network: {response.status_code}")
            else:
                print("❌ No components available")
        else:
            print(f"❌ Failed to get components: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing dependency flow: {e}")

if __name__ == "__main__":
    test_dependency_flow()
    
    print("\n" + "=" * 50)
    print("🎯 Complete Dependency Flow Test Complete!")
    print("📱 The dependency functionality should now:")
    print("   1. Show dependency network when clicking 'Open Diagram'")
    print("   2. Allow clicking on nodes to see their details")
    print("   3. Generate AI summaries on demand")
    print("   4. Display component content and relationships") 