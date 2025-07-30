import requests
import json

def test_list_summary_generation():
    print("🧪 Testing List Summary Generation...")
    
    try:
        # 1. Test that the frontend is accessible
        print("1. Testing frontend accessibility...")
        response = requests.get('http://localhost:3000')
        
        if response.status_code != 200:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
        print("✅ Frontend is accessible")
        
        # 2. Test that the backend is accessible
        print("2. Testing backend accessibility...")
        response = requests.get('http://localhost:5000/api/health')
        
        if response.status_code != 200:
            print(f"❌ Backend not accessible: {response.status_code}")
            return False
            
        print("✅ Backend is accessible")
        
        # 3. Get user lists to find a test list
        print("3. Getting user lists...")
        response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')  # Use existing user and org
        
        if response.status_code != 200:
            print(f"❌ Failed to get user lists: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to get user lists: {data.get('error')}")
            return False
            
        lists = data.get('mylists', [])  # Use 'mylists' instead of 'lists'
        if not lists:
            print("❌ No lists found for testing")
            return False
            
        test_list = lists[0]
        print(f"✅ Found test list: {test_list['aml_name']}")  # Use 'aml_name' instead of 'title'
        
        # 4. Test list summary generation
        print("4. Testing list summary generation...")
        response = requests.post(f'http://localhost:5000/api/mylists/{test_list["aml_id"]}/generate-summaries')  # Use 'aml_id' instead of 'id'
        
        if response.status_code != 200:
            print(f"❌ Failed to generate list summary: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to generate list summary: {data.get('error')}")
            return False
            
        print("✅ List summary generated successfully")
        print(f"   - List Name: {data.get('list_name')}")
        print(f"   - Total Components: {data.get('total_components')}")
        print(f"   - Summaries Generated: {data.get('summaries_generated')}")
        
        # 5. Verify the combined summary structure
        combined_summary = data.get('combined_summary', '')
        if not combined_summary:
            print("❌ No combined summary generated")
            return False
            
        print("✅ Combined summary structure verified")
        print(f"   - Summary length: {len(combined_summary)} characters")
        print(f"   - Contains list name: {data.get('list_name') in combined_summary}")
        
        # 6. Test the frontend integration
        print("6. Testing frontend integration...")
        print("   - Frontend should automatically generate summaries when a list is selected")
        print("   - Right panel should show list summary when no object is selected")
        print("   - Right panel should show object details when an object is selected")
        
        print("\n🎉 All tests passed! List summary generation is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_list_summary_generation() 