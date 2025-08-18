import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate API keys
def validate_api_keys():
    """Validate that required API keys are present"""
    missing_keys = []
    
    if not TAVILY_API_KEY:
        missing_keys.append("TAVILY_API_KEY")
    
    if not GROQ_API_KEY:
        missing_keys.append("GROQ_API_KEY")
    
    if missing_keys:
        logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    
    return True

# App configuration
APP_CONFIG = {
    "title": "Sikkim Travel Itinerary API",
    "description": "AI-powered travel itinerary generator for Sikkim",
    "version": "1.0.0",
    "debug": os.getenv("DEBUG", "False").lower() == "true"
}