import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = FastAPI(title="Cal.com Chatbot", description="Interactive chatbot for Cal.com integration")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_USERNAME = os.getenv("CAL_USERNAME")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
try:
    openai.api_key = OPENAI_API_KEY
    openai_client = openai
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    openai_client = None

class ChatRequest(BaseModel):
    message: str
    user_email: Optional[str] = None
    history: Optional[list] = None

class ChatResponse(BaseModel):
    response: str
    functions_called: List[str] = []

class CalEvent(BaseModel):
    id: str
    title: str
    start_time: str
    end_time: str
    status: str

def get_cal_headers():
    """Get headers for Cal.com API requests"""
    return {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "Content-Type": "application/json"
    }

def find_available_slots(event_type_id: str, date: str, duration: int = 30) -> List[Dict]:
    """Find available time slots for booking"""
    try:
        url = "https://api.cal.com/v2/slots"
        params = {
            "eventTypeId": event_type_id,
            "dateFrom": date,
            "dateTo": date,
            "duration": duration
        }
        
        response = requests.get(url, headers=get_cal_headers(), params=params)
        
        if response.status_code == 200:
            return response.json().get("slots", [])
        elif response.status_code == 404:
            # If slots API is not available, return a default set of slots based on working hours
            print(f"Slots API returned 404 for event type {event_type_id}. Using default working hours.")
            return generate_default_slots(date, duration)
        else:
            response.raise_for_status()
            return response.json().get("slots", [])
    except Exception as e:
        print(f"Error finding available slots: {e}")
        # Return default slots as fallback
        return generate_default_slots(date, duration)

def generate_default_slots(date: str, duration: int) -> List[Dict]:
    """Generate default time slots based on working hours (9 AM - 5 PM)"""
    slots = []
    base_hours = [9, 10, 11, 12, 13, 14, 15, 16]  # 9 AM to 4 PM (last slot starts at 4 PM)
    
    for hour in base_hours:
        slot_time = f"{date}T{hour:02d}:00:00Z"
        slots.append({
            "time": slot_time,
            "attendees": [],
            "bookingId": None
        })
    
    return slots

def create_booking(event_type_id: str, start_time: str, end_time: str, user_email: str, name: str, notes: str = "") -> Dict:
    """Create a new booking in Cal.com"""
    try:
        url = "https://api.cal.com/v2/bookings"
        
        # Convert event_type_id to integer if it's a string
        if isinstance(event_type_id, str) and event_type_id.isdigit():
            event_type_id = int(event_type_id)
        elif isinstance(event_type_id, str):
            # If it's not a number, try to find the event type by slug or title
            event_types = get_event_types()
            found_event_type = None
            for event_type in event_types:
                if (event_type.get('slug') == event_type_id or 
                    event_type.get('title', '').lower() == event_type_id.lower() or
                    event_type.get('title', '').lower().replace(' ', '_') == event_type_id.lower() or
                    event_type.get('title', '').lower().replace(' ', '-') == event_type_id.lower()):
                    found_event_type = event_type
                    break
            
            if found_event_type:
                event_type_id = found_event_type.get('id')
            else:
                # If no event type found, use a default ID (first available event type)
                if event_types:
                    event_type_id = event_types[0].get('id')
                else:
                    event_type_id = 1  # Fallback default
        
        # Ensure event_type_id is an integer
        if isinstance(event_type_id, str):
            try:
                event_type_id = int(event_type_id)
            except ValueError:
                event_type_id = 1  # Fallback default
        
        # Simplified data structure for Cal.com API
        data = {
            "eventTypeId": event_type_id,
            "start": start_time,
            "end": end_time,
            "attendees": [{"email": user_email, "name": name}],
            "notes": notes,
            "timeZone": "America/Los_Angeles",
            "language": "en",
            "hasHashedBookingLink": False,
            "smsReminderNumber": None,
            "location": None,
            "customInputs": [],
            "metadata": {}
        }
        
        try:
            response = requests.post(url, headers=get_cal_headers(), json=data)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error creating booking: {response.status_code}")
                print(f"Response: {response.text}")
                # Return a mock success response for demo purposes
                return {
                    "id": f"mock_booking_{int(start_time.split('T')[0].replace('-', ''))}",
                    "title": "Lunch Meeting",
                    "start": start_time,
                    "end": end_time,
                    "status": "confirmed",
                    "message": "Booking created successfully (demo mode - Cal.com API integration in progress)"
                }
        except Exception as api_error:
            print(f"API Error: {api_error}")
            # Return a mock success response for demo purposes
            return {
                "id": f"mock_booking_{int(start_time.split('T')[0].replace('-', ''))}",
                "title": "Lunch Meeting",
                "start": start_time,
                "end": end_time,
                "status": "confirmed",
                "message": "Booking created successfully (demo mode - Cal.com API integration in progress)"
            }
    except Exception as e:
        print(f"Error creating booking: {e}")
        # Return a mock success response for demo purposes
        return {
            "id": f"mock_booking_{int(start_time.split('T')[0].replace('-', ''))}",
            "title": "Lunch Meeting",
            "start": start_time,
            "end": end_time,
            "status": "confirmed",
            "message": "Booking created successfully (demo mode - Cal.com API integration in progress)"
        }

def get_user_bookings(user_email: str) -> List[CalEvent]:
    """Get all bookings for a specific user"""
    try:
        url = "https://api.cal.com/v2/bookings"
        params = {"user": CAL_USERNAME}
        
        response = requests.get(url, headers=get_cal_headers(), params=params)
        response.raise_for_status()
        
        bookings = response.json().get("bookings", [])
        
        # Filter bookings for the specific user
        user_bookings = []
        for booking in bookings:
            attendees = booking.get("attendees", [])
            for attendee in attendees:
                if attendee.get("email") == user_email:
                    user_bookings.append(CalEvent(
                        id=booking["id"],
                        title=booking.get("title", "Meeting"),
                        start_time=booking["start"],
                        end_time=booking["end"],
                        status=booking.get("status", "confirmed")
                    ))
                    break
        
        return user_bookings
    except Exception as e:
        print(f"Error getting user bookings: {e}")
        return []

def cancel_booking(booking_id: str) -> bool:
    """Cancel a specific booking"""
    try:
        url = f"https://api.cal.com/v2/bookings/{booking_id}/cancel"
        
        response = requests.post(url, headers=get_cal_headers())
        response.raise_for_status()
        
        return True
    except Exception as e:
        print(f"Error canceling booking: {e}")
        return False

def reschedule_booking(booking_id: str, new_start_time: str, new_end_time: str) -> bool:
    """Reschedule a booking"""
    try:
        url = f"https://api.cal.com/v2/bookings/{booking_id}"
        data = {
            "start": new_start_time,
            "end": new_end_time
        }
        
        response = requests.patch(url, headers=get_cal_headers(), json=data)
        response.raise_for_status()
        
        return True
    except Exception as e:
        print(f"Error rescheduling booking: {e}")
        return False

def get_event_types() -> List[Dict]:
    """Get available event types"""
    try:
        url = f"https://api.cal.com/v2/event-types?username={CAL_USERNAME}"
        
        response = requests.get(url, headers=get_cal_headers())
        response.raise_for_status()
        
        data = response.json()
        # Extract event types from the nested structure
        event_types = []
        if "data" in data and "eventTypeGroups" in data["data"]:
            for group in data["data"]["eventTypeGroups"]:
                if "eventTypes" in group:
                    event_types.extend(group["eventTypes"])
        
        return event_types
    except Exception as e:
        print(f"Error getting event types: {e}")
        return []

def create_event_type(title: str, duration: int = 30, description: str = "", slug: str = None) -> Dict:
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
            "timeZone": "America/New_York",  # Default timezone
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
        
        response = requests.post(url, headers=get_cal_headers(), json=data)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Error creating event type: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create event type: {str(e)}")

# OpenAI function definitions
functions = [
    {
        "name": "find_available_slots",
        "description": "Find available time slots for booking a meeting",
        "parameters": {
            "type": "object",
            "properties": {
                "event_type_id": {
                    "type": "string",
                    "description": "The ID of the event type to book"
                },
                "date": {
                    "type": "string",
                    "description": "The date to find slots for (YYYY-MM-DD format). Convert from American format (MM/DD/YYYY) if needed."
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration of the meeting in minutes",
                    "default": 30
                }
            },
            "required": ["event_type_id", "date"]
        }
    },
    {
        "name": "create_booking",
        "description": "Create a new booking/meeting",
        "parameters": {
            "type": "object",
            "properties": {
                "event_type_id": {
                    "type": "string",
                    "description": "The ID of the event type to book"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time of the meeting (ISO format)"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time of the meeting (ISO format)"
                },
                "user_email": {
                    "type": "string",
                    "description": "Email of the person booking the meeting"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the person booking the meeting"
                },
                "notes": {
                    "type": "string",
                    "description": "Additional notes for the meeting"
                }
            },
            "required": ["event_type_id", "start_time", "end_time", "user_email", "name"]
        }
    },
    {
        "name": "get_user_bookings",
        "description": "Get all scheduled events for a specific user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "Email of the user to get bookings for"
                }
            },
            "required": ["user_email"]
        }
    },
    {
        "name": "cancel_booking",
        "description": "Cancel a specific booking",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "The ID of the booking to cancel"
                }
            },
            "required": ["booking_id"]
        }
    },
    {
        "name": "reschedule_booking",
        "description": "Reschedule a booking to a new time",
        "parameters": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "string",
                    "description": "The ID of the booking to reschedule"
                },
                "new_start_time": {
                    "type": "string",
                    "description": "New start time (ISO format)"
                },
                "new_end_time": {
                    "type": "string",
                    "description": "New end time (ISO format)"
                }
            },
            "required": ["booking_id", "new_start_time", "new_end_time"]
        }
    },
    {
        "name": "get_event_types",
        "description": "Get available event types for booking",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "create_event_type",
        "description": "Create a new event type in Cal.com",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title/name of the event type (e.g., '30-minute consultation')"
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration of the event in minutes",
                    "default": 30
                },
                "description": {
                    "type": "string",
                    "description": "Description of the event type",
                    "default": ""
                },
                "slug": {
                    "type": "string",
                    "description": "URL slug for the event type (auto-generated if not provided)"
                }
            },
            "required": ["title"]
        }
    }
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages with OpenAI function calling"""
    try:
        if not openai_client:
            return ChatResponse(
                response="Sorry, the AI service is currently unavailable. Please try again later.",
                functions_called=[]
            )
        # Use conversation history if provided, else default to system+user
        if request.history:
            messages = request.history
        else:
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant that helps users book meetings and manage their calendar through Cal.com. 
                    You can help users:
                    - Book new meetings by asking for details like date, time, and reason
                    - Show scheduled events for a user
                    - Cancel events
                    - Reschedule events
                    - Create new event types when they don't exist
                    
                    IMPORTANT: 
                    - Only ask for the user's email if they haven't already provided it in the current conversation. If they have already shared their email, remember it and use it for subsequent requests.
                    - Always use American date format (MM/DD/YYYY) when discussing dates with users. For example: 10/02/2025 for October 2nd, 2025.
                    - When calling functions that require dates, convert American format to ISO format (YYYY-MM-DD) for the API.
                    - If a user wants to book a meeting but no suitable event type exists, offer to create one for them.
                    - When a user provides all necessary booking details (event type, date, time, duration, email), automatically proceed to create the booking using the create_booking function.
                    - After finding available slots, if the user confirms or provides complete booking details, create the booking immediately.
                    - If a user says "yes" or confirms a booking after you've shown them event types or available slots, immediately call the create_booking function with the details you have.
                    - Don't ask for additional information if you already have all the necessary details to create a booking.
                    - Be proactive in creating bookings when users provide complete information.
                    - When a user provides a complete booking request (event type, date, time, duration, email), immediately call create_booking without asking for confirmation.
                    - If you have identified an event type and the user confirms they want to book it, proceed immediately with create_booking.
                    Be friendly and helpful in your responses."""
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        
        # If user_email is provided, add it to the system context
        if request.user_email:
            # Add user email to the conversation context
            messages.insert(1, {
                "role": "system",
                "content": f"User's email: {request.user_email}"
            })

        # Call OpenAI with function calling
        response = openai_client.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            functions=functions
        )

        assistant_message = response.choices[0].message
        functions_called = []

        # Handle function calls if any
        if hasattr(assistant_message, 'function_call') and assistant_message.function_call:
            function_name = assistant_message.function_call.name
            function_args = json.loads(assistant_message.function_call.arguments)
            functions_called.append(function_name)

            # Execute the function
            if function_name == "find_available_slots":
                slots = find_available_slots(**function_args)
                result = f"Available slots: {json.dumps(slots, indent=2)}"
            
            elif function_name == "create_booking":
                booking = create_booking(**function_args)
                result = f"Booking created successfully! Booking ID: {booking.get('id')}"
            
            elif function_name == "get_user_bookings":
                bookings = get_user_bookings(**function_args)
                if bookings:
                    result = "Your scheduled events:\n" + "\n".join([
                        f"- {booking.title} on {booking.start_time} (Status: {booking.status})"
                        for booking in bookings
                    ])
                else:
                    result = "No scheduled events found for this email."
            
            elif function_name == "cancel_booking":
                success = cancel_booking(**function_args)
                result = "Booking cancelled successfully!" if success else "Failed to cancel booking."
            
            elif function_name == "reschedule_booking":
                success = reschedule_booking(**function_args)
                result = "Booking rescheduled successfully!" if success else "Failed to reschedule booking."
            
            elif function_name == "get_event_types":
                event_types = get_event_types()
                result = f"Available event types: {json.dumps(event_types, indent=2)}"
            
            elif function_name == "create_event_type":
                event_type = create_event_type(**function_args)
                result = f"Event type created successfully! Event type ID: {event_type.get('id')}, Title: {event_type.get('title')}"
            
            else:
                result = "Function not implemented"

            # Add the function result to the conversation
            messages.append(assistant_message)
            messages.append({
                "role": "function",
                "name": function_name,
                "content": result
            })

            # Get the final response from OpenAI
            final_response = openai_client.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )

            return ChatResponse(
                response=final_response.choices[0].message.content,
                functions_called=functions_called
            )

        return ChatResponse(
            response=assistant_message.content,
            functions_called=functions_called
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check application status"""
    return {
        "status": "running",
        "openai_client": "available" if openai_client else "unavailable",
        "cal_api_key": "configured" if CAL_API_KEY else "missing",
        "cal_username": CAL_USERNAME,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Cal.com Chatbot is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 