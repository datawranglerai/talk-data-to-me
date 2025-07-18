from google.adk.tools import BaseTool, ToolContext

from typing import Optional, Dict, Any
from loguru import logger


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
    from commentator_agent.commentator import commentator_queue

    event_data = {
        "agent": tool_context.agent_name,  # Get agent name from tool_context
        "tool": tool.name,
        "args": args,
        "timestamp": "now"
    }

    # Push event to commentator queue (non-blocking)
    try:
        commentator_queue.put_nowait(event_data)
        logger.debug(f"🎯 CALLBACK: Put event in queue. Queue size now: {commentator_queue.qsize()}")
        logger.debug(f"--- Tool {tool.name} called for {tool_context.agent_name} ---")  # Add this debug line
    except Exception as e:
        logger.error(f"Failed to enqueue event: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")

    return None  # allow the real tool to execute


def broadcast_tool_complete(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext,
        tool_response: Any
) -> Optional[Dict]:
    """Captures tool completion event with outputs."""
    from commentator_agent.commentator import commentator_queue

    event_data = {
        "event_type": "tool_complete",
        "agent": tool_context.agent_name,
        "tool": tool.name,
        "args": args,
        "result": tool_response,
        "timestamp": "now"
    }

    try:
        commentator_queue.put_nowait(event_data)
        logger.debug(f"🎯 TOOL COMPLETE: {tool.name} finished with result: {str(tool_response)[:100]}...")
    except Exception as e:
        logger.error(f"Failed to enqueue tool complete event: {e}")

    return tool_response  # Return the result unchanged
