#!/usr/bin/env python3
"""
Test script to verify dependency analysis functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager
import re
import xml.etree.ElementTree as ET

def test_dependency_analysis():
    """Test dependency analysis functions"""
    db = get_db_manager()
    
    try:
        print("🔍 Testing Dependency Analysis Functions")
        print("=" * 50)
        
        # Get a sample Apex class component
        print("\n1. Testing Apex Class dependency analysis...")
        apex_components = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_metadata_type_id = 1 AND amc_status = 1 
            AND amc_content IS NOT NULL AND amc_content != ''
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
            
            # Test the dependency analysis
            content = component['amc_content']
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:200]}...")
            
            # Test SOQL pattern matching
            soql_pattern = r'(?i)SELECT\s+.+?\s+FROM\s+(\w+)'
            soql_matches = re.findall(soql_pattern, content)
            print(f"SOQL matches found: {soql_matches}")
            
            # Test DML pattern matching
            dml_pattern = r'(?i)(insert|update|delete|upsert|merge)\s+(\w+)'
            dml_matches = re.findall(dml_pattern, content)
            print(f"DML matches found: {dml_matches}")
            
            # Test class inheritance pattern
            class_pattern = r'(?i)public\s+class\s+(\w+)\s+extends\s+(\w+)'
            class_matches = re.findall(class_pattern, content)
            print(f"Class inheritance matches found: {class_matches}")
            
            # Test interface implementation pattern
            interface_pattern = r'(?i)public\s+class\s+(\w+)\s+implements\s+(\w+)'
            interface_matches = re.findall(interface_pattern, content)
            print(f"Interface implementation matches found: {interface_matches}")
            
        else:
            print("No Apex class components found with content")
        
        # Test Custom Object dependency analysis
        print("\n2. Testing Custom Object dependency analysis...")
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
                
                # Find all elements to understand the structure
                all_elements = root.findall('.//*')
                print(f"Found {len(all_elements)} total elements")
                
                # Show unique element names
                element_names = set()
                for elem in all_elements:
                    element_names.add(elem.tag)
                print(f"Unique element names: {sorted(list(element_names))}")
                
                # Find field relationships - try different patterns
                fields = root.findall('.//fields')
                print(f"Found {len(fields)} field elements using './/fields'")
                
                # Try alternative patterns
                fields_alt1 = root.findall('.//field')
                print(f"Found {len(fields_alt1)} field elements using './/field'")
                
                fields_alt2 = root.findall('.//*[contains(local-name(), "field")]')
                print(f"Found {len(fields_alt2)} field elements using wildcard")
                
                # Show first few elements with their structure
                print("\nFirst 10 elements with their structure:")
                for i, elem in enumerate(all_elements[:10]):
                    print(f"  {i+1}. {elem.tag}: {elem.text[:50] if elem.text else 'No text'}")
                    for child in elem:
                        print(f"     - {child.tag}: {child.text[:30] if child.text else 'No text'}")
                
            except ET.ParseError as e:
                print(f"Error parsing XML: {str(e)}")
        
        # Test Flow dependency analysis
        print("\n3. Testing Flow dependency analysis...")
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
                
                # Find all elements to understand the structure
                all_elements = root.findall('.//*')
                print(f"Found {len(all_elements)} total elements")
                
                # Show unique element names
                element_names = set()
                for elem in all_elements:
                    element_names.add(elem.tag)
                print(f"Unique element names: {sorted(list(element_names))}")
                
                # Find object references - try different patterns
                objects = root.findall('.//object')
                print(f"Found {len(objects)} object references using './/object'")
                
                objects_alt1 = root.findall('.//*[contains(local-name(), "object")]')
                print(f"Found {len(objects_alt1)} object references using wildcard")
                
                # Find Apex class references - try different patterns
                apex_classes = root.findall('.//apexClass')
                print(f"Found {len(apex_classes)} Apex class references using './/apexClass'")
                
                apex_classes_alt1 = root.findall('.//*[contains(local-name(), "apex")]')
                print(f"Found {len(apex_classes_alt1)} Apex references using wildcard")
                
                # Show first few elements with their structure
                print("\nFirst 10 elements with their structure:")
                for i, elem in enumerate(all_elements[:10]):
                    print(f"  {i+1}. {elem.tag}: {elem.text[:50] if elem.text else 'No text'}")
                    for child in elem:
                        print(f"     - {child.tag}: {child.text[:30] if child.text else 'No text'}")
                
            except ET.ParseError as e:
                print(f"Error parsing XML: {str(e)}")
        
        # Test Layout dependency analysis
        print("\n4. Testing Layout dependency analysis...")
        layout_components = db.execute_query("""
            SELECT * FROM ids_audit_metadata_component 
            WHERE amc_metadata_type_id = 5 AND amc_status = 1 
            AND amc_dev_name LIKE '%-%' 
            LIMIT 1
        """, fetch_all=True)
        
        if layout_components:
            component = layout_components[0]
            print(f"Testing component: {component['amc_dev_name']} (ID: {component['amc_id']})")
            
            # Extract object name from layout name
            layout_name = component['amc_dev_name']
            object_name = layout_name.split('-')[0] if '-' in layout_name else None
            print(f"Extracted object name: {object_name}")
        
        print("\n" + "=" * 50)
        print("✅ Dependency analysis test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during dependency analysis test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dependency_analysis() 