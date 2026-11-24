# --- Define 3 Specialist Activity Agents ---
from dotenv import load_dotenv

from google.adk.agents import LlmAgent, Agent
from google.adk.tools import google_search

load_dotenv()

museum_agent = LlmAgent(
    name="museum_expert",
    model="gemini-3.5-flash",
    instruction="You are a generic museum expert. When asked, suggest ONE famous museum or cultural site in the requested city. Keep it brief.",
)

restaurant_agent = LlmAgent(
    name="restaurant_expert",
    model="gemini-3.5-flash",
    instruction="You are a foodie. When asked, suggest ONE famous local restaurant or dish in the requested city. Keep it brief.",
)

outdoor_agent = LlmAgent(
    name="outdoor_expert",
    model="gemini-3.5-flash",
    instruction="You are an adventure guide. When asked, suggest ONE outdoor activity or park in the requested city. Keep it brief.",
)

print("✅ Specialist agents are ready to plan!")

from typing import Dict, Any, Optional
from google.adk.tools import ToolContext

# TODO: Implement call back logic

def get_planner_instruction(context: ToolContext) -> str:
    """
    Dynamic instruction that safely retrieves state, defaulting to 'None' if missing.
    """
    # context is likely a ReadonlyContext which wraps the actual context
    # We need to access .state from it.
    
    last_activity = "None"
    if context and hasattr(context, "state") and context.state:
        last_activity = context.state.get("last_activity_type", "None")
    
    return f"""
        You are a Master Trip Planner dedicated to creating varied, balanced itineraries.

        ### CRITICAL STATE INFORMATION
        The last activity type you planned was: {last_activity}
        (If it says 'None', you are free to choose any activity).

        ### YOUR STRICT RULES
        1. You **MUST** delegate every request to one of your 3 specialists. NEVER answer directly.
        2. **VARIETY IS MANDATORY:** You are FORBIDDEN from using the same specialist twice in a row.
           - If last_activity_type is 'CULTURAL' -> `museum_expert` is BANNED for this turn.
           - If last_activity_type is 'FOOD' -> `restaurant_expert` is BANNED for this turn.
           - If last_activity_type is 'OUTDOOR' -> `outdoor_expert` is BANNED for this turn.
        3. If the user asks for something that fits a banned specialist (e.g., asking for a hike when OUTDOOR is banned), you MUST politely refuse and suggest a DIFFERENT available type of activity instead.
        4. **CRITICAL:** You must only transfer to ONE agent at a time. Do NOT attempt to call multiple tools or transfer to multiple agents in a single turn.
    """


root_agent = LlmAgent(
    name="master_trip_planner",
    model="gemini-3.5-flash",
    instruction=get_planner_instruction,
    sub_agents=[museum_agent, restaurant_agent, outdoor_agent],
    # TODO: add callback to root agent
    
)
print("🎩 The Master Planner is ready.")
