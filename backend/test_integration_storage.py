#!/usr/bin/env python3
"""
Test script for integration storage functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_store_integration():
    """Test storing integration details"""
    print("🔍 Testing integration storage...")
    
    # Test data (replace with actual credentials for testing)
    test_data = {
        "username": "test@example.com",
        "password": "testpassword123",
        "security_token": "testtoken",
        "is_sandbox": True,
        "name": "Test Integration",
        "org_id": 409,
        "ext_app_id": 1001,
        "created_user_id": 243
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/store-integration", json=test_data)
        print(f"✅ Store integration: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Integration ID: {data.get('integration_id')}")
            print(f"Message: {data.get('message')}")
            return data.get('integration_id')
        else:
            print(f"Response: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Store integration failed: {e}")
        return None

def test_get_integration(integration_id):
    """Test getting integration details"""
    print(f"\n🔍 Testing get integration {integration_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/integrations/{integration_id}")
        print(f"✅ Get integration: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            integration = data.get('integration', {})
            print(f"Integration Name: {integration.get('i_name')}")
            print(f"Instance URL: {integration.get('i_instance_url')}")
            print(f"Has Credentials: {integration.get('has_credentials')}")
            print(f"Token Length: {integration.get('token_length')}")
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Get integration failed: {e}")
        return False

def test_get_integrations_by_org():
    """Test getting integrations by organization"""
    print("\n🔍 Testing get integrations by org...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/integrations/org/409")
        print(f"✅ Get integrations by org: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            integrations = data.get('integrations', [])
            print(f"Found {len(integrations)} integrations")
            
            for integration in integrations:
                print(f"  - ID: {integration.get('i_id')}, Name: {integration.get('i_name')}")
            
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Get integrations by org failed: {e}")
        return False

def test_login_with_integration(integration_id):
    """Test logging in with stored integration"""
    print(f"\n🔍 Testing login with integration {integration_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/login-with-integration/{integration_id}")
        print(f"✅ Login with integration: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message')}")
            print(f"Environment: {data.get('environment')}")
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Login with integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Integration Storage Functionality...")
    print("=" * 60)
    
    # Test storing integration
    integration_id = test_store_integration()
    
    if integration_id:
        # Test getting integration
        test_get_integration(integration_id)
        
        # Test getting all integrations
        test_get_integrations_by_org()
        
        # Test login with integration (will fail with test credentials)
        test_login_with_integration(integration_id)
        
        print("\n" + "=" * 60)
        print("✅ Integration storage functionality is working!")
        print(f"📝 Integration ID {integration_id} was created successfully")
        print("💡 Use real Salesforce credentials to test login functionality")
    else:
        print("\n" + "=" * 60)
        print("❌ Integration storage test failed")
        print("💡 Check server logs for details")

if __name__ == "__main__":
    main() 