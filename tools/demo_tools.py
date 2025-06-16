from google.adk.tools import ToolContext


def fake_search(query: str, tool_context: ToolContext):
    """Pretend to search the web and return a stub result.

    Args:
        query: The search query string

    Returns:
        A dictionary containing the search results
    """
    return {"result": f"Search results for '{query}'."}


def fake_summarise(text: str, tool_context: ToolContext):
    """Summarise text in one sentence.

    Args:
        text: The text to summarize

    Returns:
        A dictionary containing the summary
    """
    return {"summary": f"Summary: {text[:50]}..."}
