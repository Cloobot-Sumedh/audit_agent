#!/usr/bin/env python3
"""
Test script to verify on-demand AI summary generation
"""

import requests
import json

def test_on_demand_ai():
    """Test on-demand AI summary generation"""
    try:
        print("🧪 Testing On-Demand AI Summary Generation...")
        print("=" * 50)
        
        # Test 1: Get a component without AI summary
        print("\n🔍 Step 1: Getting a component...")
        response = requests.get('http://localhost:5000/api/metadata-components/5')
        
        if response.status_code != 200:
            print("❌ Could not get metadata components")
            return
            
        data = response.json()
        if not data.get('success') or not data.get('components'):
            print("❌ No components found")
            return
            
        # Get the first component
        component = data['components'][0]
        component_id = component['amc_id']
        print(f"✅ Using component ID: {component_id}")
        print(f"   Component: {component.get('amc_dev_name', 'Unknown')}")
        print(f"   Type: {component.get('metadata_type_name', 'Unknown')}")
        
        # Check if it has an AI summary
        ai_summary = component.get('amc_ai_summary')
        if ai_summary:
            print(f"   📝 Existing AI Summary: {len(ai_summary)} characters")
        else:
            print(f"   ❌ No AI summary found")
        
        # Test 2: Generate AI summary on-demand
        print("\n🔍 Step 2: Generating AI summary on-demand...")
        response = requests.post(f'http://localhost:5000/api/metadata-component/{component_id}/generate-summary')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data.get('summary', '')
                print(f"✅ AI Summary generated successfully!")
                print(f"   📝 Summary length: {len(summary)} characters")
                print(f"   📝 Summary preview: {summary[:100]}...")
            else:
                print(f"❌ Failed to generate summary: {data.get('error')}")
        else:
            print(f"❌ Failed to generate summary: {response.status_code}")
        
        # Test 3: Verify the summary was stored
        print("\n🔍 Step 3: Verifying summary was stored...")
        response = requests.get(f'http://localhost:5000/api/metadata-component/{component_id}/details')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stored_summary = data.get('ai_summary', '')
                if stored_summary:
                    print(f"✅ Summary stored successfully!")
                    print(f"   📝 Stored summary length: {len(stored_summary)} characters")
                else:
                    print(f"❌ Summary not found in database")
            else:
                print(f"❌ Failed to get component details: {data.get('error')}")
        else:
            print(f"❌ Failed to get component details: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎯 On-Demand AI Summary Generation Test Complete!")
        print("📱 Try clicking on metadata components and using the 'Generate Summary' button")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server_db.py is running.")
    except Exception as e:
        print(f"❌ Error testing on-demand AI: {e}")

if __name__ == "__main__":
    test_on_demand_ai() 