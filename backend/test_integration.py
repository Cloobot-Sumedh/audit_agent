#!/usr/bin/env python3
"""
Test script for database integration functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_integrations():
    """Test integration endpoints"""
    print("\n🔍 Testing integration endpoints...")
    
    # Test getting integrations by org
    try:
        response = requests.get(f"{BASE_URL}/api/integrations/org/409")
        print(f"✅ Get integrations by org: {response.status_code}")
        data = response.json()
        print(f"Found {data.get('count', 0)} integrations")
        return True
    except Exception as e:
        print(f"❌ Get integrations failed: {e}")
        return False

def test_metadata_types():
    """Test metadata types endpoints"""
    print("\n🔍 Testing metadata types endpoints...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/metadata-types/org/409")
        print(f"✅ Get metadata types: {response.status_code}")
        data = response.json()
        print(f"Found {data.get('count', 0)} metadata types")
        return True
    except Exception as e:
        print(f"❌ Get metadata types failed: {e}")
        return False

def test_extraction_jobs():
    """Test extraction jobs endpoints"""
    print("\n🔍 Testing extraction jobs endpoints...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/extraction-jobs/integration/4")
        print(f"✅ Get extraction jobs: {response.status_code}")
        data = response.json()
        print(f"Found {data.get('count', 0)} extraction jobs")
        return True
    except Exception as e:
        print(f"❌ Get extraction jobs failed: {e}")
        return False

def test_metadata_components():
    """Test metadata components endpoints"""
    print("\n🔍 Testing metadata components endpoints...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/metadata-components/1")
        print(f"✅ Get metadata components: {response.status_code}")
        data = response.json()
        print(f"Found {data.get('count', 0)} metadata components")
        return True
    except Exception as e:
        print(f"❌ Get metadata components failed: {e}")
        return False

def test_search_metadata():
    """Test search metadata endpoint"""
    print("\n🔍 Testing search metadata endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/search-metadata?org_id=409")
        print(f"✅ Search metadata: {response.status_code}")
        data = response.json()
        print(f"Found {data.get('count', 0)} components in search")
        return True
    except Exception as e:
        print(f"❌ Search metadata failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Salesforce Metadata Extractor Database Integration...")
    print("=" * 60)
    
    tests = [
        test_health,
        test_integrations,
        test_metadata_types,
        test_extraction_jobs,
        test_metadata_components,
        test_search_metadata
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")
    
    return passed == total

if __name__ == "__main__":
    main() 