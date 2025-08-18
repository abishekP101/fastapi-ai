from langchain_tavily import TavilySearch
from .configs import TAVILY_API_KEY
import logging

logger = logging.getLogger(__name__)

def get_tavily_tool():
    """Get Tavily search tool with error handling"""
    try:
        if not TAVILY_API_KEY:
            raise ValueError("Tavily API key not configured")
        
        return TavilySearch(
            api_key=TAVILY_API_KEY,
            max_results=5,
            search_depth="basic"
        )
    except Exception as e:
        logger.error(f"Error initializing Tavily tool: {str(e)}")
        raise
