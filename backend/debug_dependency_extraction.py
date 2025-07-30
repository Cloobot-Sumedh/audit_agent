#!/usr/bin/env python3
"""
Debug script to test dependency analysis functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager
import re
import xml.etree.ElementTree as ET

def debug_dependency_analysis():
    """Debug dependency analysis functions"""
    db = get_db_manager()
    
    try:
        print("🔍 Debugging Dependency Analysis Functions")
        print("=" * 60)
        
        # Get a sample Apex class with actual content
        print("\n1. Testing Apex Class dependency analysis...")
        apex_components = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_metadata_type_id = 1 AND amc_status = 1 
            AND amc_content IS NOT NULL AND amc_content != ''
            AND amc_content != 'public class TestClass { }'
            LIMIT 1
        """, fetch_all=True)
        
        if apex_components:
            component = apex_components[0]
            print(f"Testing component: {component['amc_dev_name']} (ID: {component['amc_id']})")
            
            # Get all components for mapping
            all_components = db.execute_query("""
                SELECT amc_id, amc_dev_name FROM ids_audit_metadata_component 
                WHERE amc_status = 1
            """, fetch_all=True)
            
            component_map = {comp['amc_dev_name']: comp['amc_id'] for comp in all_components}
            print(f"Component map size: {len(component_map)}")
            
            # Check for duplicate component names
            component_names = [comp['amc_dev_name'] for comp in all_components]
            duplicate_names = [name for name in set(component_names) if component_names.count(name) > 1]
            if duplicate_names:
                print(f"⚠️  Found duplicate component names: {duplicate_names}")
                for name in duplicate_names:
                    duplicates = [comp for comp in all_components if comp['amc_dev_name'] == name]
                    print(f"  '{name}' appears {len(duplicates)} times with IDs: {[comp['amc_id'] for comp in duplicates]}")
            
            # Show some sample components in the map
            print("Sample components in map:")
            for i, (name, comp_id) in enumerate(list(component_map.items())[:10]):
                print(f"  {name} -> {comp_id}")
            
            # Test the dependency analysis
            content = component['amc_content']
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:500]}...")
            
            # Test SOQL pattern matching
            soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
            soql_matches = re.findall(soql_pattern, content)
            print(f"SOQL matches found: {soql_matches}")
            
            # Check if any of the SOQL matches exist in component map
            for obj_name in soql_matches:
                if obj_name in component_map:
                    print(f"✅ Found '{obj_name}' in component map (ID: {component_map[obj_name]})")
                else:
                    print(f"❌ '{obj_name}' NOT found in component map")
                    # Check if it needs __c suffix
                    if '_' in obj_name and not obj_name.endswith('__c'):
                        obj_name_with_suffix = f"{obj_name}__c"
                        if obj_name_with_suffix in component_map:
                            print(f"✅ Found '{obj_name_with_suffix}' in component map (ID: {component_map[obj_name_with_suffix]})")
                        else:
                            print(f"❌ '{obj_name_with_suffix}' also NOT found in component map")
            
            # Test DML pattern matching
            dml_pattern = r'(?i)(insert|update|delete|upsert|merge)\s+(\w+)'
            dml_matches = re.findall(dml_pattern, content)
            print(f"DML matches found: {dml_matches}")
            
            # Check if any of the DML matches exist in component map
            for operation, var_name in dml_matches:
                if var_name.lower() not in ['list', 'set', 'map', 'string', 'integer', 'boolean']:
                    if var_name in component_map:
                        print(f"✅ Found '{var_name}' in component map (ID: {component_map[var_name]})")
                    else:
                        print(f"❌ '{var_name}' NOT found in component map")
            
            # Test class inheritance pattern
            class_pattern = r'(?i)public\s+class\s+(\w+)\s+extends\s+(\w+)'
            class_matches = re.findall(class_pattern, content)
            print(f"Class inheritance matches found: {class_matches}")
            
            # Test interface implementation pattern
            interface_pattern = r'(?i)public\s+class\s+(\w+)\s+implements\s+(\w+)'
            interface_matches = re.findall(interface_pattern, content)
            print(f"Interface implementation matches found: {interface_matches}")
            
            # Test the actual dependency analysis function
            print("\n2. Testing actual dependency analysis function...")
            
            # Import the function
            import server_db
            dependencies = server_db.analyze_apex_class_dependencies_in_memory(
                component['amc_dev_name'] + '.cls', 
                component_map
            )
            print(f"Dependencies found: {len(dependencies)}")
            for dep in dependencies:
                print(f"  - {dep}")
            
        else:
            print("No Apex class components found with meaningful content")
        
        # Find Apex classes that reference custom objects
        print("\n3. Searching for Apex classes that reference custom objects...")
        apex_components_with_refs = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_metadata_type_id = 1 AND amc_status = 1 
            AND amc_content IS NOT NULL AND amc_content != ''
            AND (amc_content LIKE '%Feedback__c%' OR amc_content LIKE '%Product_Configuraion__mdt%')
            LIMIT 3
        """, fetch_all=True)
        
        if apex_components_with_refs:
            print(f"Found {len(apex_components_with_refs)} Apex classes with custom object references:")
            for comp in apex_components_with_refs:
                print(f"  - {comp['amc_dev_name']} (ID: {comp['amc_id']})")
                content = comp['amc_content']
                
                # Check for Feedback__c references
                if 'Feedback__c' in content:
                    print(f"    ✅ Contains Feedback__c references")
                    soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+Feedback__c'
                    if re.search(soql_pattern, content):
                        print(f"    ✅ Contains SOQL query on Feedback__c")
                
                # Check for Product_Configuraion__mdt references
                if 'Product_Configuraion__mdt' in content:
                    print(f"    ✅ Contains Product_Configuraion__mdt references")
                    soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+Product_Configuraion__mdt'
                    if re.search(soql_pattern, content):
                        print(f"    ✅ Contains SOQL query on Product_Configuraion__mdt")
            
            # Test dependency analysis with a class that has custom object references
            print("\n4. Testing dependency analysis with ProductConfigController...")
            test_component = apex_components_with_refs[0]
            print(f"Testing component: {test_component['amc_dev_name']} (ID: {test_component['amc_id']})")
            
            content = test_component['amc_content']
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:500]}...")
            
            # Test SOQL pattern matching
            soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
            soql_matches = re.findall(soql_pattern, content)
            print(f"SOQL matches found: {soql_matches}")
            
            # Check if any of the SOQL matches exist in component map
            for obj_name in soql_matches:
                if obj_name in component_map:
                    print(f"✅ Found '{obj_name}' in component map (ID: {component_map[obj_name]})")
                else:
                    print(f"❌ '{obj_name}' NOT found in component map")
                    # Check if it needs __c suffix
                    if '_' in obj_name and not obj_name.endswith('__c'):
                        obj_name_with_suffix = f"{obj_name}__c"
                        if obj_name_with_suffix in component_map:
                            print(f"✅ Found '{obj_name_with_suffix}' in component map (ID: {component_map[obj_name_with_suffix]})")
                        else:
                            print(f"❌ '{obj_name_with_suffix}' also NOT found in component map")
            
            # Test the actual dependency analysis function
            print("\n5. Testing actual dependency analysis function with ProductConfigController...")
            
            # Debug the component lookup
            print(f"Component name: {test_component['amc_dev_name']}")
            print(f"Component ID: {test_component['amc_id']}")
            print(f"Looking for component in map: {test_component['amc_dev_name']}")
            print(f"Component in map: {test_component['amc_dev_name'] in component_map}")
            if test_component['amc_dev_name'] in component_map:
                print(f"Component ID from map: {component_map[test_component['amc_dev_name']]}")
            
            dependencies = server_db.analyze_apex_class_dependencies_in_memory(
                test_component['amc_dev_name'] + '.cls', 
                component_map
            )
            print(f"Dependencies found: {len(dependencies)}")
            for dep in dependencies:
                print(f"  - {dep}")
            
            # Debug the database lookup
            print("\n7. Debugging database lookup...")
            component_from_db = db.get_metadata_component(test_component['amc_id'])
            if component_from_db:
                print(f"✅ Component found in database: {component_from_db['amc_dev_name']}")
                print(f"Content length: {len(component_from_db.get('amc_content', ''))}")
            else:
                print(f"❌ Component NOT found in database")
            
            # Test the SOQL pattern directly
            print("\n8. Testing SOQL pattern directly...")
            soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
            for match in re.finditer(soql_pattern, content):
                obj_name = match.group(1)
                print(f"Found SOQL query on: {obj_name}")
                if obj_name in component_map:
                    print(f"✅ {obj_name} found in component map (ID: {component_map[obj_name]})")
                    print(f"Source component ID: {test_component['amc_id']}")
                    if component_map[obj_name] != test_component['amc_id']:
                        print(f"✅ Would create dependency: {test_component['amc_id']} -> {component_map[obj_name]}")
                    else:
                        print(f"❌ Same component, no dependency created")
                else:
                    print(f"❌ {obj_name} NOT found in component map")
        else:
            print("No Apex classes found with custom object references")
        
        # Test Custom Object dependency analysis
        print("\n6. Testing Custom Object dependency analysis...")
        object_components = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_metadata_type_id = 3 AND amc_status = 1 
            AND amc_content IS NOT NULL AND amc_content != ''
            LIMIT 1
        """, fetch_all=True)
        
        if object_components:
            component = object_components[0]
            print(f"Testing component: {component['amc_dev_name']} (ID: {component['amc_id']})")
            
            content = component['amc_content']
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:500]}...")
            
            try:
                root = ET.fromstring(content)
                
                # Define namespace for Salesforce metadata
                ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
                
                # Find field relationships using namespace
                fields = root.findall('.//sf:fields', ns)
                print(f"Found {len(fields)} field elements using namespace")
                
                for field in fields[:5]:  # Show first 5 fields
                    field_name_elem = field.find('sf:fullName', ns)
                    ref_to_elem = field.find('sf:referenceTo', ns)
                    type_elem = field.find('sf:type', ns)
                    
                    if field_name_elem is not None:
                        field_name = field_name_elem.text
                        ref_to = ref_to_elem.text if ref_to_elem is not None else None
                        field_type = type_elem.text if type_elem is not None else None
                        
                        print(f"  Field: {field_name}, Type: {field_type}, References: {ref_to}")
                
                # Test the actual dependency analysis function
                print("\n7. Testing actual Custom Object dependency analysis function...")
                
                dependencies = server_db.analyze_custom_object_dependencies_in_memory(
                    component['amc_dev_name'] + '.object', 
                    component_map
                )
                print(f"Dependencies found: {len(dependencies)}")
                for dep in dependencies:
                    print(f"  - {dep}")
                
            except ET.ParseError as e:
                print(f"Error parsing XML: {str(e)}")
        
        # Test Flow dependency analysis
        print("\n8. Testing Flow dependency analysis...")
        flow_components = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_metadata_type_id = 4 AND amc_status = 1 
            AND amc_content IS NOT NULL AND amc_content != ''
            LIMIT 1
        """, fetch_all=True)
        
        if flow_components:
            component = flow_components[0]
            print(f"Testing component: {component['amc_dev_name']} (ID: {component['amc_id']})")
            
            content = component['amc_content']
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:500]}...")
            
            try:
                root = ET.fromstring(content)
                
                # Define namespace for Salesforce metadata
                ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
                
                # Find object references
                objects = root.findall('.//sf:object', ns)
                print(f"Found {len(objects)} object references")
                
                for obj in objects[:5]:  # Show first 5 objects
                    if obj.text:
                        print(f"  Object: {obj.text}")
                
                # Find Apex class references
                apex_classes = root.findall('.//sf:apexClass', ns)
                print(f"Found {len(apex_classes)} Apex class references")
                
                for apex in apex_classes[:5]:  # Show first 5 Apex classes
                    if apex.text:
                        print(f"  Apex Class: {apex.text}")
                
                # Test the actual dependency analysis function
                print("\n9. Testing actual Flow dependency analysis function...")
                
                dependencies = server_db.analyze_flow_dependencies_in_memory(
                    component['amc_dev_name'] + '.flow', 
                    component_map
                )
                print(f"Dependencies found: {len(dependencies)}")
                for dep in dependencies:
                    print(f"  - {dep}")
                
            except ET.ParseError as e:
                print(f"Error parsing XML: {str(e)}")
        
        print("\n" + "=" * 60)
        print("✅ Dependency analysis debug completed!")
        
    except Exception as e:
        print(f"❌ Error during dependency analysis debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dependency_analysis() 