from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any
import json
import logging
from .configs import GROQ_API_KEY, TAVILY_API_KEY

logger = logging.getLogger(__name__)

@tool
def search_sikkim_attractions(query: str) -> str:
    """Search for attractions and information about Sikkim travel destinations."""
    try:
        if not TAVILY_API_KEY:
            return "Tavily API key not configured. Using fallback information."
        
        search = TavilySearch(
            api_key=TAVILY_API_KEY,
            max_results=5,
            search_depth="basic"
        )
        
        results = search.invoke(query)
        
        # Format results as a readable string
        formatted_results = []
        for result in results:
            title = result.get('title', '')
            content = result.get('content', '')
            if title and content:
                formatted_results.append(f"{title}: {content[:200]}...")
        
        return "\n".join(formatted_results) if formatted_results else "No search results found."
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"Search failed: {str(e)}"

@tool
def generate_detailed_itinerary(preference: str, days: int, search_data: str) -> str:
    """Generate a detailed travel itinerary for Sikkim based on preferences and search data."""
    try:
        if not GROQ_API_KEY:
            return json.dumps({"error": "GROQ API key not configured"})
        
        llm = ChatGroq(
            model_name="llama3-70b-8192",
            api_key=GROQ_API_KEY,
            temperature=0.7
        )
        
        prompt = f"""
        You are an expert Sikkim travel planner. Create a detailed {days}-day itinerary based on the preference: {preference}.
        
        Available information about Sikkim: {search_data}
        
        Create a JSON itinerary with this exact structure:
        [
          {{
            "day": 1,
            "title": "Day 1 - [Theme/Area]",
            "activities": [
              "Activity 1 with timing (e.g., 9:00 AM - Visit Gangtok Mall Road)",
              "Activity 2 with timing",
              "Activity 3 with timing"
            ],
            "location": "Primary location name",
            "description": "Brief description of the day's highlights",
            "accommodation": "Suggested accommodation type"
          }}
        ]
        
        Guidelines:
        - Focus on {preference} activities
        - Include popular Sikkim destinations: Gangtok, Pelling, Lachung, Tsomgo Lake, Rumtek Monastery
        - Consider travel time between locations
        - Include cultural, adventure, and nature activities
        - Provide realistic daily schedules
        - Return ONLY valid JSON, no additional text or explanations
        """
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            # If JSON is invalid, return a fallback
            logger.warning("Invalid JSON generated, using fallback")
            return json.dumps([{
                "day": 1,
                "title": f"Day 1 - {preference.title()} Experience",
                "activities": [
                    "9:00 AM - Arrive in Gangtok",
                    "10:00 AM - Visit MG Marg and local markets",
                    "2:00 PM - Explore Rumtek Monastery",
                    "6:00 PM - Dinner at local restaurant"
                ],
                "location": "Gangtok",
                "description": f"Start your {preference} journey in Sikkim's capital",
                "accommodation": "Hotel in Gangtok"
            }])
    
    except Exception as e:
        logger.error(f"Itinerary generation error: {str(e)}")
        return json.dumps({"error": f"Itinerary generation failed: {str(e)}"})

class TravelAgent:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ API key not configured")
        
        self.llm = ChatGroq(
            model_name="llama3-70b-8192",
            api_key=GROQ_API_KEY,
            temperature=0.7
        )
        
        # Create tools
        self.tools = [search_sikkim_attractions, generate_detailed_itinerary]
        
        # Improved prompt template for richer, valid JSON output
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are an expert travel agent specializing in Sikkim tourism. Your goal is to create personalized, detailed travel itineraries based on user preferences.

Instructions:
[ 
    {{
        "day": 1,
        "title": "Day 1 - Arrival in Gangtok",
        "activities": [
            "9:00 AM - Arrive in Gangtok and check into hotel",
            "11:00 AM - Visit MG Marg and explore local markets",
            "2:00 PM - Visit Rumtek Monastery",
            "6:00 PM - Dinner at local restaurant"
        ],
        "location": "Gangtok",
        "description": "Begin your Sikkim adventure in the capital city.",
        "accommodations": [
            {{ "name": "Mayfair Spa Resort & Casino", "url": "https://www.mayfairhotels.com/mayfair-gangtok/" }},
            {{ "name": "Hotel Sonam Delek", "url": "https://www.sonamdelek.com/" }}
        ]
    }}
]
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def generate_itinerary(self, preference: str, days: int) -> Dict[str, Any]:
        """Generate a travel itinerary using the agent."""
        try:
            # Create the input for the agent
            agent_input = f"""
            Create a {days}-day travel itinerary for Sikkim based on this preference: {preference}
            
            Please:
            1. Search for relevant attractions and information about Sikkim
            2. Generate a detailed itinerary with daily activities, locations, and descriptions
            3. Return the final itinerary as JSON
            """
            
            # Execute the agent
            result = self.agent_executor.invoke({
                "input": agent_input,
                "chat_history": []
            })
            
            # Extract the response
            response_content = result.get("output", "")
            
            # Try to parse JSON from the response, attempt to fix minor issues
            import re
            try:
                # Extract JSON array from response
                match = re.search(r'(\[.*\])', response_content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = response_content.strip()
                # Attempt to fix common issues
                json_str = json_str.replace("\'", '"')
                # Remove trailing commas
                json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                itinerary_data = json.loads(json_str)
                return {
                    "success": True,
                    "itinerary": itinerary_data,
                    "preference": preference,
                    "days": days
                }
            except Exception as e:
                logger.error(f"JSON parsing error: {str(e)} | Raw: {response_content}")
                return {
                    "success": False,
                    "error": f"Invalid JSON format: {str(e)}",
                    "raw_response": response_content
                }
        
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            # Use fallback itinerary when agent fails
            try:
                from .fallback import get_fallback_itinerary
                fallback_itinerary = get_fallback_itinerary(preference, days)
                return {
                    "success": True,
                    "itinerary": fallback_itinerary,
                    "preference": preference,
                    "days": days,
                    "note": "Generated using fallback due to agent error"
                }
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return {
                    "success": False,
                    "error": f"Agent execution failed: {str(e)}"
                }

# Create a global instance
travel_agent = None

def get_travel_agent() -> TravelAgent:
    """Get or create the travel agent instance."""
    global travel_agent
    if travel_agent is None:
        travel_agent = TravelAgent()
    return travel_agent
