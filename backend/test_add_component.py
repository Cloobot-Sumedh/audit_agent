#!/usr/bin/env python3
"""
Test script to debug add component to list functionality
"""

import requests
import json

def test_add_component():
    print("🧪 Testing component addition...")
    
    try:
        # 1. Get available components
        print("1. Getting available components...")
        components_response = requests.get('http://localhost:5000/api/metadata-components/1')
        if components_response.status_code != 200:
            print(f"❌ Failed to get components: {components_response.status_code}")
            return False
            
        components_data = components_response.json()
        components = components_data.get('components', [])
        
        if not components:
            print("❌ No components found")
            return False
            
        print(f"✅ Found {len(components)} components")
        
        # 2. Try to add the first component to list 9
        component = components[0]
        component_id = component.get('amc_id')
        print(f"2. Adding component {component_id} to list 9...")
        
        add_data = {
            "org_id": 1,
            "component_id": component_id,
            "notes": "Test component addition"
        }
        
        add_response = requests.post('http://localhost:5000/api/mylists/9/components', json=add_data)
        print(f"Response status: {add_response.status_code}")
        print(f"Response content: {add_response.text}")
        
        if add_response.status_code == 200:
            result = add_response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Failed to add component")
            
        # 3. Check the list again
        print("3. Checking list components...")
        list_response = requests.get('http://localhost:5000/api/mylists/9/components')
        if list_response.status_code == 200:
            list_data = list_response.json()
            components = list_data.get('components', [])
            print(f"✅ List now has {len(components)} components")
            
            if components:
                first_component = components[0]
                print(f"  Component details:")
                print(f"    ID: {first_component.get('amc_id')}")
                print(f"    Name: {first_component.get('amc_dev_name', 'Unknown')}")
                print(f"    Type: {first_component.get('metadata_type_name', 'Unknown')}")
                print(f"    Created: {first_component.get('amc_created_timestamp', 'Unknown')}")
                print(f"    Notes: {first_component.get('amc_notes', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_add_component() 