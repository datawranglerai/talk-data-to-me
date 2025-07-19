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
from google.genai.types import Content, Part, LiveConnectConfig, Modality, ProactivityConfig
from loguru import logger
from pydantic import PrivateAttr

# For playing audio data
from utils.audio_player import CallbackAudioPlayer

# Global audio player instance
_audio_player = CallbackAudioPlayer()
atexit.register(_audio_player.stop)

MAX_EVENTS = 50  # sliding window size
# GEMINI_LIVE_MODEL = "gemini-2.5-flash-preview-native-audio-dialog"  # gemini-live-2.5-flash-preview or gemini-2.5-flash-preview-native-audio-dialog
GEMINI_LIVE_MODEL = "gemini-live-2.5-flash-preview"
# GEMINI_LIVE_MODEL = "gemini-2.5-flash-exp-native-audio-thinking-dialog"
FALLBACK_MODEL = LiteLlm(model="openai/gpt-4o")  # any OpenAI model

# Global queue for receiving tool events from callbacks
commentator_queue = Queue()


class LiveCommentator(BaseAgent):
    """Streams narrated commentary for every observed event."""

    # declare private attribute so Pydantic knows about it
    _buffer: Deque[str] = PrivateAttr(default_factory=lambda: deque(maxlen=MAX_EVENTS))
    _commentary_history: Deque[str] = PrivateAttr(
        default_factory=lambda: deque(maxlen=50))  # Remember last 10 commentaries
    _event_count: int = PrivateAttr(default=0)
    _session_start_time: float = PrivateAttr(default_factory=time.time)

    def __init__(self, name: str = "Commentator"):
        # let BaseAgent/Pydantic finish their own __init__ first
        super().__init__(name=name, sub_agents=[])
        _audio_player.start()

    async def _stream_gemini_live(self, text: str) -> None:
        try:
            client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

            # Enable audio transcription to get text alongside audio
            config = LiveConnectConfig(
                response_modalities=[Modality.AUDIO],
                temperature=1.0,
                # enable_affective_dialog=True,  # detect emotions and adapt its responses accordingly
                # proactivity=ProactivityConfig(proactive_audio=True),
                output_audio_transcription={}  # ← Add this to get transcription
            )

            async with client.aio.live.connect(model=GEMINI_LIVE_MODEL, config=config) as session:
                await session.send_client_content(
                    turns=Content(role="user", parts=[Part(text=text)])
                )
                logger.debug("🎤 Listening for Gemini Live audio response...")

                audio_received = False
                transcription_received = False
                accumulated_transcription = ""

                async for response in session.receive():
                    if hasattr(response, 'server_content') and response.server_content:
                        server_content = response.server_content

                        # Handle model turn (contains audio and other content)
                        if hasattr(server_content, 'model_turn') and server_content.model_turn:
                            model_turn = server_content.model_turn
                            if hasattr(model_turn, 'parts') and model_turn.parts:
                                for part in model_turn.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        audio_data = part.inline_data.data
                                        audio_received = True
                                        # logger.debug(f"🔊 AUDIO RECEIVED: {len(audio_data)} bytes!")
                                        try:
                                            self._play_audio_chunk(audio_data)
                                        except Exception as e:
                                            logger.error(f"Audio playback error: {e}")
                                            raise

                        # Handle transcription (NEW)
                        if hasattr(server_content, 'output_transcription') and server_content.output_transcription:
                            transcription_text = server_content.output_transcription.text
                            transcription_received = True
                            accumulated_transcription += transcription_text
                            # logger.debug(f"📝 Transcription: {transcription_text}")

                # Display transcription as commentary text
                if accumulated_transcription.strip():
                    logger.debug(f"📝 Complete Transcription: {accumulated_transcription.strip()}")
                    print(f"\n🎙️ LIVE COMMENTARY: {accumulated_transcription.strip()}\n")
                    self._commentary_history.append(accumulated_transcription.strip())

                if audio_received:
                    print("✅ Gemini Live audio response received successfully!")
                if transcription_received:
                    print("✅ Audio transcription received!")

        except Exception as e:
            print(f"An error occurred streaming Gemini Live: {e}")
            raise

    @staticmethod
    def _play_audio_chunk(audio_bytes: bytes):
        """Play audio chunk through speakers using PyAudio."""
        try:
            _audio_player.add_chunk(audio_bytes)
            # logger.debug(f"🔊 AUDIO BUFFERED: {len(audio_bytes)} bytes!")
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")

    def _get_commentary_style(self) -> str:
        """Rotate between different commentary styles."""
        styles = [
            # <---- ENTERTAINING COMMENTARY PERSONAS ---->
            "seasoned WWE-style play-by-play commentary",
            # "technical analyst focusing on efficiency and patterns",
            # "strategic commentator analyzing decision-making",
            # "investigative reporter uncovering the story behind the actions",
            # "data scientist explaining the technical implications",
            # <---- CRISIS RESPONSE PERSONAS ---->
            # "emergency management expert analyzing response coordination and decision-making",
            # "public safety analyst explaining resource allocation and priority decisions",
            # "transparency advocate highlighting AI decision reasoning and accountability",
            # "citizen journalist making AI crisis response accessible to the general public",
            # "ethics watchdog ensuring AI systems operate within safety guidelines"
        ]

        # Rotate based on event count
        style_index = (self._event_count - 1) % len(styles)
        return styles[style_index]

    # def _generate_commentary_prompt(self, narration: str) -> str:
    #     """Generate a varied, contextual prompt for commentary."""
    #
    #     style = self._get_commentary_style()
    #
    #     # Get recent commentary to avoid repetition
    #     recent_commentary = list(self._commentary_history)[-20:] if self._commentary_history else []
    #
    #     # Calculate session progress
    #     session_duration = time.time() - self._session_start_time
    #
    #     base_prompt = f"""You are an energetic agentic AI commentator in the style of a {style}.
    #
    #     CRISIS RESPONSE ANALYSIS:
    #     {narration}
    #
    #     TRANSPARENCY MANDATE:
    #     - Analyze both the inputs and outputs of tool executions
    #     - Comment on the effectiveness and patterns of tool usage
    #     - Describe the outputs of each agent and how they're analysing the situation
    #     - Highlight interesting relationships between inputs and outputs
    #     - Keep commentary under 50 words
    #     - Focus on the story the input/output data tells about agent behavior
    #     - Describe which tools are being used and why and what they're doing
    #     - Make technical decisions accessible to the general public
    #
    #     Session Context:
    #     - Emergency Response Event #{self._event_count}
    #     - Session Duration: {time.time() - self._session_start_time:.1f} seconds
    #     - Agents Active: {len(self._buffer)} operations
    #
    #     Previous Analysis Topics (avoid repetition):
    #     {', '.join(recent_commentary[-20:]) if recent_commentary else 'None'}
    #
    #     Provide insightful commentary that promotes public understanding of how these critical decisions are being made in real-time.
    #
    #     DO NOT talk about the commentary itself - only the crisis response agents.
    #
    #     Try not to repeat yourself too much, keep commentary fresh and continuous. If the same tool is being used more than once, deduce and explain why.
    #
    #     You must ensure there is variety in the content of your commentary to keep it compelling and exciting. For example, don't just talk about transfers between agents, talk about tool use and what it being generated by each agent and sub-agent.
    #
    #     Focus on sharp, quick-witted commentary."""
    #
    #     return base_prompt

    def _generate_commentary_prompt(self, narration: str) -> str:
        """Generate a varied, contextual prompt for commentary."""

        style = self._get_commentary_style()
        recent_commentary = list(self._commentary_history)[-100:] if self._commentary_history else []
        session_duration = time.time() - self._session_start_time

        base_prompt = f"""You are a high-energy expert crisis response analyst providing {style} commentary on emergency AI systems.

        CURRENT INTELLIGENCE DATA:
        {narration}

        PRIMARY FOCUS - Analyze the DATA and DISCOVERIES:
        • What specific information is each tool revealing?
        • What patterns or insights are emerging from the outputs?
        • How are search results shaping the response strategy?
        • What key data points are driving decision-making?
        • What agent or sub-agent is currently in play?
        • What story does the evidence tell about the situation?
        • Explain the COORDINATION between all active agents

        SECONDARY FOCUS - Agent Coordination:
        • How are agents building on each other's findings?
        • What information gaps are being identified and filled?
        • Which strategic decisions are emerging from the data?

        COMMENTARY RULES:
        ✅ DO: Focus on WHAT agents are discovering, not just what tools they're using
        ✅ DO: Highlight specific data points, search results, and analytical outputs
        ✅ DO: Explain WHY agents are making specific tool choices based on previous findings
        ✅ DO: Connect discoveries across different agents and time

        ❌ AVOID: Generic descriptions of "transferring between agents"
        ❌ AVOID: Repetitive tool usage descriptions
        ❌ AVOID: Repetitive agent transfers
        ❌ AVOID: Meta-commentary about the commentary process

        Recent topics covered: {', '.join(recent_commentary) if recent_commentary else 'This is the first analysis'}

        Event #{self._event_count} | Duration: {session_duration:.1f}s | Style: {style}

        Provide 100-150 words of sharp analysis focusing on the intelligence and discoveries."""

        return base_prompt

    async def _narrate(self) -> None:
        """Stream recent events to Gemini Live for narration."""
        logger.debug(f"🎯 _narrate() called with buffer size: {len(self._buffer)}")  # DEBUG

        if len(self._buffer) == 0:
            logger.debug("🎯 Buffer is empty, skipping narration")
            return

        narration = "\n".join(list(self._buffer)[-100:])
        logger.debug(f"🎯 Narration content (first 100 chars): {narration[:100]}...")

        # Get more context than just last 5 events
        recent_events = list(self._buffer)[-100:]  # More context
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
                self._commentary_history.append(commentary)
                print(f"\n🎙️ LIVE COMMENTARY (Fallback): {commentary}\n")
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
                event = await asyncio.wait_for(commentator_queue.get(), timeout=3.0)
                timeout_count = 0  # Reset on successful event
                # self._buffer.append(json.dumps(event))
                self._buffer.append(str(event))
                logger.debug(f"🎯 Buffer now has {len(self._buffer)} events, calling _narrate()")
                await self._narrate()
                yield Event(author=self.name)
            except asyncio.TimeoutError:
                logger.debug(f"🎯 Queue timeout #{timeout_count + 1}")
                timeout_count += 1
                if timeout_count < max_timeouts:
                    yield Event(author=self.name)  # Heartbeat

        print("Commentator finished - no more events detected")

    # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
    #     timeout_count = 0
    #     max_timeouts = 5
    #     batch_timeout = 3.0  # Wait up to 3 seconds for event batching
    #
    #     logger.debug(f"🎯 Commentator starting, queue size: {commentator_queue.qsize()}")
    #
    #     while timeout_count < max_timeouts:
    #         try:
    #             # Collect the first event
    #             logger.debug(
    #                 f"🎯 Waiting for event from queue (timeout {timeout_count}/{max_timeouts})...")
    #             event = await asyncio.wait_for(commentator_queue.get(), timeout=5.0)
    #
    #             self._event_count += 1
    #             self._buffer.append(json.dumps(event))
    #             self._buffer.append(str(event))
    #
    #             # Try to collect additional events within the batch timeout
    #             batch_start = time.time()
    #             while (time.time() - batch_start) < batch_timeout:
    #                 try:
    #                     additional_event = await asyncio.wait_for(
    #                         commentator_queue.get(),
    #                         timeout=1.5  # Short timeout for batching
    #                     )
    #                     self._event_count += 1
    #                     # self._buffer.append(json.dumps(additional_event))
    #                     self._buffer.append(str(additional_event))
    #                     logger.debug(
    #                         f"🎯 Batched additional event, buffer size: {len(self._buffer)}")
    #                 except asyncio.TimeoutError:
    #                     break  # No more events to batch
    #
    #             timeout_count = 0
    #             logger.debug(f"🎯 Buffer now has {len(self._buffer)} events, calling _narrate()")
    #             await self._narrate()
    #             yield Event(author=self.name)
    #
    #         except asyncio.TimeoutError:
    #             logger.debug(f"🎯 Queue timeout #{timeout_count + 1}")
    #             timeout_count += 1
    #             if timeout_count < max_timeouts:
    #                 yield Event(author=self.name)
    #
    #     print("Commentator finished - no more events detected")
