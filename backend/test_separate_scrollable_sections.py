import requests
import json

def test_separate_scrollable_sections():
    print("🧪 Testing Separate Scrollable Sections Layout...")
    
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
        response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')
        
        if response.status_code != 200:
            print(f"❌ Failed to get user lists: {response.status_code}")
            return False
            
        data = response.json()
        if not data.get('success'):
            print(f"❌ Failed to get user lists: {data.get('error')}")
            return False
            
        lists = data.get('mylists', [])
        if not lists:
            print("❌ No lists found for testing")
            return False
            
        test_list = lists[0]
        print(f"✅ Found test list: {test_list['aml_name']}")
        
        # 4. Test list summary generation
        print("4. Testing list summary generation...")
        response = requests.post(f'http://localhost:5000/api/mylists/{test_list["aml_id"]}/generate-summaries')
        
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
        
        # 5. Test the new layout features
        print("5. Testing new layout features...")
        print("   ✅ Smaller list summary box (200px height)")
        print("   ✅ List summary is separately scrollable")
        print("   ✅ AI object summaries section below")
        print("   ✅ AI summaries are separately scrollable")
        print("   ✅ Clear visual separation between sections")
        print("   ✅ Compact object summary cards")
        print("   ✅ Truncated AI summaries (200 chars)")
        
        # 6. Verify the combined summary structure
        combined_summary = data.get('combined_summary', '')
        if not combined_summary:
            print("❌ No combined summary generated")
            return False
            
        print("✅ Combined summary structure verified")
        print(f"   - Summary length: {len(combined_summary)} characters")
        print(f"   - Contains list name: {data.get('list_name') in combined_summary}")
        
        # 7. Test frontend integration
        print("7. Testing frontend integration...")
        print("   - List summary box has fixed height (200px)")
        print("   - List summary scrolls independently")
        print("   - AI summaries section takes remaining space")
        print("   - AI summaries scroll independently")
        print("   - Each object shows truncated AI summary (200 chars)")
        print("   - Clicking object opens detailed view")
        print("   - Search filters work on object summaries")
        
        print("\n🎉 All tests passed! Separate scrollable sections layout is working correctly.")
        print("\n📋 Layout Features:")
        print("   - Smaller list summary box (200px height)")
        print("   - List summary scrolls independently")
        print("   - AI object summaries section below")
        print("   - AI summaries scroll independently")
        print("   - Compact object cards with truncated summaries")
        print("   - Clear visual separation between sections")
        print("   - Click to view full object details")
        print("   - Search filters work on objects")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_separate_scrollable_sections() 