#!/usr/bin/env python3
"""
Test script to verify dependency network data structure for frontend display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager
import requests
import json

def test_frontend_dependency_display():
    """Test dependency network data structure for frontend"""
    db = get_db_manager()
    
    try:
        print("🔍 Testing Frontend Dependency Display")
        print("=" * 50)
        
        # Get a component that has dependencies
        print("\n1. Finding components with dependencies...")
        components_with_deps = db.execute_query("""
            SELECT DISTINCT amc_id, amc_dev_name, amc_metadata_type_id 
            FROM ids_audit_metadata_component amc
            INNER JOIN ids_audit_metadata_dependency amd 
            ON amc.amc_id = amd.amd_from_component_id OR amc.amc_id = amd.amd_to_component_id
            WHERE amc.amc_status = 1
            LIMIT 5
        """, fetch_all=True)
        
        if not components_with_deps:
            print("❌ No components with dependencies found")
            return
        
        print(f"✅ Found {len(components_with_deps)} components with dependencies")
        
        # Test the dependency network endpoint for each component
        for i, component in enumerate(components_with_deps):
            print(f"\n2. Testing component {i+1}: {component['amc_dev_name']} (ID: {component['amc_id']})")
            
            # Test the API endpoint
            try:
                response = requests.get(f"http://localhost:5000/api/metadata-component/{component['amc_id']}/dependency-network")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        print(f"✅ API call successful")
                        
                        # Check data structure
                        network = data.get('network', {})
                        nodes = network.get('nodes', [])
                        edges = network.get('edges', [])
                        stats = data.get('stats', {})
                        
                        print(f"   📊 Network data:")
                        print(f"      - Nodes: {len(nodes)}")
                        print(f"      - Edges: {len(edges)}")
                        print(f"      - Stats: {stats}")
                        
                        # Check if data structure matches frontend expectations
                        if nodes and edges:
                            print(f"   ✅ Data structure is valid for frontend display")
                            
                            # Show sample node and edge
                            if nodes:
                                sample_node = nodes[0]
                                print(f"   📋 Sample node: {sample_node}")
                            
                            if edges:
                                sample_edge = edges[0]
                                print(f"   🔗 Sample edge: {sample_edge}")
                        else:
                            print(f"   ⚠️  No network data found")
                        
                        # Check relationships data
                        relationships = data.get('relationships', [])
                        print(f"   📈 Raw relationships: {len(relationships)}")
                        
                    else:
                        print(f"❌ API call failed: {data.get('error', 'Unknown error')}")
                        
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing API: {str(e)}")
        
        # Test with a component that has no dependencies
        print(f"\n3. Testing component with no dependencies...")
        components_no_deps = db.execute_query("""
            SELECT amc_id, amc_dev_name 
            FROM ids_audit_metadata_component 
            WHERE amc_status = 1 
            AND amc_id NOT IN (
                SELECT DISTINCT amd_from_component_id FROM ids_audit_metadata_dependency
                UNION
                SELECT DISTINCT amd_to_component_id FROM ids_audit_metadata_dependency
            )
            LIMIT 1
        """, fetch_one=True)
        
        if components_no_deps:
            print(f"Testing component: {components_no_deps['amc_dev_name']} (ID: {components_no_deps['amc_id']})")
            
            try:
                response = requests.get(f"http://localhost:5000/api/metadata-component/{components_no_deps['amc_id']}/dependency-network")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        network = data.get('network', {})
                        nodes = network.get('nodes', [])
                        edges = network.get('edges', [])
                        
                        print(f"   📊 Empty network data:")
                        print(f"      - Nodes: {len(nodes)}")
                        print(f"      - Edges: {len(edges)}")
                        
                        if not nodes and not edges:
                            print(f"   ✅ Correctly shows no dependencies")
                        else:
                            print(f"   ⚠️  Unexpected data for component with no dependencies")
                    else:
                        print(f"❌ API call failed: {data.get('error', 'Unknown error')}")
                        
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing API: {str(e)}")
        
        print(f"\n✅ Frontend dependency display test completed")
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")

if __name__ == "__main__":
    test_frontend_dependency_display() 