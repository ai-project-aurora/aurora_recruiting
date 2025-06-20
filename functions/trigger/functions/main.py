from firebase_functions.firestore_fn import (
    on_document_written,
    Event,
    Change,
    DocumentSnapshot,
)

# from vertexai import agent_engines
from google import auth as google_auth
from google.auth.transport import requests as google_requests

import requests
import json

from vertexai import agent_engines

project_id = "hacker2025-team-182-dev"
agent_engine_resource_id = "3571917454458224640"
agent_engine_resource_location = "europe-west3"

base_url = f"https://{agent_engine_resource_location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{agent_engine_resource_location}/reasoningEngines/{agent_engine_resource_id}"


def get_identity_token():
    credentials, _ = google_auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)

    return credentials.token


@on_document_written(document="wizard/{auroraSessionId}", region="europe-west3")
def onAuroraEvents(event: Event[Change[DocumentSnapshot]]) -> None:
    print(f"new file written: '{event.params["auroraSessionId"]}'")
    print(f"value: {event.data}")

    auroraSessionId = event.params["auroraSessionId"]

    # get_agent_info()
    # create_session(auroraSessionId)
    # get_session(auroraSessionId)
    # stream_query(auroraSessionId)
    stream_query(auroraSessionId)


def create_session(auroraSessionId: str):
    print(f"create agent session: {auroraSessionId}")

    response = requests.post(
        f"{base_url}:query",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        },
        data=json.dumps(
            {
                "class_method": "create_session",
                "input": {"user_id": f"{auroraSessionId}"},
            }
        ),
    )

    print(f"create session response: {response.status_code} {response.text}")


def get_session(auroraSessionId: str):
    print(f"list agent sessions")

    response = requests.post(
        f"{base_url}:query",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        },
        data=json.dumps(
            {
                "class_method": "list_sessions",
                "input": {"user_id": f"{auroraSessionId}"},
            }
        ),
    )

    print(f"list agent response: {response.status_code} {response.text}")


def create_session(auroraSessionId: str):
    print(f"create agent session: {auroraSessionId}")

    response = requests.post(
        f"{base_url}:query",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        },
        data=json.dumps(
            {
                "class_method": "create_session",
                "input": {"user_id": f"{auroraSessionId}"},
            }
        ),
    )

    print(f"create session response: {response.status_code} {response.text}")


# def stream_query(auroraSessionId: str):
#     print(f"create agent session: {auroraSessionId}")

#     response = requests.post(
#         f"{base_url}:streamQuery",
#         headers={
#             "Content-Type": "application/json; charset=utf-8",
#             "Authorization": f"Bearer {get_identity_token()}",
#         },
#         data=json.dumps(
#             {
#                 "class_method": "stream_query",
#                 "input": {
#                     "user_id": f"{auroraSessionId}",
#                     "session_id": f"{auroraSessionId}",
#                     "message": "What is the exchange rate from US dollars to SEK today?",
#                 },
#             }
#         ),
#         # stream=True,
#     )

#     print(f"query response: {response.status_code} {response.text}")


def stream_query(auroraSessionId: str):
    adk_app = agent_engines.get(
        f"projects/{project_id}/locations/{agent_engine_resource_location}/reasoningEngines/{agent_engine_resource_id}"
    )
    for event in adk_app.stream_query(
        user_id=f"{auroraSessionId}",
        # session_id=f"{auroraSessionId}",  # Optional
        message="What is the exchange rate from US dollars to SEK today?",
    ):
        print(event)


def get_agent_info():
    response = requests.get(
        f"{base_url}",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        },
    )

    print(f"response: {response.status_code} {response.text}")
