"""
Fallback itinerary generator for when the agent fails
"""
import json
from typing import List, Dict, Any

def get_fallback_itinerary(preference: str, days: int) -> List[Dict[str, Any]]:
    """Generate a fallback itinerary when the agent fails"""
    
    # Base activities for different preferences
    preference_activities = {
        "culture": [
            "Visit Rumtek Monastery - Buddhist architecture and culture",
            "Explore MG Marg - Local markets and street food",
            "Tour Enchey Monastery - Traditional Sikkimese culture",
            "Visit Namgyal Institute of Tibetology - Tibetan artifacts",
            "Experience local tea ceremony"
        ],
        "adventure": [
            "Trek to Dzongri - Mountain hiking",
            "River rafting on Teesta River",
            "Paragliding at Gangtok",
            "Mountain biking in Pelling",
            "Rock climbing at various locations"
        ],
        "nature": [
            "Visit Tsomgo Lake - High altitude lake",
            "Explore Yumthang Valley - Flower valley",
            "Trek to Kanchenjunga Base Camp",
            "Visit Gurudongmar Lake",
            "Explore Rhododendron Sanctuary"
        ],
        "spiritual": [
            "Meditation at Rumtek Monastery",
            "Visit Pemayangtse Monastery",
            "Attend prayer ceremonies",
            "Visit Tashiding Monastery",
            "Experience spiritual retreat"
        ]
    }
    
    # Default to culture if preference not found
    activities = preference_activities.get(preference.lower(), preference_activities["culture"])
    
    # Generate daily itineraries
    itinerary = []
    for day in range(1, days + 1):
        # Select activities for this day (cycle through available activities)
        day_activities = []
        for i in range(4):  # 4 activities per day
            activity_idx = (day - 1 + i) % len(activities)
            time_slot = ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"][i]
            day_activities.append(f"{time_slot} - {activities[activity_idx]}")
        
        # Add accommodation and meal times
        day_activities.extend([
            "6:00 PM - Dinner at local restaurant",
            "8:00 PM - Rest and prepare for next day"
        ])
        
        # Determine location based on day
        locations = ["Gangtok", "Pelling", "Lachung", "Namchi", "Ravangla"]
        location = locations[(day - 1) % len(locations)]
        
        itinerary.append({
            "day": day,
            "title": f"Day {day} - {preference.title()} Experience in {location}",
            "activities": day_activities,
            "location": location,
            "description": f"Explore {location} with focus on {preference} activities and experiences.",
            "accommodation": f"Hotel in {location}"
        })
    
    return itinerary

def get_sample_itinerary(preference: str, days: int) -> str:
    """Get a sample itinerary as JSON string"""
    itinerary = get_fallback_itinerary(preference, days)
    return json.dumps(itinerary, indent=2)



