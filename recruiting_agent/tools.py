import logging
import google.cloud.logging
import os

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import List
from google.adk.tools.tool_context import ToolContext
from dotenv import load_dotenv
from google.cloud import firestore, storage

load_dotenv()
deploy=os.getenv("DEPLOY", 'False')
# from google.adk.tools.crewai_tool import CrewaiTool
# from crewai_tools import FileWriterTool

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


# Initialize Firestore client
db = firestore.Client()

def upload_to_gcs(file_name: str, data: str) -> dict[str, str]:
    """
    Uploads candidate data to gcs.
    Use candidate_name and candidate_data_type as path to file in the storage
    :param candidate_name - name of the candidate
    :param candidate_data_type - one of compliance, salary, skills, interview, notification

    """
    bucket_name = os.getenv("OUTPUT_BUCKET_NAME", "aurora-output-bucket")
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(data.encode("utf-8"))
        return {"status": "success", "path": f"gs://{bucket_name}/{file_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def store_candidate(candidate_id:str, data: dict) -> dict[str, str]:
    # Reference to the collection and document
    try:
        doc_ref = db.collection('wizard').document(candidate_id)
    # Set data in Firestore
        doc_ref.set(data)
        print(f"Candidate {candidate_id} data stored.")
        return {"status": "success " + candidate_id}
    except Exception as e:
        print(f"Error storing candidate {candidate_id} data: {e}")
        return {"status": "error"}

# def write_to_file(file_name):
#         return CrewaiTool(
#             name=file_name,
#             description=(
#                 "Writes a file to disk when run with a"
#                 "filename, content, overwrite set to 'true',"
#                 "and an optional directory"
#             ),
#             tool=FileWriterTool()
#         )
#
#


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
