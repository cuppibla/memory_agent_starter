import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to sys.path to ensure we can import agent.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from google.adk.agents import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import Session, DatabaseSessionService
from agent import root_agent

# TODO: Configuration for Persistent Sessions
# Note: DatabaseSessionService requires an async driver URL (e.g., "sqlite+aiosqlite:///...")

# --- A Helper Function to Run Our Agents ---
async def run_agent_query(agent: Agent, query: str, session: Session, user_id: str, session_service: DatabaseSessionService, is_router: bool = False):
    """Initializes a runner and executes a query for a given agent and session."""
    print(f"\n🚀 Running query for agent: '{agent.name}' in session: '{session.id}'...")

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=agent.name
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=types.Content(parts=[types.Part(text=query)], role="user")
        ):
            if not is_router:
                # Let's see what the agent is thinking!
                # print(f"EVENT: {event}")
                pass
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text or ""
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if not is_router:
        print("\n" + "-"*50)
        print("✅ Final Response:")
        print(final_response)
        print("-"*50 + "\n")

    return final_response

async def main():
    # REPLACE ME: Create a database session service
    
    # --- Test Case 1: New Session ---
    print("\n" + "="*50)
    print("TEST CASE 1: New Session (Setting Context)")
    print("="*50)
    
    session_id = "my_persistent_trip" 
    
    # Ensure we start fresh for this test by creating a new session if needed, 
    # or just using the existing one but acknowledging we are 'starting' a flow.
    # In a real app, you might generate a random UUID for a truly new session.
    
    # Get or create session
    session = await session_service.get_session(
        app_name=root_agent.name, user_id="user_01", session_id=session_id
    )
    if not session:
        session = await session_service.create_session(
            app_name=root_agent.name, user_id="user_01", session_id=session_id
        )
        print(f"Created new session: {session_id}")
    else:
        print(f"Resumed existing session: {session_id}")

    # Turn 1: Tell the agent something about ourselves
    query_1 = "Hi! I'm planning a trip to Tokyo. I love ramen and I'm a vegetarian."
    await run_agent_query(root_agent, query_1, session, "user_01", session_service)

    # --- Test Case 2: Resume Session ---
    print("\n" + "="*50)
    print("TEST CASE 2: Resume Session (Verifying Memory)")
    print("="*50)
    
    # Simulate a break in conversation or a new request coming in later
    # We re-fetch the session to prove persistence works (though in this script it's the same object, 
    # the service abstraction handles the DB sync).
    
    session_resumed = await session_service.get_session(
        app_name=root_agent.name, user_id="user_01", session_id=session_id
    )
    
    # Turn 2: Ask for a recommendation that requires remembering Turn 1
    query_2 = "Where should I go for dinner?"
    await run_agent_query(root_agent, query_2, session_resumed, "user_01", session_service)

    # --- Test Case 3: Cross-Session Retrieval ---
    print("\n" + "="*50)
    print("TEST CASE 3: Cross-Session Retrieval (Manual Context Injection)")
    print("="*50)
    
    # Scenario: User starts a completely NEW trip (new session ID) but wants to reference 
    # preferences from the previous trip ("my_persistent_trip").
    
    new_session_id = "my_second_trip"
    print(f"Starting NEW session: {new_session_id}")
    
    # TODO: retrieve the previous session manually
    
    # 2. Extract relevant info (naive approach: get all user/model turns)
    # In a real app, you might use an LLM to summarize this, or filter for specific 'preferences'.
    previous_context = ""
    if old_session and old_session.events:
        print(f"Found {len(old_session.events)} events in old session.")
        previous_context = "PREVIOUS TRIP CONTEXT:\n"
        for event in old_session.events:
            # Assuming event structure has 'role' and 'parts' (standard GenAI types)
            # We need to be careful with the structure. Let's just dump the text.
            # The 'event' in session.events is likely a Turn or similar object.
            # Let's inspect it or just try to access standard attributes.
            # Based on standard ADK, it might be a Pydantic model with 'role' and 'parts'.
            # Let's try to stringify it safely.
            try:
                role = getattr(event, 'author', None) or getattr(getattr(event, 'content', None), 'role', None) or getattr(event, 'role', 'unknown')
                text = ""
                if getattr(event, 'parts', None):
                    text = " ".join([p.text for p in event.parts if getattr(p, 'text', None)])
                elif getattr(event, 'content', None) and getattr(event.content, 'parts', None):
                    text = " ".join([p.text for p in event.content.parts if getattr(p, 'text', None)])
                
                if text:
                    # TODO: Extract content from the OLD session
                    pass

            except Exception as e:
                print(f"Error parsing event: {e}")

    print(f"Extracted Context:\n{previous_context}")

    # 3. Create the NEW session (delete first if left over from a previous run)
    existing_new_session = await session_service.get_session(
        app_name=root_agent.name, user_id="user_01", session_id=new_session_id
    )
    if existing_new_session:
        await session_service.delete_session(
            app_name=root_agent.name, user_id="user_01", session_id=new_session_id
        )
    new_session = await session_service.create_session(
        app_name=root_agent.name, user_id="user_01", session_id=new_session_id
    )
    
    # 4. Inject the context into the FIRST query of the new session
    # We explicitly tell the agent: "Here is what we know from a past trip..."
    # TODO: Manually inject the context to the query
    
    
    await run_agent_query(root_agent, query_3, new_session, "user_01", session_service)
    await session_service.close()

if __name__ == "__main__":
    asyncio.run(main())