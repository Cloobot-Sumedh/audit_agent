#!/usr/bin/env python3
"""
Test script to verify loading screen functionality during extraction
"""

import requests
import json
import time

def test_extraction_with_loading_screen():
    """Test extraction process to verify loading screen shows progress"""
    try:
        print("🧪 Testing Extraction with Loading Screen...")
        print("=" * 50)
        
        # Test 1: Start extraction
        print("\n🔍 Step 1: Starting extraction...")
        response = requests.post('http://localhost:5000/api/dashboard/extract/6')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                job_id = data.get('job_id')
                print(f"✅ Extraction started with job ID: {job_id}")
                
                # Test 2: Monitor progress
                print("\n🔍 Step 2: Monitoring progress...")
                max_checks = 10
                for i in range(max_checks):
                    time.sleep(3)  # Wait 3 seconds between checks
                    
                    status_response = requests.get(f'http://localhost:5000/api/dashboard/job-status/{job_id}')
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        print(f"\n📊 Check {i+1}/{max_checks}:")
                        print(f"   Status: {status_data.get('status', 'unknown')}")
                        print(f"   Progress messages: {len(status_data.get('progress', []))}")
                        
                        if status_data.get('progress'):
                            latest_progress = status_data['progress'][-1] if status_data['progress'] else 'No progress'
                            print(f"   Latest: {latest_progress}")
                        
                        if status_data.get('status') == 'success':
                            print("✅ Extraction completed successfully!")
                            break
                        elif status_data.get('status') == 'error':
                            print(f"❌ Extraction failed: {status_data.get('error')}")
                            break
                    else:
                        print(f"❌ Failed to check status: {status_response.status_code}")
                        break
                else:
                    print("⏰ Extraction timed out")
            else:
                print(f"❌ Failed to start extraction: {data.get('error')}")
        else:
            print(f"❌ Failed to start extraction: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing loading screen: {e}")

if __name__ == "__main__":
    test_extraction_with_loading_screen()
    
    print("\n" + "=" * 50)
    print("🎯 Loading Screen Test Complete!")
    print("📱 Check the frontend at http://localhost:3000")
    print("🔄 Click 'Extract Metadata' to see the loading screen in action") 