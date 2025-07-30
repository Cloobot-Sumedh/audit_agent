#!/usr/bin/env python3
"""
Test script to verify dependency extraction and storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager
import json

def test_dependency_extraction():
    """Test dependency extraction and storage"""
    db = get_db_manager()
    
    try:
        print("🔍 Testing Dependency Extraction and Storage")
        print("=" * 50)
        
        # Check all extraction jobs
        print("\n1. Checking extraction jobs...")
        jobs = db.execute_query("SELECT * FROM ids_audit_extraction_job WHERE aej_status = 1 ORDER BY aej_created_timestamp DESC", fetch_all=True)
        
        print(f"✅ Found {len(jobs)} extraction jobs:")
        for job in jobs:
            print(f"   Job ID: {job['aej_id']}, Status: {job['aej_job_status']}, Files: {job['aej_total_files']}, Integration: {job['aej_integration_id']}")
        
        # Check all metadata components
        print("\n2. Checking metadata components...")
        components = db.execute_query("SELECT * FROM ids_audit_metadata_component WHERE amc_status = 1 ORDER BY amc_created_timestamp DESC", fetch_all=True)
        
        print(f"✅ Found {len(components)} metadata components:")
        for comp in components:
            print(f"   Component ID: {comp['amc_id']}, Job ID: {comp['amc_extraction_job_id']}, Name: {comp['amc_dev_name']}, Type ID: {comp['amc_metadata_type_id']}")
        
        # Check all dependencies
        print("\n3. Checking dependencies...")
        dependencies = db.execute_query("SELECT * FROM ids_audit_metadata_dependency WHERE amd_status = 1 ORDER BY amd_created_timestamp DESC", fetch_all=True)
        
        print(f"✅ Found {len(dependencies)} dependencies:")
        for dep in dependencies:
            print(f"   Dependency ID: {dep['amd_id']}, From: {dep['amd_from_component_id']}, To: {dep['amd_to_component_id']}, Type: {dep['amd_dependency_type']}")
        
        # Check metadata types
        print("\n4. Checking metadata types...")
        types = db.execute_query("SELECT * FROM ids_audit_metadata_type WHERE amt_status = 1 ORDER BY amt_name", fetch_all=True)
        
        print(f"✅ Found {len(types)} metadata types:")
        for type_row in types:
            print(f"   Type ID: {type_row['amt_id']}, Name: {type_row['amt_name']}")
        
        # Test dependency network for a specific component
        print("\n5. Testing dependency network...")
        if components:
            test_component = components[0]
            print(f"Testing dependency network for component: {test_component['amc_dev_name']} (ID: {test_component['amc_id']})")
            
            # Get dependencies for this component
            deps = db.get_dependencies_for_component(test_component['amc_id'])
            print(f"Found {len(deps)} dependencies for this component")
            
            for dep in deps:
                print(f"   - {dep.get('from_dev_name', 'Unknown')} → {dep.get('to_dev_name', 'Unknown')} ({dep['amd_dependency_type']})")
        
        # Check for unique component IDs across extractions
        print("\n6. Checking for unique component IDs...")
        component_jobs = db.execute_query("""
            SELECT amc_extraction_job_id, COUNT(*) as component_count, 
                   COUNT(DISTINCT amc_dev_name) as unique_names
            FROM ids_audit_metadata_component 
            WHERE amc_status = 1 
            GROUP BY amc_extraction_job_id
            ORDER BY amc_extraction_job_id DESC
        """, fetch_all=True)
        
        print("Component distribution across extraction jobs:")
        for job in component_jobs:
            print(f"   Job {job['amc_extraction_job_id']}: {job['component_count']} components, {job['unique_names']} unique names")
        
        # Check for duplicate dependencies
        print("\n7. Checking for duplicate dependencies...")
        duplicate_deps = db.execute_query("""
            SELECT amd_from_component_id, amd_to_component_id, amd_dependency_type, COUNT(*) as count
            FROM ids_audit_metadata_dependency 
            WHERE amd_status = 1 
            GROUP BY amd_from_component_id, amd_to_component_id, amd_dependency_type
            HAVING COUNT(*) > 1
        """, fetch_all=True)
        
        if duplicate_deps:
            print(f"⚠️  Found {len(duplicate_deps)} potential duplicate dependencies:")
            for dup in duplicate_deps:
                print(f"   From: {dup['amd_from_component_id']}, To: {dup['amd_to_component_id']}, Type: {dup['amd_dependency_type']}, Count: {dup['count']}")
        else:
            print("✅ No duplicate dependencies found")
        
        print("\n" + "=" * 50)
        print("✅ Dependency extraction test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during dependency extraction test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dependency_extraction() 