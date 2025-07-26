#!/usr/bin/env python3
"""
Test script to create event types using the Cal.com API
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

def create_event_type(title: str, duration: int = 30, description: str = "", slug: str = None):
    """Create a new event type in Cal.com"""
    try:
        url = "https://api.cal.com/v2/event-types"
        
        # Generate slug from title if not provided
        if not slug:
            slug = title.lower().replace(" ", "-").replace("_", "-")
            # Remove special characters
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
        
        data = {
            "title": title,
            "length": duration,
            "description": description,
            "slug": slug,
            "hidden": False,
            "hashedLink": None,
            "locations": [],
            "customInputs": [],
            "timeZone": "America/New_York",
            "scheduleId": None,
            "price": 0,
            "currency": "usd",
            "bookingFields": [],
            "useEventTypeDestinationCalendarEmail": False,
            "requiresConfirmation": False,
            "requiresBookerEmailVerification": False,
            "disableGuests": False,
            "hideCalendarNotes": False,
            "minimumBookingNotice": 0,
            "beforeEventBuffer": 0,
            "afterEventBuffer": 0,
            "seatsPerTimeSlot": None,
            "seatsShowAttendees": False,
            "schedulingType": "round_robin",
            "teamId": None,
            "successRedirectUrl": None,
            "bookingLimits": None,
            "durationLimits": None,
            "onlyShowForFirstEvent": False,
            "metadata": {},
            "periodType": "unlimited",
            "periodDays": None,
            "periodStartDate": None,
            "periodEndDate": None,
            "periodCountCalendarDays": False,
            "requiresCalendarIntegration": False,
            "destinationCalendar": None,
            "eventName": "Dynamic",
            "lockTimezones": False,
            "lockTimeZoneToggleOnBookingPage": False
        }
        
        print(f"🔄 Creating event type: {title}")
        print(f"   Duration: {duration} minutes")
        print(f"   Slug: {slug}")
        
        response = requests.post(url, headers=get_cal_headers(), json=data)
        
        if response.status_code == 201:
            event_type = response.json()
            print(f"✅ Successfully created event type!")
            print(f"   ID: {event_type.get('id')}")
            print(f"   Title: {event_type.get('title')}")
            print(f"   Slug: {event_type.get('slug')}")
            return event_type
        else:
            print(f"❌ Failed to create event type: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating event type: {e}")
        return None

def test_create_lunch_meeting():
    """Test creating a lunch meeting event type"""
    print("🍽️  Testing lunch meeting creation...")
    
    event_type = create_event_type(
        title="Business Lunch Meeting",
        duration=60,
        description="A 60-minute business lunch meeting"
    )
    
    if event_type:
        print("✅ Lunch meeting event type created successfully!")
        return event_type
    else:
        print("❌ Failed to create lunch meeting event type")
        return None

def test_create_consultation():
    """Test creating a consultation event type"""
    print("\n💼 Testing consultation creation...")
    
    event_type = create_event_type(
        title="Professional Consultation",
        duration=30,
        description="A 30-minute professional consultation meeting"
    )
    
    if event_type:
        print("✅ Consultation event type created successfully!")
        return event_type
    else:
        print("❌ Failed to create consultation event type")
        return None

def main():
    print("🧪 Event Type Creation Test")
    print("=" * 40)
    
    if not CAL_API_KEY or not CAL_USERNAME:
        print("❌ Missing environment variables:")
        print(f"   CAL_API_KEY: {'✅ Set' if CAL_API_KEY else '❌ Missing'}")
        print(f"   CAL_USERNAME: {'✅ Set' if CAL_USERNAME else '❌ Missing'}")
        return
    
    # Test creating lunch meeting
    lunch_event = test_create_lunch_meeting()
    
    # Test creating consultation
    consultation_event = test_create_consultation()
    
    if lunch_event or consultation_event:
        print("\n🎉 Event types created successfully!")
        print("You can now test the chatbot with these event types.")
        print("\nTry saying in the chatbot:")
        print("- 'I want to book a lunch meeting'")
        print("- 'Book a consultation for tomorrow'")
    else:
        print("\n❌ No event types were created.")
        print("Check your Cal.com API permissions and try again.")

if __name__ == "__main__":
    main() 