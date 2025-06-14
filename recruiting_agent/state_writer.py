from typing import List
from google.adk.tools.tool_context import ToolContext


def save_to_state(
        tool_context: ToolContext,
        data: List[str]
) -> dict[str, str]:

    # Load existing attractions from state. If none exist, start an empty list
    existing_data = tool_context.state.get("data", [])

    # Update the 'attractions' key with a combo of old and new lists.
    # When the tool is run, ADK will create an event and make
    # corresponding updates in the session's state.
    tool_context.state["data"] = existing_data + data

    # A best practice for tools is to return a status message in a return dict
    return {"status": "success"}
