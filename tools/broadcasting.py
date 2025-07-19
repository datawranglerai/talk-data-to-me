from google.adk.tools import BaseTool, ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

from typing import Optional, Dict, Any
from loguru import logger
from datetime import datetime
import time


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
        "timestamp": time.time(),
        "start_time": datetime.now().isoformat(),
        "execution_id": f"{tool_context.agent_name}_{tool.name}_{int(time.time()*1000)}",
        "agent_state": getattr(tool_context, 'agent_state', None),
        "previous_tools": getattr(tool_context, 'tool_history', [])[-10:],  # Last 3 tools
        "workflow_stage": getattr(tool_context, 'workflow_stage', 'unknown'),
        "session_context": {
            "total_tools_called": getattr(tool_context, 'tool_count', 0),
            "session_duration": time.time() - getattr(tool_context, 'session_start', time.time())
        },
        "workflow_context": {
            "current_goal": getattr(tool_context, 'current_objective', 'unknown'),
            "progress_stage": getattr(tool_context, 'progress_percentage', 0),
            "parallel_agents": getattr(tool_context, 'active_agents', []),
            "dependencies": getattr(tool, 'depends_on', []),
            "expected_next_tools": getattr(tool_context, 'planned_tools', [])
        }
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
        "tool_response": tool_response,
        "timestamp": time.time(),
    }

    try:
        commentator_queue.put_nowait(event_data)
        logger.debug(f"🎯 TOOL COMPLETE: {tool.name} finished with result: {str(tool_response)[:200]}...")
    except Exception as e:
        logger.error(f"Failed to enqueue tool complete event: {e}")

    return tool_response  # Return the result unchanged


def broadcast_llm_reasoning(
        callback_context: CallbackContext,
        llm_response: LlmResponse
) -> Optional[None]:
    """
    Captures LLM responses and reasoning for transparency commentary.
    Used as an after_model_callback to broadcast LLM decision-making.
    """
    # Import the global queue from commentator module
    from commentator_agent.commentator import commentator_queue

    # Extract reasoning data from the LLM response
    reasoning_data = {
        "agent": callback_context.agent_name,
        "model_response": llm_response.content if hasattr(llm_response, 'content') else str(llm_response),
        "reasoning_type": "llm_decision",
        "timestamp": "now",
        "session_id": callback_context.session_id if hasattr(callback_context, 'session_id') else "unknown",
        "invocation_id": callback_context.invocation_id if hasattr(callback_context, 'invocation_id') else "unknown"
    }

    # Add token usage information if available
    if hasattr(llm_response, 'usage_metadata') and llm_response.usage_metadata:
        reasoning_data["token_usage"] = {
            "prompt_tokens": llm_response.usage_metadata.prompt_token_count,
            "completion_tokens": llm_response.usage_metadata.candidates_token_count,
            "total_tokens": llm_response.usage_metadata.total_token_count
        }

    # Push reasoning event to commentator queue (non-blocking)
    try:
        commentator_queue.put_nowait(reasoning_data)
        logger.debug(f"🧠 REASONING: Captured LLM response from {callback_context.agent_name}")
        logger.debug(f"🧠 Queue size now: {commentator_queue.qsize()}")
    except Exception as e:
        logger.error(f"Failed to enqueue LLM reasoning: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")

    return None  # Allow normal LLM response flow


