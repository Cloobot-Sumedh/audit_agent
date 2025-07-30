#!/usr/bin/env python3
"""
Test script to verify frontend integration loading
"""

import requests
import json

def test_dashboard_endpoint():
    """Test the dashboard endpoint that the frontend uses"""
    try:
        # Test the endpoint that the frontend calls
        response = requests.get('http://localhost:5000/api/dashboard/user/243/org/409')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard endpoint working!")
            print(f"Status: {data.get('success')}")
            print(f"Integrations found: {len(data.get('integrations', []))}")
            
            if data.get('integrations'):
                print("\n📋 Integration details:")
                for i, integration in enumerate(data['integrations'], 1):
                    try:
                        integration_data = integration.get('integration', {})
                        latest_job = integration.get('latest_job', {})
                        metadata_stats = integration.get('metadata_stats', {})
                        
                        print(f"\n{i}. {integration_data.get('i_name', 'Unknown')}")
                        print(f"   Instance: {integration_data.get('i_instance_url', 'N/A')}")
                        print(f"   Type: {integration_data.get('i_org_type', 'N/A')}")
                        print(f"   Job Status: {latest_job.get('aej_job_status', 'No job')}")
                        print(f"   Components: {metadata_stats.get('total_components', 0) if metadata_stats else 0}")
                    except Exception as e:
                        print(f"   ❌ Error processing integration {i}: {e}")
                        print(f"   Raw data: {integration}")
            else:
                print("\n📝 No integrations found - this is normal for a fresh setup")
                
        else:
            print(f"❌ Dashboard endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing dashboard endpoint: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working!")
            print(f"Status: {data.get('status')}")
            print(f"Database: {data.get('database')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

if __name__ == "__main__":
    print("🧪 Testing Frontend Integration...")
    print("=" * 50)
    
    test_health_endpoint()
    print()
    test_dashboard_endpoint()
    
    print("\n" + "=" * 50)
    print("🎯 Frontend should now be able to load integrated accounts!")
    print("📱 Open http://localhost:3000 in your browser")
    print("🔄 Refresh the page to see integrated accounts loaded from database") 