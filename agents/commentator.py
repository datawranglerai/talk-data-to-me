import asyncio
import atexit
import json
import os
from asyncio import Queue
from collections import deque
from typing import AsyncGenerator, Deque
import time

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client  # Gemini SDK
from google.genai.types import Content, Part, LiveConnectConfig, Modality
from loguru import logger
from pydantic import PrivateAttr

# For playing audio data
from utils.audio_player import CallbackAudioPlayer

# Global audio player instance
_audio_player = CallbackAudioPlayer()
atexit.register(_audio_player.stop)

MAX_EVENTS = 25  # sliding window size
GEMINI_LIVE_MODEL = "gemini-2.0-flash-live-001"
FALLBACK_MODEL = LiteLlm(model="openai/gpt-4o")  # any OpenAI model

# Global queue for receiving tool events from callbacks
commentator_queue = Queue()


class LiveCommentator(BaseAgent):
    """Streams narrated commentary for every observed event."""

    # declare private attribute so Pydantic knows about it
    _buffer: Deque[str] = PrivateAttr(default_factory=lambda: deque(maxlen=MAX_EVENTS))
    _commentary_history: Deque[str] = PrivateAttr(
        default_factory=lambda: deque(maxlen=10))  # Remember last 10 commentaries
    _event_count: int = PrivateAttr(default=0)
    _session_start_time: float = PrivateAttr(default_factory=time.time)

    def __init__(self, name: str = "Commentator"):
        # let BaseAgent/Pydantic finish their own __init__ first
        super().__init__(name=name, sub_agents=[])
        _audio_player.start()

    async def _stream_gemini_live(self, text: str) -> None:
        try:
            # client = Client(vertexai=True)  # project & key from env
            client = Client(api_key=os.getenv("GOOGLE_API_KEY"))
            async with client.aio.live.connect(
                    model=GEMINI_LIVE_MODEL,
                    config=LiveConnectConfig(response_modalities=[Modality.AUDIO]),
            ) as session:
                await session.send_client_content(
                    turns=Content(role="user", parts=[Part(text=text)])
                )
                logger.debug("🎤 Listening for Gemini Live audio response...")
                audio_received = False
                text_received = False

                async for response in session.receive():
                    # Handle different response types from Gemini Live
                    if hasattr(response, 'server_content') and response.server_content:
                        server_content = response.server_content

                        # Check for audio data in inline_data
                        if hasattr(server_content, 'model_turn') and server_content.model_turn:
                            model_turn = server_content.model_turn
                            if hasattr(model_turn, 'parts') and model_turn.parts:
                                for part in model_turn.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        audio_data = part.inline_data.data
                                        audio_received = True
                                        # logger.debug(f"🔊 AUDIO RECEIVED: {len(audio_data)} bytes!")
                                        # Audio playback
                                        try:
                                            self._play_audio_chunk(audio_data)
                                        except Exception as e:
                                            logger.error(f"There was an error playing commentary audio: {e}")
                                            import traceback
                                            logger.error(f"Full error: {traceback.format_exc()}")
                                            raise
                                    elif hasattr(part, 'text') and part.text:
                                        text_received = True
                                        print(f"📝 Text response: {part.text}")

                        # Alternative: Check for audio directly on server_content
                        elif hasattr(server_content, 'inline_data') and server_content.inline_data:
                            audio_data = server_content.inline_data.data
                            audio_received = True
                            logger.debug(f"🔊 AUDIO RECEIVED: {len(audio_data)} bytes!")

                        # Alternative: Check for text directly on server_content
                        elif hasattr(server_content, 'text') and server_content.text:
                            text_received = True
                            print(f"📝 Text response: {server_content.text}")

                if not audio_received and not text_received:
                    print("❌ No audio or text data received in Gemini Live response")
                elif audio_received:
                    print("✅ Gemini Live audio response received successfully!")
        except Exception as e:
            print(f"An error occurred streamining Gemini Live: {e}")
            import traceback
            print(f"Full error: {traceback.format_exc()}")
            raise

    def _play_audio_chunk(self, audio_bytes: bytes):
        """Play audio chunk through speakers using PyAudio."""
        try:
            _audio_player.add_chunk(audio_bytes)
            logger.debug(f"🔊 AUDIO BUFFERED: {len(audio_bytes)} bytes!")
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")

    def _get_commentary_style(self) -> str:
        """Rotate between different commentary styles."""
        styles = [
            "sports announcer with high energy and play-by-play details",
            "technical analyst focusing on efficiency and patterns",
            "strategic commentator analyzing decision-making",
            "investigative reporter uncovering the story behind the actions",
            "data scientist explaining the technical implications"
        ]

        # Rotate based on event count
        style_index = (self._event_count - 1) % len(styles)
        return styles[style_index]

    def _generate_commentary_prompt(self, narration: str) -> str:
        """Generate a varied, contextual prompt for commentary."""

        style = self._get_commentary_style()

        # Get recent commentary to avoid repetition
        recent_commentary = list(self._commentary_history)[-3:] if self._commentary_history else []

        # Calculate session progress
        session_duration = time.time() - self._session_start_time

        # Create context-aware prompt
        base_prompt = f"""You are an AI sports-style commentator in the style of a {style}, providing live analysis of AI agent activities. 

        Current Activities:
        {narration}
    
        Session Context:
        - Event #{self._event_count}
        - Session running for {session_duration:.1f} seconds
        - Total events processed: {len(self._buffer)}
    
        Previous Commentary (avoid repeating):
        {chr(10).join(recent_commentary) if recent_commentary else "None"}
    
        INSTRUCTIONS:
        - Provide fresh, varied commentary that's different from previous remarks
        - Use sports commentary style with energy and insight
        - Focus on patterns, efficiency, and strategic decisions
        - Mention specific agent names and tool usage
        - Keep commentary under 50 words
        - Be creative with analogies and observations"""

        return base_prompt

    async def _narrate(self) -> None:
        """Stream recent events to Gemini Live for narration."""
        logger.debug(f"🎯 _narrate() called with buffer size: {len(self._buffer)}")  # DEBUG

        if len(self._buffer) == 0:
            logger.debug("🎯 Buffer is empty, skipping narration")
            return

        narration = "\n".join(list(self._buffer)[-5:])
        logger.debug(f"🎯 Narration content (first 100 chars): {narration[:100]}...")

        # Get more context than just last 5 events
        recent_events = list(self._buffer)[-8:]  # More context
        narration = "\n".join(recent_events)

        # Generate contextual prompt
        prompt = self._generate_commentary_prompt(narration)

        logger.debug(f"🎯 Generated prompt (first 150 chars): {prompt[:150]}...")

        try:
            logger.debug("🎯 Attempting Gemini Live...")
            await self._stream_gemini_live(prompt)
            logger.debug("🎯 Gemini Live succeeded!")
        except Exception as e:
            logger.error(f"Gemini Live failed, using fallback: {e}")
            try:
                # Use LiteLLM correctly through ADK's interface
                logger.debug("🎯 Attempting LiteLLM fallback...")
                import litellm
                response = await litellm.acompletion(
                    model="openai/gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                commentary = response.choices[0].message.content
                print(f"\n🎙️ LIVE COMMENTARY: {commentary}\n")
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")

    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        timeout_count = 0
        max_timeouts = 5  # Stop after 5 consecutive timeouts

        logger.debug(f"🎯 Commentator starting, queue size: {commentator_queue.qsize()}")

        while timeout_count < max_timeouts:
            try:
                logger.debug(f"🎯 Waiting for event from queue (timeout {timeout_count}/{max_timeouts})...")
                event = await asyncio.wait_for(commentator_queue.get(), timeout=2.0)
                timeout_count = 0  # Reset on successful event
                self._buffer.append(json.dumps(event))
                logger.debug(f"🎯 Buffer now has {len(self._buffer)} events, calling _narrate()")
                await self._narrate()
                yield Event(author=self.name)
            except asyncio.TimeoutError:
                logger.debug(f"🎯 Queue timeout #{timeout_count + 1}")
                timeout_count += 1
                if timeout_count < max_timeouts:
                    yield Event(author=self.name)  # Heartbeat

        print("Commentator finished - no more events detected")
