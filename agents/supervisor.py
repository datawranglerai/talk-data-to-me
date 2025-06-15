from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import BaseTool, ToolContext
from tools.demo_tools import fake_search, fake_summarise

from typing import Optional, Dict, Any

# Use a cheap OpenAI model for logic
LLM_MODEL = "openai/gpt-4.1-nano"


def broadcast_tool_event(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext
) -> Optional[Dict]:
    """
    Publishes every impending tool call to the Commentator queue so it can
    narrate. Return None to let the tool run normally.
    """
    # Import the global queue from commentator module
    from agents.commentator import commentator_queue

    event_data = {
        "agent": tool_context.agent_name,  # Get agent name from tool_context
        "tool": tool.name,
        "args": args,
        "timestamp": "now"
    }

    # Push event to commentator queue (non-blocking)
    try:
        commentator_queue.put_nowait(event_data)
    except Exception as e:
        print(f"Failed to enqueue event: {e}")

    return None  # allow the real tool to execute


supervisor = SequentialAgent(
    name="Supervisor",
    sub_agents=[
        LlmAgent(
            name="Searcher",
            model=LiteLlm(model=LLM_MODEL),
            instruction="Use fake_search to look things up.",
            tools=[fake_search],
            before_tool_callback=broadcast_tool_event
        ),
        LlmAgent(
            name="Summariser",
            model=LiteLlm(model=LLM_MODEL),
            instruction="Use fake_summarise on the previous search result.",
            tools=[fake_summarise],
            before_tool_callback=broadcast_tool_event
        ),
    ],
)
