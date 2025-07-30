import requests
import json

def debug_lists_api():
    print("🔍 Debugging Lists API...")
    
    try:
        # Test the API endpoint
        print("1. Testing lists API endpoint...")
        response = requests.get('http://localhost:5000/api/mylists/user/243/org/409')
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw response: {response.text}")
        
        # Test with different user/org combinations
        print("\n2. Testing with different user/org combinations...")
        
        test_combinations = [
            (1, 1),
            (243, 409),
            (243, 1),
            (1, 409)
        ]
        
        for user_id, org_id in test_combinations:
            print(f"\nTesting user_id={user_id}, org_id={org_id}")
            response = requests.get(f'http://localhost:5000/api/mylists/user/{user_id}/org/{org_id}')
            print(f"Status: {response.status_code}")
            try:
                data = response.json()
                print(f"Success: {data.get('success')}")
                print(f"Lists count: {len(data.get('lists', []))}")
            except:
                print(f"Raw: {response.text[:200]}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_lists_api() 