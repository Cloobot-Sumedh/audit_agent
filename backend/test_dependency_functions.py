#!/usr/bin/env python3
"""
Test script to verify dependency analysis functions with actual extraction data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager
import server_db
import re

def test_dependency_functions():
    """Test dependency analysis functions with actual data"""
    db = get_db_manager()
    
    try:
        print("🔍 Testing Dependency Analysis Functions with Actual Data")
        print("=" * 60)
        
        # Get the latest extraction job
        latest_job = db.execute_query("""
            SELECT * FROM ids_audit_extraction_job 
            WHERE aej_status = 1 
            ORDER BY aej_created_timestamp DESC 
            LIMIT 1
        """, fetch_one=True)
        
        if not latest_job:
            print("❌ No extraction jobs found")
            return
        
        job_id = latest_job['aej_id']
        print(f"Testing with latest job: {job_id}")
        
        # Get components from this job
        components = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_extraction_job_id = %s AND amc_status = 1
        """, (job_id,), fetch_all=True)
        
        print(f"Found {len(components)} components in job {job_id}")
        
        # Create component map
        component_map = {comp['amc_dev_name']: comp['amc_id'] for comp in components}
        print(f"Component map size: {len(component_map)}")
        
        # Test Apex class dependency analysis
        apex_components = [comp for comp in components if comp['amc_metadata_type_id'] == 1]
        print(f"Found {len(apex_components)} Apex classes")
        
        if apex_components:
            test_component = apex_components[0]
            print(f"\nTesting Apex class: {test_component['amc_dev_name']} (ID: {test_component['amc_id']})")
            
            # Check the content
            content = test_component.get('amc_content', '')
            print(f"Content length: {len(content)}")
            print(f"Content preview: {content[:200]}...")
            
            # Check for SOQL queries in content
            soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
            soql_matches = re.findall(soql_pattern, content)
            print(f"SOQL matches found: {soql_matches}")
            
            # Check if any of these objects are in the component map
            for obj_name in soql_matches:
                if obj_name in component_map:
                    print(f"✅ {obj_name} found in component map (ID: {component_map[obj_name]})")
                else:
                    print(f"❌ {obj_name} NOT found in component map")
            
            # Test the dependency analysis function
            dependencies = server_db.analyze_apex_class_dependencies_in_memory(
                test_component['amc_dev_name'] + '.cls',
                component_map
            )
            
            print(f"Dependencies found: {len(dependencies)}")
            for dep in dependencies:
                print(f"  - {dep}")
            
            # Test with a different Apex class that might have dependencies
            if len(apex_components) > 1:
                test_component2 = apex_components[1]
                print(f"\nTesting second Apex class: {test_component2['amc_dev_name']} (ID: {test_component2['amc_id']})")
                
                content2 = test_component2.get('amc_content', '')
                print(f"Content length: {len(content2)}")
                print(f"Content preview: {content2[:200]}...")
                
                # Check for SOQL queries in content
                soql_matches2 = re.findall(soql_pattern, content2)
                print(f"SOQL matches found: {soql_matches2}")
                
                # Check if any of these objects are in the component map
                for obj_name in soql_matches2:
                    if obj_name in component_map:
                        print(f"✅ {obj_name} found in component map (ID: {component_map[obj_name]})")
                    else:
                        print(f"❌ {obj_name} NOT found in component map")
                
                # Test the dependency analysis function
                dependencies2 = server_db.analyze_apex_class_dependencies_in_memory(
                    test_component2['amc_dev_name'] + '.cls',
                    component_map
                )
                
                print(f"Dependencies found: {len(dependencies2)}")
                for dep in dependencies2:
                    print(f"  - {dep}")
        
        # Test Flow dependency analysis
        flow_components = [comp for comp in components if comp['amc_metadata_type_id'] == 4]
        print(f"\nFound {len(flow_components)} Flows")
        
        if flow_components:
            test_flow = flow_components[0]
            print(f"Testing Flow: {test_flow['amc_dev_name']} (ID: {test_flow['amc_id']})")
            
            # Test the dependency analysis function
            dependencies = server_db.analyze_flow_dependencies_in_memory(
                test_flow['amc_dev_name'] + '.flow',
                component_map
            )
            
            print(f"Dependencies found: {len(dependencies)}")
            for dep in dependencies:
                print(f"  - {dep}")
        
        # Test Custom Object dependency analysis
        object_components = [comp for comp in components if comp['amc_metadata_type_id'] == 2]
        print(f"\nFound {len(object_components)} Custom Objects")
        
        if object_components:
            test_object = object_components[0]
            print(f"Testing Custom Object: {test_object['amc_dev_name']} (ID: {test_object['amc_id']})")
            
            # Test the dependency analysis function
            dependencies = server_db.analyze_custom_object_dependencies_in_memory(
                test_object['amc_dev_name'] + '.object',
                component_map
            )
            
            print(f"Dependencies found: {len(dependencies)}")
            for dep in dependencies:
                print(f"  - {dep}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dependency_functions() 