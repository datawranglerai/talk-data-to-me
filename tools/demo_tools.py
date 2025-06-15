from google.adk.tools import ToolContext
from typing import Dict


def fake_search(query: str, tool_context: ToolContext) -> Dict:
    """Pretend to search the web and return a stub result."""
    return {"result": f"Search results for '{query}'."}


def fake_summarise(text: str, tool_context: ToolContext) -> Dict:
    """Summarise text in one sentence."""
    return {"summary": f"Summary: {text[:50]}..."}
