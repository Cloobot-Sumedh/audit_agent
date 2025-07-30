import requests
import json

def test_frontend_refresh():
    print("🧪 Testing frontend data refresh...")
    
    try:
        # 1. Check the current list components
        print("1. Checking current list components...")
        response = requests.get('http://localhost:5000/api/mylists/9/components')
        
        if response.status_code != 200:
            print(f"❌ Failed to get list components: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to get list components: {data.get('error')}")
            return False
            
        components = data.get('components', [])
        print(f"✅ Found {len(components)} components in list")
        
        # 2. Check each component's data structure
        for i, component in enumerate(components):
            print(f"\n2. Component {i+1} data structure:")
            print(f"   ID: {component.get('amc_id')}")
            print(f"   Name: {component.get('amc_dev_name', 'Unknown')}")
            print(f"   Type: {component.get('metadata_type_name', 'Unknown')}")
            print(f"   Created: {component.get('amc_created_timestamp', 'Unknown')}")
            print(f"   Notes: {component.get('amc_notes', 'Unknown')}")
            
            # Check if this matches what the frontend expects
            expected_name = component.get('amc_dev_name') or component.get('amc_label') or 'Unknown'
            expected_type = component.get('metadata_type_name', 'Unknown')
            expected_created = component.get('amc_created_timestamp', 'Unknown')
            
            print(f"   Expected frontend values:")
            print(f"     Name: {expected_name}")
            print(f"     Type: {expected_type}")
            print(f"     Created: {expected_created}")
            
            # Check if any values are None or missing
            if expected_name == 'Unknown' or expected_type == 'Unknown' or expected_created == 'Unknown':
                print(f"   ⚠️ Some values are Unknown - this might cause frontend issues")
            else:
                print(f"   ✅ All values are present")
        
        # 3. Test the specific component that's showing issues
        print(f"\n3. Testing ProductConfigMetadataUpdater component...")
        target_component = None
        for comp in components:
            if comp.get('amc_id') == 4703:
                target_component = comp
                break
        
        if target_component:
            print(f"   Found ProductConfigMetadataUpdater:")
            print(f"     Name: {target_component.get('amc_dev_name', 'Unknown')}")
            print(f"     Type: {target_component.get('metadata_type_name', 'Unknown')}")
            print(f"     Created: {target_component.get('amc_created_timestamp', 'Unknown')}")
            print(f"     Notes: {target_component.get('amc_notes', 'Unknown')}")
            
            # Check if the values match what should be displayed
            name = target_component.get('amc_dev_name', 'Unknown')
            metadata_type = target_component.get('metadata_type_name', 'Unknown')
            created = target_component.get('amc_created_timestamp', 'Unknown')
            
            if name != 'Unknown' and metadata_type != 'Unknown' and created != 'Unknown':
                print(f"   ✅ Backend data is correct")
                print(f"   🔍 Frontend should display:")
                print(f"     Name: {name}")
                print(f"     Type: {metadata_type}")
                print(f"     Created: {created}")
            else:
                print(f"   ❌ Backend data has Unknown values")
        else:
            print(f"   ❌ ProductConfigMetadataUpdater not found in list")
        
        # 4. Check if there are any data transformation issues
        print(f"\n4. Checking data transformation...")
        print(f"   API response structure:")
        print(f"     - amc_id: {components[0].get('amc_id') if components else 'N/A'}")
        print(f"     - amc_dev_name: {components[0].get('amc_dev_name') if components else 'N/A'}")
        print(f"     - metadata_type_name: {components[0].get('metadata_type_name') if components else 'N/A'}")
        print(f"     - amc_created_timestamp: {components[0].get('amc_created_timestamp') if components else 'N/A'}")
        
        print(f"\n🎉 Test complete! If backend data is correct but frontend shows Unknown,")
        print(f"   the issue is likely a frontend caching or refresh problem.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_frontend_refresh() 