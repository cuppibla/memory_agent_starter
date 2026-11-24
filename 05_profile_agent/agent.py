from dotenv import load_dotenv
from google.adk.agents import LlmAgent
# REPLACE ME: Add tools import (use try/except ImportError for .tools vs tools so both `adk web` and `main.py` work)

load_dotenv()

# Setup the DB when the agent module is loaded
setup_user_db()

root_agent = LlmAgent(
    name="profile_planner",
    model="gemini-3.5-flash",
    # REPLACE ME: Add tools to root agent
    instruction="""
    You are a hyper-personalized Master Trip Planner.
    1. RECALL FIRST: Before planning, your first action MUST be to call `recall_user_preferences` to learn about the user.
    2. PERSONALIZE: Use any recalled preferences (like dietary needs) to tailor your suggestions.
    3. LEARN: If a user states a new, long-term preference, your final action MUST be to use `save_user_preferences` to remember it.
    """,
)