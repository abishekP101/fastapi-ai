# Sikkim Travel Itinerary API v2.0

An AI-powered travel itinerary generator for Sikkim, India. This API uses LangChain Agent and Groq to create personalized travel plans based on user preferences.

## Features

- 🤖 LangChain Agent-powered itinerary generation
- 🔍 Real-time search for Sikkim attractions using Tavily
- 🎯 Personalized recommendations based on preferences
- 🛡️ Robust error handling and fallback mechanisms
- 📚 Comprehensive API documentation
- 🔒 Input validation and sanitization
- 🚀 Simplified architecture with better reliability

## Prerequisites

- Python 3.8 or higher
- Groq API key
- Tavily API key

## Installation

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   Create a `.env` file in the backend directory with:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   DEBUG=False
   HOST=0.0.0.0
   PORT=8000
   ```

## Running the Application

### Option 1: Using the startup script
```bash
python run.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using Python module
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
- **GET** `/health`
- Returns the health status and API key configuration

### Test Agent
- **POST** `/test-agent`
- Tests the LangChain agent functionality

### Generate Itinerary
- **POST** `/generate-itinerary`
- **Body:**
  ```json
  {
    "preference": "adventure",
    "days": 5
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "itinerary": [
      {
        "day": 1,
        "title": "Day 1 - Adventure in Gangtok",
        "activities": [
          "9:00 AM - Visit MG Marg and explore local markets",
          "11:00 AM - Visit Rumtek Monastery",
          "2:00 PM - Evening at Gangtok viewpoint",
          "6:00 PM - Dinner at local restaurant"
        ],
        "location": "Gangtok",
        "description": "Begin your Sikkim adventure in the capital city",
        "accommodation": "Hotel in Gangtok"
      }
    ],
    "preference": "adventure",
    "days": 5,
    "framework": "LangChain Agent"
  }
  ```

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # Pydantic models for data validation
│   ├── agent.py         # LangChain Agent for itinerary generation
│   ├── tools.py         # External API tools (Tavily search)
│   ├── configs.py       # Configuration and environment variables
│   ├── utils.py         # Utility functions
│   ├── fallback.py      # Fallback itinerary generator
│   └── itinerary.py     # Itinerary-specific functions
├── requirements.txt     # Python dependencies
├── run.py              # Startup script
└── README.md           # This file
```

## Architecture

The application now uses a **LangChain Agent** approach instead of LangGraph:

1. **Agent Initialization**: Creates a LangChain agent with tools for search and itinerary generation
2. **Tool Integration**: Uses Tavily for real-time search and GROQ for AI-powered itinerary creation
3. **Fallback Mechanism**: Provides sample itineraries when the agent encounters errors
4. **Error Handling**: Comprehensive error handling with detailed logging

## Error Handling

The API includes comprehensive error handling:
- Input validation for all parameters
- API key validation
- Graceful fallback when external services fail
- Detailed error messages for debugging
- Agent error recovery with fallback itineraries

## Development

### Adding New Features
1. Create new functions in the appropriate module
2. Add corresponding tests
3. Update the API documentation
4. Update this README if needed

### Testing
```bash
# Test the API endpoints
curl -X POST "http://localhost:8000/generate-itinerary" \
     -H "Content-Type: application/json" \
     -d '{"preference": "culture", "days": 3}'

# Test the agent
curl -X POST "http://localhost:8000/test-agent"
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you're in the correct directory and have activated the virtual environment.

2. **API Key Errors**: Verify that your `.env` file contains valid API keys.

3. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`.

4. **Port Already in Use**: Change the port in the `.env` file or kill the process using the current port.

5. **Agent Errors**: Check the logs for detailed error messages. The system will fall back to sample itineraries if the agent fails.

### Getting API Keys

- **Groq API Key**: Sign up at [groq.com](https://groq.com)
- **Tavily API Key**: Sign up at [tavily.com](https://tavily.com)

## Migration from LangGraph

This version replaces the LangGraph workflow with a simpler LangChain Agent approach:

- **Removed**: LangGraph dependencies and complex state management
- **Added**: LangChain Agent with tools for search and itinerary generation
- **Improved**: Better error handling and fallback mechanisms
- **Simplified**: Cleaner architecture with fewer dependencies

## License

This project is for educational purposes. Please ensure you comply with the terms of service for all external APIs used.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
