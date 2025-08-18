#!/usr/bin/env python3
"""
Startup script for the Sikkim Travel Itinerary API
"""

import uvicorn
import os
from app.configs import validate_api_keys, APP_CONFIG

def main():
    """Main function to start the FastAPI server"""
    
    # Validate API keys
    if not validate_api_keys():
        print("⚠️  Warning: Some API keys are missing. The application may not work properly.")
        print("Please set the following environment variables:")
        print("- TAVILY_API_KEY")
        print("- GROQ_API_KEY") 
        print()
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = APP_CONFIG.get("debug", False)
    
    print(f"🚀 Starting Sikkim Travel Itinerary API...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print()
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
