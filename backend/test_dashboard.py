#!/usr/bin/env python3
"""
Test script for dashboard functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_user_dashboard():
    """Test getting user dashboard data"""
    print("🔍 Testing user dashboard...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/user/243/org/409")
        print(f"✅ User dashboard: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            integrations = data.get('integrations', [])
            print(f"Found {len(integrations)} integrations")
            
            for integration_data in integrations:
                integration = integration_data.get('integration', {})
                latest_job = integration_data.get('latest_job')
                metadata_stats = integration_data.get('metadata_stats')
                
                print(f"  - Integration: {integration.get('i_name')}")
                print(f"    Instance URL: {integration.get('i_instance_url')}")
                print(f"    Has Latest Job: {latest_job is not None}")
                if latest_job:
                    print(f"    Job Status: {latest_job.get('aej_job_status')}")
                    print(f"    Total Files: {latest_job.get('aej_total_files')}")
                if metadata_stats:
                    print(f"    Total Components: {metadata_stats.get('total_components')}")
                    print(f"    Types: {len(metadata_stats.get('by_type', []))}")
                print()
            
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ User dashboard failed: {e}")
        return False

def test_integration_dashboard(integration_id):
    """Test getting integration dashboard data"""
    print(f"\n🔍 Testing integration dashboard {integration_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/integration/{integration_id}")
        print(f"✅ Integration dashboard: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            dashboard_data = data.get('dashboard_data', {})
            
            integration = dashboard_data.get('integration', {})
            latest_job = dashboard_data.get('latest_job')
            metadata_stats = dashboard_data.get('metadata_stats')
            components = dashboard_data.get('metadata_components', [])
            
            print(f"Integration: {integration.get('i_name')}")
            print(f"Instance URL: {integration.get('i_instance_url')}")
            print(f"Has Latest Job: {latest_job is not None}")
            
            if latest_job:
                print(f"Job Status: {latest_job.get('aej_job_status')}")
                print(f"Total Files: {latest_job.get('aej_total_files')}")
            
            if metadata_stats:
                print(f"Total Components: {metadata_stats.get('total_components')}")
                print("Components by Type:")
                for type_stat in metadata_stats.get('by_type', []):
                    print(f"  - {type_stat.get('metadata_type')}: {type_stat.get('component_count')}")
            
            print(f"Metadata Components: {len(components)}")
            
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Integration dashboard failed: {e}")
        return False

def test_dashboard_extract(integration_id):
    """Test extracting metadata for dashboard"""
    print(f"\n🔍 Testing dashboard extract for integration {integration_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/dashboard/extract/{integration_id}")
        print(f"✅ Dashboard extract: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"Job ID: {job_id}")
            print(f"Message: {data.get('message')}")
            return job_id
        else:
            print(f"Response: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard extract failed: {e}")
        return None

def test_dashboard_job_status(job_id):
    """Test getting dashboard job status"""
    print(f"\n🔍 Testing dashboard job status {job_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/job-status/{job_id}")
        print(f"✅ Dashboard job status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            progress = data.get('progress', [])
            dashboard_data = data.get('dashboard_data')
            
            print(f"Status: {status}")
            print(f"Progress Steps: {len(progress)}")
            for step in progress:
                print(f"  - {step}")
            
            if dashboard_data:
                print("Dashboard data available!")
                integration = dashboard_data.get('integration', {})
                print(f"Integration: {integration.get('i_name')}")
            
            return True
        else:
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard job status failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Dashboard Functionality...")
    print("=" * 60)
    
    # Test user dashboard
    test_user_dashboard()
    
    # Get the first integration ID from user dashboard
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/user/243/org/409")
        if response.status_code == 200:
            data = response.json()
            integrations = data.get('integrations', [])
            if integrations:
                first_integration_id = integrations[0]['integration']['i_id']
                print(f"\n📝 Using integration ID: {first_integration_id}")
                
                # Test integration dashboard with actual integration ID
                test_integration_dashboard(first_integration_id)
                
                # Test dashboard extract with actual integration ID
                job_id = test_dashboard_extract(first_integration_id)
                
                if job_id:
                    # Test job status
                    test_dashboard_job_status(job_id)
            else:
                print("❌ No integrations found to test")
        else:
            print("❌ Failed to get user dashboard for testing")
    except Exception as e:
        print(f"❌ Error getting integration ID: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Dashboard functionality tests completed!")
    print("💡 Use real Salesforce credentials to test extraction functionality")

if __name__ == "__main__":
    main() 