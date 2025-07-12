import asyncio

from google.adk.sessions import InMemorySessionService
from google.adk.agents import ParallelAgent
from google.adk.runners import Runner
from agents.crisis_supervisor import crisis_supervisor
from agents.commentator import LiveCommentator

from google.genai.types import Content, Part


async def hackathon_demo():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="CRISIS_AI_TRANSPARENCY",
        user_id="PUBLIC_OBSERVER",
        session_id="WILDFIRE_DEMO_2024"
    )

    root = ParallelAgent(
        name="CrisisResponseSystem",
        sub_agents=[crisis_supervisor, LiveCommentator()]
    )

    runner = Runner(agent=root, app_name="CRISIS_AI_TRANSPARENCY", session_service=session_service)

    # Simulate incoming crisis report
    crisis_alert = Content(
        role="user",
        parts=[Part(
            text="URGENT: Wildfire detected near residential area in Santa Rosa, CA. Wind speeds increasing. Immediate response required.")]
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
        # Real-time transparency logging
        print(f"[TRANSPARENCY LOG] {event}")
