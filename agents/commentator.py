import asyncio, time, json
from asyncio import Queue
from pydantic import PrivateAttr
from collections import deque
from typing import AsyncGenerator, Deque

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import Client  # Gemini SDK
from google.genai.types import Content, Part, LiveConnectConfig, Modality
from google.adk.models.lite_llm import LiteLlm

MAX_EVENTS = 25  # sliding window size
GEMINI_LIVE_MODEL = "gemini-2.0-flash-live-001"
FALLBACK_MODEL = LiteLlm(model="openai/gpt-4o")  # any OpenAI model

# Global queue for receiving tool events from callbacks
commentator_queue = Queue()


class LiveCommentator(BaseAgent):
    """Streams narrated commentary for every observed event."""

    # declare private attribute so Pydantic knows about it
    _buffer: Deque[str] = PrivateAttr(default_factory=lambda: deque(maxlen=MAX_EVENTS))

    def __init__(self, name: str = "Commentator"):
        # let BaseAgent/Pydantic finish their own __init__ first
        super().__init__(name=name, sub_agents=[])

    async def _stream_gemini_live(self, text: str) -> None:
        client = Client(vertexai=True)  # project & key from env
        async with client.aio.live.connect(
                model=GEMINI_LIVE_MODEL,
                config=LiveConnectConfig(response_modalities=[Modality.AUDIO]),
        ) as session:
            await session.send_client_content(
                turns=Content(role="user", parts=[Part(text=text)])
            )
            async for _ in session.receive():  # discard server echoes
                pass

    async def _narrate(self) -> None:
        """Stream recent events to Gemini Live for narration."""
        if len(self._buffer) == 0:
            return

        narration = "\n".join(list(self._buffer)[-5:])

        try:
            await self._stream_gemini_live(f"Provide live commentary: {narration}")
        except Exception as e:
            print(f"Gemini Live failed, using fallback: {e}")
            try:
                # Use LiteLLM correctly through ADK's interface
                import litellm
                response = await litellm.acompletion(
                    model="openai/gpt-4o",
                    messages=[{"role": "user", "content": f"Provide live commentary: {narration}"}]
                )
                print(f"Commentary: {response.choices[0].message.content}")
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        timeout_count = 0
        max_timeouts = 10  # Stop after 10 consecutive timeouts

        while timeout_count < max_timeouts:
            try:
                event = await asyncio.wait_for(commentator_queue.get(), timeout=1.0)
                timeout_count = 0  # Reset on successful event
                self._buffer.append(json.dumps(event))
                await self._narrate()
                yield Event(author=self.name)
            except asyncio.TimeoutError:
                timeout_count += 1
                if timeout_count < max_timeouts:
                    yield Event(author=self.name)  # Heartbeat

        print("Commentator finished - no more events detected")

