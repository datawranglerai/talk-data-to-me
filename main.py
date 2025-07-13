import asyncio

from google.adk.sessions import InMemorySessionService
from google.adk.agents import ParallelAgent
from google.adk.runners import Runner
from commentator_agent.supervisor import supervisor
from commentator_agent.commentator import LiveCommentator

from google.genai.types import Content, Part

SESSION_ID = "session1"
USER_ID = "TESTUSER"
APP_NAME = "COMMENTATOR_AGENT"


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    root = ParallelAgent(
        name="Root",
        sub_agents=[supervisor, LiveCommentator()]
    )

    runner = Runner(
        agent=root,
        app_name=APP_NAME,
        session_service=session_service
    )

    content = Content(role="user",
                      parts=[Part(text="Kick-off the Supervisor workflow!")])
    async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
    ):
        print(event)


if __name__ == "__main__":
    asyncio.run(main())
