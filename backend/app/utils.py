import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def validate_json_string(json_str: str) -> bool:
    """Validate if a string is valid JSON"""
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default

def clean_search_results(results: str) -> List[str]:
    """Clean and format search results"""
    if not results:
        return []
    
    # Split by newlines and clean each line
    lines = results.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:  # Filter out very short lines
            cleaned_lines.append(line)
    
    return cleaned_lines[:10]  # Limit to 10 results

def format_itinerary_response(itinerary_data: List[Dict], preference: str, days: int) -> Dict[str, Any]:
    """Format the final itinerary response"""
    return {
        "success": True,
        "itinerary": itinerary_data,
        "preference": preference,
        "days": days,
        "total_activities": sum(len(day.get("activities", [])) for day in itinerary_data),
        "locations": list(set(day.get("location", "") for day in itinerary_data if day.get("location")))
    }

def sanitize_preference(preference: str) -> str:
    """Sanitize user preference input"""
    if not preference:
        return "general"
    
    # Remove special characters and limit length
    sanitized = "".join(c for c in preference if c.isalnum() or c.isspace())
    return sanitized.strip()[:100]  # Limit to 100 characters
