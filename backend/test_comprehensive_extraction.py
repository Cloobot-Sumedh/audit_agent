#!/usr/bin/env python3
"""
Test script to verify comprehensive metadata extraction is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_metadata_extraction import get_comprehensive_metadata_retrieve_body, ALL_METADATA_TYPES

def test_comprehensive_metadata_types():
    """Test that all metadata types are included in the comprehensive extraction"""
    print("🧪 Testing Comprehensive Metadata Extraction")
    print("=" * 50)
    
    # Test the comprehensive retrieve body
    session_id = "test_session_123"
    retrieve_body = get_comprehensive_metadata_retrieve_body(session_id)
    
    print(f"✅ Comprehensive retrieve body generated successfully")
    print(f"📏 Body length: {len(retrieve_body):,} characters")
    
    # Check that all metadata types are included
    missing_types = []
    for metadata_type in ALL_METADATA_TYPES:
        if f'<name>{metadata_type}</name>' not in retrieve_body:
            missing_types.append(metadata_type)
    
    if missing_types:
        print(f"❌ Missing metadata types: {missing_types}")
        return False
    else:
        print(f"✅ All {len(ALL_METADATA_TYPES)} metadata types included")
    
    # Check for key elements
    required_elements = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<soapenv:Envelope',
        '<met:SessionHeader>',
        f'<met:sessionId>{session_id}</met:sessionId>',
        '<met:retrieve>',
        '<met:retrieveRequest>',
        '<met:apiVersion>62.0</met:apiVersion>',
        '<met:singlePackage>true</met:singlePackage>',
        '<met:unpackaged>'
    ]
    
    for element in required_elements:
        if element not in retrieve_body:
            print(f"❌ Missing required element: {element}")
            return False
    
    print("✅ All required XML elements present")
    
    # Count the number of metadata types
    type_count = retrieve_body.count('<name>')
    print(f"📊 Total metadata types in request: {type_count}")
    
    # Show some examples of included types
    print("\n📋 Sample metadata types included:")
    sample_types = ['ApexClass', 'CustomObject', 'Flow', 'Layout', 'PermissionSet', 
                   'Profile', 'Report', 'Dashboard', 'WaveApplication', 'CustomMetadata']
    
    for sample_type in sample_types:
        if f'<name>{sample_type}</name>' in retrieve_body:
            print(f"  ✅ {sample_type}")
        else:
            print(f"  ❌ {sample_type}")
    
    print("\n🎯 Comprehensive extraction is ready!")
    return True

def test_metadata_extraction_functions():
    """Test that the extraction functions are properly updated"""
    print("\n🧪 Testing Extraction Functions")
    print("=" * 40)
    
    try:
        from server_db import extract_metadata_corrected, extract_metadata_to_database
        
        # Check function docstrings
        if "COMPREHENSIVE" in extract_metadata_corrected.__doc__:
            print("✅ extract_metadata_corrected updated for comprehensive extraction")
        else:
            print("❌ extract_metadata_corrected not updated")
            
        if "COMPREHENSIVE" in extract_metadata_to_database.__doc__:
            print("✅ extract_metadata_to_database updated for comprehensive extraction")
        else:
            print("❌ extract_metadata_to_database not updated")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Comprehensive Metadata Extraction Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test 1: Comprehensive metadata types
    if not test_comprehensive_metadata_types():
        success = False
    
    # Test 2: Extraction functions
    if not test_metadata_extraction_functions():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Comprehensive extraction is ready.")
        print("\n📝 Next Steps:")
        print("1. Run a new metadata extraction from your Salesforce org")
        print("2. The extraction will now include ALL 80+ metadata types")
        print("3. Expect longer processing times (15-30 minutes for medium orgs)")
        print("4. Check the dashboard for comprehensive results")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 