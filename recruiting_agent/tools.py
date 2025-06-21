import logging
import google.cloud.logging
import os

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import FileWriterTool
from typing import List
from google.adk.tools.tool_context import ToolContext
from dotenv import load_dotenv

load_dotenv()


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


deploy=os.getenv("DEPLOY", "false"),

def write_to_file(file_name):
    if deploy != "true":
        return CrewaiTool(
            name=file_name,
            description=(
                "Writes a file to disk when run with a"
                "filename, content, overwrite set to 'true',"
                "and an optional directory"
            ),
            tool=FileWriterTool()
        )

def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts and "text" in llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
            logging.info(f"[query to {callback_context.agent_name}]: " + last_user_message)

def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info(f"[response from {callback_context.agent_name}]: " + part.text)
            elif part.function_call:
                logging.info(f"[function call from {callback_context.agent_name}]: " + part.function_call.name)
