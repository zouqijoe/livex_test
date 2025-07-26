#!/usr/bin/env python3
"""
Test script for Cal.com API integration
This script helps verify that the Cal.com API is working correctly.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_cal_api():
    """Test Cal.com API connectivity"""
    print("🧪 Testing Cal.com API Integration")
    print("=" * 50)
    
    # Get environment variables
    cal_api_key = os.getenv("CAL_API_KEY")
    cal_username = os.getenv("CAL_USERNAME")
    
    if not cal_api_key:
        print("❌ CAL_API_KEY not found in environment variables")
        return False
    
    if not cal_username:
        print("❌ CAL_USERNAME not found in environment variables")
        return False
    
    print(f"✅ Cal.com API Key: {cal_api_key[:20]}...")
    print(f"✅ Cal.com Username: {cal_username}")
    
    # Test headers
    headers = {
        "Authorization": f"Bearer {cal_api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get event types
    print("\n📋 Testing: Get Event Types")
    try:
        url = "https://api.cal.com/v2/event-types"
        params = {"user": cal_username}
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            event_types = data.get("event_types", [])
            print(f"✅ Found {len(event_types)} event types")
            for event in event_types[:3]:  # Show first 3
                print(f"  - {event.get('title', 'Untitled')} (ID: {event.get('id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # Test 2: Get bookings
    print("\n📅 Testing: Get Bookings")
    try:
        url = "https://api.cal.com/v2/bookings"
        params = {"user": cal_username}
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            bookings = data.get("bookings", [])
            print(f"✅ Found {len(bookings)} bookings")
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # Test 3: Get available slots
    print("\n⏰ Testing: Get Available Slots")
    try:
        # First get an event type ID
        url = "https://api.cal.com/v2/event-types"
        params = {"user": cal_username}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            event_types = data.get("event_types", [])
            
            if event_types:
                event_type_id = event_types[0].get("id")
                print(f"Using event type ID: {event_type_id}")
                
                # Test slots API
                url = "https://api.cal.com/v2/slots"
                params = {
                    "eventTypeId": event_type_id,
                    "dateFrom": "2024-01-15",
                    "dateTo": "2024-01-15",
                    "duration": 30
                }
                
                response = requests.get(url, headers=headers, params=params)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    slots = data.get("slots", [])
                    print(f"✅ Found {len(slots)} available slots")
                else:
                    print(f"❌ Error: {response.text}")
            else:
                print("⚠️  No event types found to test slots")
        else:
            print(f"❌ Error getting event types: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    print("\n✅ All Cal.com API tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_cal_api()
    if success:
        print("\n🎉 Cal.com API integration is working correctly!")
        print("You can now run the chatbot with: python3 app.py")
    else:
        print("\n❌ There were issues with the Cal.com API integration.")
        print("Please check your API key and username.") 