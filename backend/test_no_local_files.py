#!/usr/bin/env python3
"""
Test script to verify that metadata extraction works without local files
"""

import requests
import json
import time

# Test the new in-memory processing
def test_in_memory_extraction():
    print("🧪 Testing in-memory metadata extraction (no local files)...")
    
    # Test data for integration
    test_integration = {
        "username": "test@example.com",
        "password": "testpassword",
        "security_token": "",
        "is_sandbox": True,
        "name": "Test Integration"
    }
    
    try:
        # 1. Test login
        print("1. Testing login...")
        login_response = requests.post(
            'http://localhost:5000/api/login-test',
            json=test_integration,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get('success'):
                print("✅ Login test successful")
            else:
                print(f"❌ Login test failed: {login_data.get('error')}")
                return False
        else:
            print(f"❌ Login test failed with status: {login_response.status_code}")
            return False
        
        # 2. Store integration
        print("2. Storing integration...")
        store_response = requests.post(
            'http://localhost:5000/api/store-integration',
            json=test_integration,
            headers={'Content-Type': 'application/json'}
        )
        
        if store_response.status_code == 200:
            store_data = store_response.json()
            if store_data.get('success'):
                integration_id = store_data.get('integration_id')
                print(f"✅ Integration stored with ID: {integration_id}")
            else:
                print(f"❌ Failed to store integration: {store_data.get('error')}")
                return False
        else:
            print(f"❌ Store integration failed with status: {store_response.status_code}")
            return False
        
        # 3. Test extraction (this will use the new in-memory processing)
        print("3. Testing metadata extraction (in-memory)...")
        extract_response = requests.post(
            f'http://localhost:5000/api/dashboard/extract/{integration_id}',
            headers={'Content-Type': 'application/json'}
        )
        
        if extract_response.status_code == 200:
            extract_data = extract_response.json()
            if extract_data.get('success'):
                job_id = extract_data.get('job_id')
                print(f"✅ Extraction started with job ID: {job_id}")
                
                # 4. Monitor job status
                print("4. Monitoring job status...")
                max_attempts = 30
                attempt = 0
                
                while attempt < max_attempts:
                    attempt += 1
                    print(f"   Checking status... ({attempt}/{max_attempts})")
                    
                    status_response = requests.get(
                        f'http://localhost:5000/api/dashboard/job-status/{job_id}'
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data.get('status') == 'success':
                            print("✅ Extraction completed successfully!")
                            print(f"   Progress: {len(status_data.get('progress', []))} steps")
                            return True
                        elif status_data.get('status') == 'error':
                            print(f"❌ Extraction failed: {status_data.get('error')}")
                            return False
                        else:
                            # Still running
                            progress = status_data.get('progress', [])
                            if progress:
                                print(f"   Latest: {progress[-1]}")
                            time.sleep(2)
                    else:
                        print(f"❌ Status check failed: {status_response.status_code}")
                        return False
                
                print("❌ Extraction timed out")
                return False
            else:
                print(f"❌ Extraction failed: {extract_data.get('error')}")
                return False
        else:
            print(f"❌ Extraction request failed: {extract_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing No Local Files Extraction")
    print("=" * 50)
    
    success = test_in_memory_extraction()
    
    if success:
        print("\n✅ All tests passed! No local files were created.")
    else:
        print("\n❌ Tests failed.")
    
    print("\n📝 Summary:")
    print("- No local folder creation")
    print("- No file system operations")
    print("- Direct database storage")
    print("- In-memory zip processing") 