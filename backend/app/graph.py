from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from .configs import GROQ_API_KEY, TAVILY_API_KEY
from .fallback import get_fallback_itinerary
from .tools import get_tavily_tool
import logging
import json
import requests

logger = logging.getLogger(__name__)


class GraphState(TypedDict, total=False):
    preference: str
    days: int
    itinerary: List[Dict[str, Any]]
    accommodations: Dict[str, List[Dict[str, Any]]]
    combined: List[Dict[str, Any]]


def _generate_itinerary(preference: str, days: int) -> List[Dict[str, Any]]:
    if not GROQ_API_KEY:
        return get_fallback_itinerary(preference, days)

    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model_name="llama3-70b-8192", api_key=GROQ_API_KEY, temperature=0.5)
        prompt = f"""
        You are an expert Sikkim travel planner. Create a detailed {days}-day itinerary for preference: {preference}.
        Return ONLY a JSON array with items having fields: day (number), title (string), activities (array of strings), location (string), description (string), accommodation (string).
        Ensure location is a real place name in Sikkim for each day.
        """
        resp = llm.invoke(prompt)
        content = (resp.content or "").strip()
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            logger.warning("Lang model returned invalid JSON; falling back")
        return get_fallback_itinerary(preference, days)
    except Exception as e:
        logger.error(f"Itinerary generation failed: {e}")
        return get_fallback_itinerary(preference, days)


def _search_accommodations_near(location: str, limit: int = 8) -> List[Dict[str, Any]]:
    if not TAVILY_API_KEY:
        return []
    try:
        search = get_tavily_tool()
        query = f"best hotels and homestays near {location} Sikkim India"
        results = search.invoke(query)
        # normalize and dedupe
        candidates: List[Dict[str, Any]] = []
        for r in results[: limit * 2]:
            title = (r.get("title") or "").strip()
            url = (r.get("url") or "").strip()
            name = title.split("|")[0].split("-")[0].strip()
            if len(name) < 3:
                continue
            candidates.append({"name": name, "url": url})
        seen = set()
        uniq: List[Dict[str, Any]] = []
        for c in candidates:
            k = c["name"].lower()
            if k in seen:
                continue
            seen.add(k)
            uniq.append(c)
            if len(uniq) >= limit:
                break

        # geocode via Nominatim
        session = requests.Session()
        session.headers.update({"User-Agent": "fastapi-ai/langgraph/1.0"})
        items: List[Dict[str, Any]] = []
        for c in uniq:
            q = f"{c['name']}, {location}, Sikkim, India"
            try:
                resp = session.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": q, "format": "json", "limit": 1},
                    timeout=10,
                )
                geo = resp.json() if resp.ok else []
                lat = float(geo[0]["lat"]) if geo else None
                lon = float(geo[0]["lon"]) if geo else None
            except Exception:
                lat = None
                lon = None
            items.append({"name": c["name"], "url": c["url"], "lat": lat, "lon": lon})
        return items
    except Exception as e:
        logger.error(f"Accommodation search failed for {location}: {e}")
        return []


def node_generate_itinerary(state: GraphState) -> GraphState:
    preference = state.get("preference", "general")
    days = int(state.get("days", 3))
    itinerary = _generate_itinerary(preference, days)
    return {**state, "itinerary": itinerary}


def node_fetch_accommodations(state: GraphState) -> GraphState:
    itinerary = state.get("itinerary", [])
    accommodations: Dict[str, List[Dict[str, Any]]] = {}
    for day in itinerary:
        location = day.get("location") or "Sikkim"
        items = _search_accommodations_near(location, limit=8)
        accommodations[location] = items
    return {**state, "accommodations": accommodations}


def node_combine(state: GraphState) -> GraphState:
    itinerary = state.get("itinerary", [])
    accommodations = state.get("accommodations", {})
    combined: List[Dict[str, Any]] = []
    for day in itinerary:
        location = day.get("location") or "Sikkim"
        day_acc = accommodations.get(location, [])
        combined.append({**day, "accommodations": day_acc})
    return {**state, "combined": combined}


def build_graph():
    g = StateGraph(GraphState)
    g.add_node("generate_itinerary", node_generate_itinerary)
    g.add_node("fetch_accommodations", node_fetch_accommodations)
    g.add_node("combine", node_combine)

    g.add_edge(START, "generate_itinerary")
    g.add_edge("generate_itinerary", "fetch_accommodations")
    g.add_edge("fetch_accommodations", "combine")
    g.add_edge("combine", END)
    return g.compile()


def run_graph(preference: str, days: int) -> Dict[str, Any]:
    workflow = build_graph()
    initial: GraphState = {"preference": preference, "days": days}
    final: GraphState = workflow.invoke(initial)
    return {
        "success": True,
        "preference": preference,
        "days": days,
        "itinerary": final.get("itinerary", []),
        "accommodations": final.get("accommodations", {}),
        "combined": final.get("combined", []),
        "framework": "LangGraph",
    }


