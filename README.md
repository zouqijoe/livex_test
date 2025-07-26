# Cal.com Chatbot with OpenAI Function Calling

## Overview

This is an interactive chatbot that integrates with Cal.com using OpenAI's function calling capabilities. The chatbot allows users to book meetings, view scheduled events, cancel events, and reschedule meetings through a natural language interface.

## Features

✅ **Core Features:**
- Book new meetings with natural language
- View scheduled events for a user
- Cancel events
- Reschedule meetings
- Interactive web interface

✅ **Bonus Features:**
- Modern, responsive web UI
- Real-time chat interface
- Quick action buttons
- Typing indicators
- Error handling and validation

## Project Structure

```
livex_test_job_app/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script for environment variables
├── env.example           # Example environment variables
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface template
└── static/
    ├── css/
    │   └── style.css     # Styling for the web interface
    └── js/
        └── chat.js       # JavaScript for chat functionality
```

## Quick Start

### 1. Setup Environment Variables

Run the setup script to configure your environment:

```bash
python setup.py
```

The script will prompt you for:
- **Cal.com API Key**: Your Cal.com API key (starts with `cal_live_...`)
- **Cal.com Username**: Your Cal.com username

Alternatively, create a `.env` file manually:

```bash
# OpenAI Configuration
OPENAI_API_KEY=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

# Cal.com Configuration
CAL_API_KEY=your_cal_api_key_here
CAL_USERNAME=your_cal_username_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

### 4. Access the Chatbot

Open your browser and navigate to: http://localhost:8000

## Usage Examples

### Booking a Meeting
```
User: "help me to book a meeting"
Bot: "I'd be happy to help you book a meeting! Could you please provide your email address so I can assist you with the booking process?"

User: "my email is john@example.com"
Bot: "Great! I'll help you book a meeting. What type of meeting would you like to schedule? I can show you the available event types."

User: "I need a 30-minute consultation"
Bot: "Perfect! I found some available consultation slots. When would you like to schedule this meeting? I can show you available times for today or tomorrow."
```

### Viewing Scheduled Events
```
User: "show me the scheduled events"
Bot: "I'd be happy to show you your scheduled events! Could you please provide your email address so I can look up your bookings?"

User: "my email is john@example.com"
Bot: "Here are your scheduled events:
- Team Meeting on 2024-01-15T10:00:00Z (Status: confirmed)
- Client Consultation on 2024-01-16T14:30:00Z (Status: confirmed)"
```

### Canceling an Event
```
User: "cancel my event at 3pm today"
Bot: "I'll help you cancel that event. Could you please provide your email address so I can find the specific event you're referring to?"

User: "my email is john@example.com"
Bot: "I found your event scheduled for 3pm today. I've successfully cancelled it for you."
```

## API Endpoints

### Web Interface
- `GET /` - Main chat interface
- `GET /health` - Health check endpoint

### Chat API
- `POST /chat` - Send messages to the chatbot
  - Request body: `{"message": "your message", "user_email": "optional"}`
  - Response: `{"response": "bot response", "functions_called": ["function_names"]}`

## Technical Details

### OpenAI Function Calling

The chatbot uses OpenAI's function calling feature to integrate with Cal.com APIs:

1. **find_available_slots** - Find available time slots for booking
2. **create_booking** - Create a new meeting booking
3. **get_user_bookings** - Retrieve user's scheduled events
4. **cancel_booking** - Cancel a specific booking
5. **reschedule_booking** - Reschedule a booking to a new time
6. **get_event_types** - Get available event types

### Cal.com API Integration

The application integrates with Cal.com's REST API v2:
- Authentication using Bearer tokens
- Booking management (create, read, cancel, update)
- Slot availability checking
- Event type retrieval

### Web Interface Features

- **Real-time Chat**: Instant message sending and receiving
- **Responsive Design**: Works on desktop and mobile devices
- **Quick Actions**: Pre-defined buttons for common tasks
- **Typing Indicators**: Visual feedback during bot processing
- **Error Handling**: Graceful error messages and recovery

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing the API

You can test the API endpoints using curl:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help me to book a meeting"}'
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY environment variable is required"**
   - Make sure your `.env` file exists and contains the OpenAI API key

2. **"Failed to create booking"**
   - Verify your Cal.com API key is correct
   - Ensure your Cal.com username is set correctly
   - Check that the event type ID exists in your Cal.com account

3. **"No scheduled events found"**
   - Verify the email address is correct
   - Check that the user has bookings in your Cal.com account

### Environment Variables

Make sure all required environment variables are set:
- `OPENAI_API_KEY`: Your OpenAI API key
- `CAL_API_KEY`: Your Cal.com API key
- `CAL_USERNAME`: Your Cal.com username

## Security Notes

- Never commit your `.env` file to version control
- The OpenAI API key provided is for testing only
- Use environment variables for all sensitive configuration
- Implement proper authentication for production use

## License

This project is created for the LiveX coding challenge.
