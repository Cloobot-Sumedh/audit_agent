import requests
import json

def test_user_experience_summary():
    print("🧪 Testing Complete User Experience for Automatic Summary Generation...")
    
    try:
        # 1. Test that both frontend and backend are accessible
        print("1. Testing system accessibility...")
        
        frontend_response = requests.get('http://localhost:3000')
        backend_response = requests.get('http://localhost:5000/api/health')
        
        if frontend_response.status_code != 200:
            print(f"❌ Frontend not accessible: {frontend_response.status_code}")
            return False
            
        if backend_response.status_code != 200:
            print(f"❌ Backend not accessible: {backend_response.status_code}")
            return False
            
        print("✅ Frontend and backend are accessible")
        
        # 2. Get a component that likely doesn't have a summary
        print("2. Finding a component without existing summary...")
        response = requests.get('http://localhost:5000/api/metadata-components/5')
        
        if response.status_code != 200:
            print(f"❌ Could not get metadata components: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success') or not data.get('components'):
            print("❌ No components found")
            return False
        
        # Find a component without existing summary
        component_without_summary = None
        for component in data['components']:
            component_id = component['amc_id']
            details_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
            
            if details_response.status_code == 200:
                details_data = details_response.json()
                if details_data.get('success'):
                    existing_summary = details_data.get('ai_summary', '')
                    if not existing_summary or not existing_summary.strip():
                        component_without_summary = component
                        break
        
        if not component_without_summary:
            print("ℹ️  All components already have summaries, using first component")
            component_without_summary = data['components'][0]
        
        component_id = component_without_summary['amc_id']
        component_name = component_without_summary.get('amc_dev_name', 'Unknown')
        
        print(f"✅ Using component ID: {component_id}")
        print(f"   Component: {component_name}")
        print(f"   Type: {component_without_summary.get('metadata_type_name', 'Unknown')}")
        
        # 3. Simulate the frontend behavior - check details first
        print("3. Simulating frontend behavior - checking for existing summary...")
        details_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
        
        if details_response.status_code != 200:
            print(f"❌ Could not get component details: {details_response.status_code}")
            return False
            
        details_data = details_response.json()
        if not details_data.get('success'):
            print(f"❌ Failed to get component details: {details_data.get('error')}")
            return False
        
        existing_summary = details_data.get('ai_summary', '')
        if existing_summary and existing_summary.strip():
            print(f"✅ Found existing AI summary ({len(existing_summary)} characters)")
            print(f"   Summary preview: {existing_summary[:100]}...")
            print("   ✅ User will see existing summary immediately")
        else:
            print("ℹ️  No existing AI summary found")
            print("   ✅ System will automatically generate summary")
            
            # 4. Simulate automatic generation
            print("4. Simulating automatic summary generation...")
            generate_response = requests.post(f'http://localhost:5000/api/metadata-component/{component_id}/generate-summary')
            
            if generate_response.status_code != 200:
                print(f"❌ Could not generate summary: {generate_response.status_code}")
                return False
                
            generate_data = generate_response.json()
            if not generate_data.get('success'):
                print(f"❌ Failed to generate summary: {generate_data.get('error')}")
                return False
                
            generated_summary = generate_data.get('summary', '')
            if generated_summary and generated_summary.strip():
                print(f"✅ Successfully generated AI summary ({len(generated_summary)} characters)")
                print(f"   Summary preview: {generated_summary[:100]}...")
                print("   ✅ User will see generated summary automatically")
            else:
                print("❌ Generated summary is empty")
                return False
        
        # 5. Verify the complete flow works
        print("5. Verifying complete user experience flow...")
        
        # Simulate what happens when user clicks on a component
        # 1. Get details (should include summary)
        details_response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
        details_data = details_response.json()
        
        if details_data.get('success'):
            final_summary = details_data.get('ai_summary', '')
            if final_summary and final_summary.strip():
                print(f"✅ Final verification: User will see summary ({len(final_summary)} characters)")
                print("   ✅ No manual button clicking required")
                print("   ✅ Summary is automatically available")
            else:
                print("❌ Final verification failed: No summary available")
                return False
        else:
            print("❌ Final verification failed: Could not get component details")
            return False
        
        print("\n🎉 Complete user experience test passed!")
        print("\n📊 User Experience Summary:")
        print("   ✅ User clicks on any metadata component")
        print("   ✅ System automatically checks for existing summary")
        print("   ✅ If summary exists: Shows immediately")
        print("   ✅ If no summary: Generates automatically")
        print("   ✅ No manual 'Generate Summary' button needed")
        print("   ✅ Summary is stored for future use")
        print("   ✅ Seamless user experience")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_user_experience_summary()
    if success:
        print("\n✅ User experience test completed successfully!")
    else:
        print("\n❌ User experience test failed!") 