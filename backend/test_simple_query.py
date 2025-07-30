#!/usr/bin/env python3
"""
Simple test to check database query directly
"""

from database import get_db_manager

def test_simple_query():
    """Test the database query directly"""
    db = get_db_manager()
    
    try:
        # Test 1: Get all components for job 4
        print("🔍 Testing: Get all components for job 4")
        components = db.execute_query(
            "SELECT COUNT(*) as count FROM ids_audit_metadata_component WHERE amc_extraction_job_id = 4 AND amc_status = 1",
            fetch_one=True
        )
        print(f"✅ Components for job 4: {components['count'] if components else 0}")
        
        # Test 2: Get components by type for job 4
        print("\n🔍 Testing: Get CustomObject components for job 4")
        custom_objects = db.execute_query(
            "SELECT COUNT(*) as count FROM ids_audit_metadata_component WHERE amc_extraction_job_id = 4 AND amc_metadata_type_id = 3 AND amc_status = 1",
            fetch_one=True
        )
        print(f"✅ CustomObject components for job 4: {custom_objects['count'] if custom_objects else 0}")
        
        # Test 3: Get all job IDs
        print("\n🔍 Testing: Get all job IDs")
        jobs = db.execute_query(
            "SELECT DISTINCT amc_extraction_job_id FROM ids_audit_metadata_component WHERE amc_status = 1 ORDER BY amc_extraction_job_id",
            fetch_all=True
        )
        print(f"✅ Job IDs with components: {[job['amc_extraction_job_id'] for job in jobs]}")
        
        # Test 4: Get components for each job
        for job in jobs:
            job_id = job['amc_extraction_job_id']
            count = db.execute_query(
                "SELECT COUNT(*) as count FROM ids_audit_metadata_component WHERE amc_extraction_job_id = %s AND amc_status = 1",
                (job_id,),
                fetch_one=True
            )
            print(f"   Job {job_id}: {count['count'] if count else 0} components")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Simple Database Query Test...")
    print("=" * 50)
    
    test_simple_query()
    
    print("\n" + "=" * 50) 