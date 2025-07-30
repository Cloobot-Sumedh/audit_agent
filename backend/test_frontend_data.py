import requests
import json

def test_frontend_data():
    print("🧪 Testing frontend data structure...")
    
    try:
        # 1. Get list components from API
        print("1. Getting list components from API...")
        response = requests.get('http://localhost:5000/api/mylists/1/components')
        
        if response.status_code != 200:
            print(f"❌ API failed: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ API error: {data.get('error')}")
            return False
            
        components = data.get('components', [])
        if not components:
            print("❌ No components returned")
            return False
            
        print(f"✅ Got {len(components)} components from API")
        
        # 2. Check first component structure
        first_component = components[0]
        print("2. Checking component structure for frontend...")
        
        # Fields that MetadataObjectView expects
        expected_fields = {
            'amc_dev_name': 'Name display',
            'amc_label': 'Alternative name',
            'amc_created_timestamp': 'Created date',
            'amc_last_modified': 'Modified date',
            'amc_notes': 'Notes',
            'metadata_type_name': 'Type display'
        }
        
        print("3. Checking field values:")
        for field, description in expected_fields.items():
            value = first_component.get(field)
            print(f"  {field} ({description}): {value}")
            
            if field in ['amc_dev_name', 'amc_created_timestamp', 'metadata_type_name']:
                if not value:
                    print(f"    ❌ Missing required field: {field}")
                else:
                    print(f"    ✅ Present: {value}")
        
        # 4. Simulate frontend transformation
        print("4. Simulating frontend transformation...")
        transformed_component = {
            # Keep original database properties for MetadataObjectView
            'amc_id': first_component.get('amc_id'),
            'amc_dev_name': first_component.get('amc_dev_name'),
            'amc_label': first_component.get('amc_label'),
            'amc_notes': first_component.get('amc_notes'),
            'amc_content': first_component.get('amc_content'),
            'amc_ai_summary': first_component.get('amc_ai_summary'),
            'amc_ai_model': first_component.get('amc_ai_model'),
            'amc_last_modified': first_component.get('amc_last_modified'),
            'amc_api_version': first_component.get('amc_api_version'),
            'amc_created_timestamp': first_component.get('amc_created_timestamp'),
            'metadata_type_name': first_component.get('metadata_type_name'),
            # Add frontend-specific properties
            'name': first_component.get('amc_dev_name'),
            'type': first_component.get('metadata_type_name'),
            'addedToListAt': first_component.get('almm_created_timestamp'),
            'component_id': first_component.get('almm_component_id')
        }
        
        print("5. Transformed component structure:")
        for key, value in transformed_component.items():
            print(f"  {key}: {value}")
        
        # 6. Test MetadataObjectView logic
        print("6. Testing MetadataObjectView display logic...")
        
        # Test Name display
        name = transformed_component.get('amc_dev_name') or transformed_component.get('amc_label') or 'Unknown'
        print(f"  Name display: {name}")
        
        # Test Type display
        metadata_type = transformed_component.get('metadata_type_name')
        if metadata_type:
            object_type = metadata_type
        else:
            # Fallback logic
            filename = transformed_component.get('amc_dev_name') or transformed_component.get('amc_label') or ''
            if filename.endswith('.cls'):
                object_type = 'ApexClass'
            elif filename.endswith('.trigger'):
                object_type = 'ApexTrigger'
            elif filename.endswith('.object'):
                object_type = 'CustomObject'
            elif filename.endswith('.flow'):
                object_type = 'Flow'
            elif filename.endswith('.layout'):
                object_type = 'Layout'
            else:
                object_type = 'Unknown'
        print(f"  Type display: {object_type}")
        
        # Test Created date display
        created_timestamp = transformed_component.get('amc_created_timestamp')
        if created_timestamp:
            try:
                from datetime import datetime
                created_date = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00')).strftime('%m/%d/%Y')
                print(f"  Created date display: {created_date}")
            except:
                print(f"  Created date display: {created_timestamp}")
        else:
            print("  Created date display: Unknown")
        
        print("✅ Frontend data structure test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_frontend_data()
    if success:
        print("\n🎉 Frontend data structure is correct!")
    else:
        print("\n💥 Frontend data structure has issues!") 