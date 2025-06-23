from firebase_functions.firestore_fn import (
    on_document_written,
    Event,
    Change,
    DocumentSnapshot,
)

# from vertexai import agent_engines
from google import auth as google_auth
from google.auth.transport import requests as google_requests

# import requests
# import json
import pprint

import vertexai
from vertexai import agent_engines

project_id = "hacker2025-team-182-dev"
agent_engine_resource_id = "9130379741423992832"
agent_engine_resource_location = "europe-west1"
agent_engine_app_name = "Aurora Recruiting Agent"
agent_engine_bucket_name = "project-aurora-dev-bucket"

reasoning_engine_resource_id = f"projects/{project_id}/locations/{agent_engine_resource_location}/reasoningEngines/{agent_engine_resource_id}"
base_url = f"https://{agent_engine_resource_location}-aiplatform.googleapis.com/v1/{reasoning_engine_resource_id}"


# def get_identity_token():
#     credentials, _ = google_auth.default()
#     auth_request = google_requests.Request()
#     credentials.refresh(auth_request)

#     return credentials.token


@on_document_written(
    document="wizard/{auroraSessionId}", region="europe-west1", memory=512
)
def onAuroraEvents(event: Event[Change[DocumentSnapshot]]) -> None:
    print(f"new file written: '{event.params["auroraSessionId"]}'")
    print(f"value: {event.data}")
    # print(event.data)
    # print(event.data.params)

    processRequest(event.params["auroraSessionId"])


def processRequest(auroraSessionId):
    print("Triggering agent engine...")

    vertexai.init(
        project=project_id,
        location=agent_engine_resource_location,
        staging_bucket=f"gs://{agent_engine_bucket_name}",
    )

    all_engines = agent_engines.list(filter=f'display_name="{agent_engine_app_name}"')
    engine = next(all_engines)

    print(f"Using agent engine app: {engine.display_name}")

    stream_query(engine, auroraSessionId)


def stream_query(engine, auroraSessionId):
    print(f"stream query for session: {auroraSessionId}")

    events = engine.stream_query(
        user_id=f"{auroraSessionId}",
        # session_id=f"{auroraSessionId}",  # Optional
        message=f"There is a new request in firestore in 'wizard/{auroraSessionId}'. Please process it.",
    )

    for event in events:
        print(f"event: {event}")

    # max_events = 3
    # for i in range(max_events):
    #     try:
    #         event = next(events)
    #         print(f"event: {event}")
    #     except StopIteration:
    #         print("No more events.")
    #         break

    # for event in engine.stream_query(
    #     user_id=f"{auroraSessionId}",
    #     # session_id=f"{auroraSessionId}",  # Optional
    #     message="There is a new request in firestore in 'wizard/{auroraSessionId}'. Please process it.",
    # ):
    #     print(f"event: {event}")


# main is only used for local debugging
def main():
    print("starting function code in local debug mode")
    processRequest("debug")


if __name__ == "__main__":
    main()
