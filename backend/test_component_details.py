#!/usr/bin/env python3
"""
Test script to verify component detail endpoints
"""

import requests
import json

def test_component_details():
    """Test the component detail endpoints"""
    try:
        # First, get a component ID from the metadata components
        response = requests.get('http://localhost:5000/api/metadata-components/4')
        
        if response.status_code != 200:
            print("❌ Could not get metadata components")
            return
            
        data = response.json()
        if not data.get('success') or not data.get('components'):
            print("❌ No components found")
            return
            
        # Get the first component
        component = data['components'][0]
        component_id = component['amc_id']
        print(f"✅ Using component ID: {component_id}")
        print(f"   Component: {component.get('amc_dev_name', 'Unknown')}")
        print(f"   Type: {component.get('metadata_type_name', 'Unknown')}")
        
        # Test 1: Get component details
        print("\n🔍 Testing: Get component details")
        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Component details retrieved")
            print(f"   AI Summary: {len(data.get('ai_summary', ''))} characters")
            print(f"   Dependencies: {len(data.get('dependencies', []))} found")
            print(f"   Content: {len(data.get('content', ''))} characters")
        else:
            print(f"❌ Failed to get component details: {response.status_code}")
        
        # Test 2: Get component dependencies
        print("\n🔍 Testing: Get component dependencies")
        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/dependencies')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dependencies retrieved: {data.get('count', 0)} found")
            if data.get('dependencies'):
                for dep in data['dependencies'][:3]:  # Show first 3
                    print(f"   - {dep.get('from_dev_name', 'Unknown')} -> {dep.get('to_dev_name', 'Unknown')} ({dep.get('amd_dependency_type', 'Unknown')})")
        else:
            print(f"❌ Failed to get dependencies: {response.status_code}")
        
        # Test 3: Get component content
        print("\n🔍 Testing: Get component content")
        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/content')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content retrieved")
            print(f"   Component: {data.get('component_name', 'Unknown')}")
            print(f"   Type: {data.get('metadata_type', 'Unknown')}")
            print(f"   Content length: {len(data.get('content', ''))} characters")
        else:
            print(f"❌ Failed to get content: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing component details: {e}")

if __name__ == "__main__":
    print("🧪 Testing Component Detail Endpoints...")
    print("=" * 50)
    
    test_component_details()
    
    print("\n" + "=" * 50)
    print("🎯 Component details should now be available when clicking on metadata!")
    print("📱 Try clicking on a metadata component in the explorer") 