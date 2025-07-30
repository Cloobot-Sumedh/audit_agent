#!/usr/bin/env python3
"""
Check if metadata components are stored in the database
"""

from database import get_db_manager

def check_database_components():
    """Check what's in the database"""
    db = get_db_manager()
    
    try:
        # Check all extraction jobs
        print("🔍 Checking extraction jobs...")
        jobs = db.execute_query("SELECT * FROM ids_audit_extraction_job WHERE aej_status = 1 ORDER BY aej_created_timestamp DESC", fetch_all=True)
        
        print(f"✅ Found {len(jobs)} extraction jobs:")
        for job in jobs:
            print(f"   Job ID: {job['aej_id']}, Status: {job['aej_job_status']}, Files: {job['aej_total_files']}")
        
        # Check all metadata components
        print("\n🔍 Checking metadata components...")
        components = db.execute_query("SELECT * FROM ids_audit_metadata_component WHERE amc_status = 1 ORDER BY amc_created_timestamp DESC", fetch_all=True)
        
        print(f"✅ Found {len(components)} metadata components:")
        for comp in components:
            print(f"   Component ID: {comp['amc_id']}, Job ID: {comp['amc_extraction_job_id']}, Type ID: {comp['amc_metadata_type_id']}, Name: {comp['amc_dev_name']}")
        
        # Check metadata types
        print("\n🔍 Checking metadata types...")
        types = db.execute_query("SELECT * FROM ids_audit_metadata_type WHERE amt_status = 1 ORDER BY amt_name", fetch_all=True)
        
        print(f"✅ Found {len(types)} metadata types:")
        for type_row in types:
            print(f"   Type ID: {type_row['amt_id']}, Name: {type_row['amt_name']}")
        
        # Check integrations
        print("\n🔍 Checking integrations...")
        integrations = db.execute_query("SELECT * FROM ids_integration WHERE i_status = 1 ORDER BY i_created_timestamp DESC", fetch_all=True)
        
        print(f"✅ Found {len(integrations)} integrations:")
        for integration in integrations:
            print(f"   Integration ID: {integration['i_id']}, Name: {integration['i_name']}, Type: {integration['i_org_type']}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    print("🔍 Checking Database Contents...")
    print("=" * 50)
    
    check_database_components()
    
    print("\n" + "=" * 50)
    print("💡 This will help us understand what data is actually in the database") 