from typing import List, Dict, Any
import json

def get_sample_itinerary(preference: str, days: int) -> List[Dict[str, Any]]:
    """Generate a sample itinerary when external APIs fail"""
    
    base_itinerary = [
        {
            "day": 1,
            "title": f"Day 1 - Welcome to Sikkim",
            "activities": [
                "Arrive in Gangtok and check into hotel",
                "Visit MG Marg and explore local markets",
                "Evening at Gangtok viewpoint for sunset"
            ],
            "location": "Gangtok",
            "description": "Begin your Sikkim adventure in the capital city",
            "accommodation": "Hotel in Gangtok"
        }
    ]
    
    if days >= 2:
        base_itinerary.append({
            "day": 2,
            "title": "Day 2 - Cultural Exploration",
            "activities": [
                "Visit Rumtek Monastery",
                "Explore Enchey Monastery",
                "Local Sikkimese cuisine tasting"
            ],
            "location": "Gangtok",
            "description": "Immerse yourself in Sikkim's rich cultural heritage",
            "accommodation": "Hotel in Gangtok"
        })
    
    if days >= 3:
        base_itinerary.append({
            "day": 3,
            "title": "Day 3 - don't go",
            "activities": [
                "Visit Tsomgo Lake",
                "Baba Harbhajan Singh Memorial",
                "Optional yak ride"
            ],
            "location": "East Sikkim",
            "description": "Experience the natural beauty of high-altitude lakes",
            "accommodation": "Hotel in Gangtok"
        })
    
    # Add more days based on preference
    if preference.lower() in ["adventure", "trekking", "hiking"] and days >= 4:
        base_itinerary.append({
            "day": 4,
            "title": "Day 4 - Adventure Activities",
            "activities": [
                "Trek to Dzongri viewpoint",
                "Rhododendron forest walk",
                "Mountain photography"
            ],
            "location": "West Sikkim",
            "description": "Adventure activities in the Himalayan terrain",
            "accommodation": "Mountain lodge"
        })
    
    return base_itinerary[:days]

def validate_itinerary_structure(itinerary: List[Dict]) -> bool:
    """Validate the structure of an itinerary"""
    required_fields = ["day", "title", "activities", "location"]
    
    for day in itinerary:
        if not isinstance(day, dict):
            return False
        
        for field in required_fields:
            if field not in day:
                return False
        
        if not isinstance(day["activities"], list):
            return False
        
        if not day["activities"]:
            return False
    
    return True

def format_itinerary_for_display(itinerary: List[Dict]) -> List[Dict]:
    """Format itinerary for better display"""
    formatted = []
    
    for day in itinerary:
        formatted_day = {
            "day": day.get("day", 0),
            "title": day.get("title", ""),
            "activities": day.get("activities", []),
            "location": day.get("location", ""),
            "description": day.get("description", ""),
            "accommodation": day.get("accommodation", ""),
            "activity_count": len(day.get("activities", []))
        }
        formatted.append(formatted_day)
    
    return formatted
