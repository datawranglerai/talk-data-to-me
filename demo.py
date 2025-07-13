import asyncio

from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.agents import ParallelAgent
from google.adk.runners import Runner
from google.genai.types import Content, Part

from crisis_response_agent.agent import crisis_supervisor
from commentator_agent.commentator import LiveCommentator


SESSION_ID = "WILDFIRE_DEMO_2025"
USER_ID = "PUBLIC_OBSERVER"
APP_NAME = "CRISIS_AI_TRANSPARENCY"


async def hackathon_demo():
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    root = ParallelAgent(
        name="CrisisResponseSystem",
        sub_agents=[
            crisis_supervisor,
            LiveCommentator()
        ]
    )

    runner = Runner(
        agent=root,
        app_name="CRISIS_AI_TRANSPARENCY",
        session_service=session_service,
        memory_service=memory_service
    )

    # Simulate incoming crisis report
    crisis_alert = Content(
        role="user",
        parts=[Part(text="""Please analyze this crisis situation and create a comprehensive response plan:
    
        URGENT CRISIS: Wildfire detected near Santa Rosa, CA...
    
        I need you to plan your approach step by step, coordinate with all available specialist teams, and provide a final comprehensive response plan.""")]
    )

    print("🚨 LIVE CRISIS AI TRANSPARENCY DEMO 🚨")
    print("=" * 50)
    print("🎭 AI Decision-Making Theatre: Every AI decision explained in real-time")
    print("🔍 Public Oversight: Democratizing AI crisis response cognition")
    print("📢 Live Commentary: Making AI transparent and accountable")
    print("=" * 50)

    async for event in runner.run_async(
            user_id="PUBLIC_OBSERVER",
            session_id="WILDFIRE_DEMO_2025",
            new_message=crisis_alert
    ):
        event_str = str(event)

        # Real-time transparency logging
        print(f"[TRANSPARENCY LOG] {event}")

        # Look for planning phases
        if "PLANNING" in event_str or "planning" in event_str:
            print(f"🧠 [PLANNING] {event}")
        elif "ACTION" in event_str or "action" in event_str:
            print(f"⚡ [ACTION] {event}")
        elif "REASONING" in event_str or "reasoning" in event_str:
            print(f"🔍 [REASONING] {event}")
        elif "FINAL_ANSWER" in event_str:
            print(f"📋 [FINAL PLAN] {event}")
        elif "transfer_to_agent" in event_str:
            print(f"🔄 [AGENT TRANSFER] {event}")
        elif "function_call" in event_str:
            print(f"🛠️ [TOOL CALL] {event}")
        else:
            print(f"📡 [SYSTEM] {event}")


if __name__ == '__main__':
    asyncio.run(hackathon_demo())
