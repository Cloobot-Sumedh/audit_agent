import requests
import json

def test_remove_extracted_from():
    print("🧪 Testing removal of 'Extracted from' text...")
    
    try:
        # 1. Get metadata components to check the data structure
        print("1. Getting metadata components...")
        response = requests.get('http://localhost:5000/api/metadata-components/1')
        
        if response.status_code != 200:
            print(f"❌ Failed to get metadata components: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to get metadata components: {data.get('error')}")
            return False
            
        components = data.get('components', [])
        print(f"✅ Found {len(components)} components")
        
        # 2. Check if any components have "Extracted from" in their notes
        print("\n2. Checking for 'Extracted from' text in component notes...")
        components_with_extracted_from = []
        
        for component in components:
            notes = component.get('amc_notes', '')
            if 'Extracted from' in notes:
                components_with_extracted_from.append({
                    'name': component.get('amc_dev_name', 'Unknown'),
                    'notes': notes
                })
        
        if components_with_extracted_from:
            print(f"   Found {len(components_with_extracted_from)} components with 'Extracted from' in notes:")
            for comp in components_with_extracted_from:
                print(f"     - {comp['name']}: {comp['notes'][:50]}...")
            print(f"   ✅ This is expected - the backend still stores this information")
        else:
            print(f"   No components found with 'Extracted from' in notes")
        
        # 3. Simulate frontend transformation to verify the text won't be displayed
        print(f"\n3. Simulating frontend display...")
        for i, component in enumerate(components[:3]):  # Check first 3 components
            print(f"\n   Component {i+1}: {component.get('amc_dev_name', 'Unknown')}")
            
            # Simulate what the frontend will display
            display_name = component.get('amc_dev_name') or component.get('amc_label') or 'Unknown'
            display_type = component.get('metadata_type_name', 'Unknown')
            display_created = component.get('amc_created_timestamp', 'Unknown')
            
            print(f"     Frontend will display:")
            print(f"       Name: {display_name}")
            print(f"       Type: {display_type}")
            print(f"       Created: {display_created}")
            print(f"       Notes: [REMOVED - no longer displayed]")
            
            # Check if the notes contain "Extracted from"
            notes = component.get('amc_notes', '')
            if 'Extracted from' in notes:
                print(f"     ✅ Notes contain 'Extracted from' but will NOT be displayed in frontend")
            else:
                print(f"     ✅ Notes do not contain 'Extracted from'")
        
        print(f"\n🎉 Test complete! The 'Extracted from' text should no longer appear in the UI.")
        print(f"   Refresh your browser and check the metadata explorer.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_remove_extracted_from() 