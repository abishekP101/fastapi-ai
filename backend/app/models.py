from pydantic import BaseModel, Field, validator
from typing import List, Optional

class TravelState(BaseModel):
    preference: str
    days: int
    search_results: str = ""
    filtered_results: List[str] = []
    itinerary_json: str = ""

class ItineraryRequest(BaseModel):
    preference: str = Field(..., min_length=1, max_length=500, description="Travel preferences (e.g., adventure, culture, nature)")
    days: int = Field(..., ge=1, le=30, description="Number of days for the trip (1-30)")
    
    @validator('preference')
    def validate_preference(cls, v):
        if not v or not v.strip():
            raise ValueError('Preference cannot be empty')
        return v.strip()
    
    @validator('days')
    def validate_days(cls, v):
        if v < 1 or v > 30:
            raise ValueError('Days must be between 1 and 30')
        return v

class ItineraryResponse(BaseModel):
    success: bool
    itinerary: List[dict]
    preference: str
    days: int
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None



