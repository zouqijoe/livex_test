#!/usr/bin/env python3
"""
Test script to verify Cal.com API connectivity and event types
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_USERNAME = os.getenv("CAL_USERNAME")

def get_cal_headers():
    """Get headers for Cal.com API requests"""
    return {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "Content-Type": "application/json"
    }

def test_cal_connection():
    """Test basic Cal.com API connection"""
    print("🔗 Testing Cal.com API connection...")
    try:
        # Test with event types endpoint
        url = f"https://api.cal.com/v2/event-types?username={CAL_USERNAME}"
        response = requests.get(url, headers=get_cal_headers())
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection successful!")
            print(f"   Username: {CAL_USERNAME}")
            print(f"   Event types found: {len(data.get('event_types', []))}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_event_types():
    """Test getting event types"""
    print("\n📅 Testing event types...")
    try:
        url = f"https://api.cal.com/v2/event-types?username={CAL_USERNAME}"
        response = requests.get(url, headers=get_cal_headers())
        
        if response.status_code == 200:
            data = response.json()
            # Extract event types from the nested structure
            event_types = []
            if "data" in data and "eventTypeGroups" in data["data"]:
                for group in data["data"]["eventTypeGroups"]:
                    if "eventTypes" in group:
                        event_types.extend(group["eventTypes"])
            
            print(f"✅ Found {len(event_types)} event type(s):")
            
            if event_types:
                for i, event_type in enumerate(event_types, 1):
                    print(f"   {i}. {event_type.get('title', 'N/A')}")
                    print(f"      ID: {event_type.get('id', 'N/A')}")
                    print(f"      Duration: {event_type.get('length', 'N/A')} minutes")
                    print(f"      Slug: {event_type.get('slug', 'N/A')}")
                    print()
                return event_types
            else:
                print("   ⚠️  No event types found!")
                return []
        else:
            print(f"❌ Failed to get event types: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting event types: {e}")
        return []

def test_slots_availability(event_types):
    """Test finding available slots"""
    print("🔍 Testing slot availability...")
    
    if not event_types:
        print("❌ No event types available to test slots")
        return False
    
    # Test with the first event type
    event_type = event_types[0]
    event_id = event_type.get('id')
    event_title = event_type.get('title', 'Unknown')
    
    print(f"   Testing with event type: {event_title} (ID: {event_id})")
    
    try:
        url = "https://api.cal.com/v2/slots"
        params = {
            "eventTypeId": event_id,
            "dateFrom": "2025-10-02",
            "dateTo": "2025-10-02",
            "duration": event_type.get('length', 30)
        }
        
        response = requests.get(url, headers=get_cal_headers(), params=params)
        
        if response.status_code == 200:
            slots = response.json().get('slots', [])
            print(f"✅ Found {len(slots)} available slot(s) for 10/02/2025")
            if slots:
                for slot in slots[:3]:  # Show first 3 slots
                    print(f"   - {slot.get('time', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to get slots: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting slots: {e}")
        return False

def test_booking_creation(event_types):
    """Test booking creation (simulation)"""
    print("\n📝 Testing booking creation...")
    
    if not event_types:
        print("❌ No event types found. Cannot test booking creation.")
        return False
    
    event_type = event_types[0]
    event_id = event_type.get('id')
    event_title = event_type.get('title', 'Unknown')
    
    print(f"   Would test booking with: {event_title} (ID: {event_id})")
    print("   ⚠️  This is a simulation - no actual booking will be created")
    return True

def main():
    print("🧪 Cal.com API Verification Test")
    print("=" * 40)
    
    if not CAL_API_KEY or not CAL_USERNAME:
        print("❌ Missing environment variables:")
        print(f"   CAL_API_KEY: {'✅ Set' if CAL_API_KEY else '❌ Missing'}")
        print(f"   CAL_USERNAME: {'✅ Set' if CAL_USERNAME else '❌ Missing'}")
        return
    
    # Test connection
    if not test_cal_connection():
        print("\n❌ Cannot proceed - API connection failed")
        return
    
    # Test event types
    event_types = test_event_types()
    
    # Test slots if event types exist
    if event_types:
        test_slots_availability(event_types)
        test_booking_creation(event_types)
    else:
        print("\n📋 SETUP REQUIRED:")
        print("You need to create event types in your Cal.com account:")
        print("1. Go to https://cal.com")
        print("2. Click 'Event Types' in the sidebar")
        print("3. Click 'Create' to add a new event type")
        print("4. Configure with:")
        print("   - Title: '30-minute consultation'")
        print("   - Duration: 30 minutes")
        print("   - Set your availability (e.g., 9 AM - 5 PM)")
        print("5. Save the event type")
        print("\nAfter creating event types, run this test again!")

if __name__ == "__main__":
    main() 