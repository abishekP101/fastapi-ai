from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from .models import ItineraryRequest, TravelState
from .agent import get_travel_agent
from .configs import GROQ_API_KEY, TAVILY_API_KEY
from .graph import run_graph
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sikkim Travel Itinerary API",
    description="AI-powered travel itinerary generator for Sikkim using LangChain Agent",
    version="2.0.0"
)

# Serve frontend at /ui (LangGraph UI)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sikkim Travel Itinerary API v2.0", "status": "running", "framework": "LangChain Agent"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "api_keys_configured": bool(GROQ_API_KEY and TAVILY_API_KEY)}

@app.get("/debug/api-keys")
def debug_api_keys():
    """Debug endpoint to check API key status"""
    return {
        "groq_api_key": "configured" if GROQ_API_KEY else "missing",
        "tavily_api_key": "configured" if TAVILY_API_KEY else "missing",
        "groq_key_length": len(GROQ_API_KEY) if GROQ_API_KEY else 0,
        "tavily_key_length": len(TAVILY_API_KEY) if TAVILY_API_KEY else 0
    }

@app.post("/test-ai")
async def test_ai():
    """Test endpoint to directly test GROQ AI"""
    try:
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ API key not configured")
        
        from langchain_groq import ChatGroq
        llm = ChatGroq(model_name="llama3-70b-8192", api_key=GROQ_API_KEY, temperature=0.7)
        
        test_prompt = "Create a simple 2-day itinerary for Sikkim focusing on culture. Return only valid JSON."
        response = llm.invoke(test_prompt)
        
        return {
            "success": True,
            "ai_response": response.content,
            "model": "llama3-70b-8192"
        }
    except Exception as e:
        logger.error(f"AI test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI test failed: {str(e)}")

@app.post("/generate-itinerary")
async def generate_itinerary(req: ItineraryRequest):
    try:
        # Validate API keys
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ API key not configured")
        if not TAVILY_API_KEY:
            raise HTTPException(status_code=500, detail="Tavily API key not configured")
        
        # Validate input
        if req.days <= 0 or req.days > 30:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
        
        if not req.preference or len(req.preference.strip()) == 0:
            raise HTTPException(status_code=400, detail="Preference cannot be empty")
        
        logger.info(f"Generating itinerary for {req.days} days with preference: {req.preference}")
        
        # Get the travel agent and generate itinerary
        try:
            travel_agent = get_travel_agent()
            result = travel_agent.generate_itinerary(req.preference, req.days)
            
            if result.get("success"):
                return {
                    "success": True,
                    "itinerary": result["itinerary"],
                    "preference": req.preference,
                    "days": req.days,
                    "framework": "LangChain Agent"
                }
            else:
                # If agent failed, provide detailed error
                error_msg = result.get("error", "Unknown error occurred")
                logger.error(f"Agent failed: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Agent failed: {error_msg}")
                
        except ValueError as ve:
            # Configuration errors
            logger.error(f"Configuration error: {str(ve)}")
            raise HTTPException(status_code=500, detail=f"Configuration error: {str(ve)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}")
        # Provide more specific error messages
        if "validation error" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
        elif "api key" in str(e).lower():
            raise HTTPException(status_code=500, detail="API key configuration error")
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/test-agent")
async def test_agent():
    """Test endpoint to verify the agent is working"""
    try:
        if not GROQ_API_KEY or not TAVILY_API_KEY:
            raise HTTPException(status_code=500, detail="API keys not configured")
        
        travel_agent = get_travel_agent()
        result = travel_agent.generate_itinerary("culture", 2)
        
        return {
            "success": True,
            "agent_test": result,
            "message": "Agent is working correctly"
        }
    except Exception as e:
        logger.error(f"Agent test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent test failed: {str(e)}")

@app.post("/graph/generate")
def graph_generate(req: ItineraryRequest):
    """Run LangGraph pipeline: itinerary -> accommodations -> combined JSON"""
    try:
        if not TAVILY_API_KEY:
            raise HTTPException(status_code=500, detail="Tavily API key not configured")
        return run_graph(req.preference, req.days)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Graph generation failed: {str(e)}")
