from firebase_functions.firestore_fn import (
    on_document_written,
    Event,
    Change,
    DocumentSnapshot,
)

import vertexai
from vertexai import agent_engines

project_id = "hacker2025-team-182-dev"
agent_engine_resource_location = "europe-west1"
agent_engine_app_name = "Aurora Recruiting Agent"
agent_engine_bucket_name = "project-aurora-dev-bucket"


@on_document_written(
    document="wizard/{auroraSessionId}", region="europe-west1", memory=512
)
def onAuroraEvents(event: Event[Change[DocumentSnapshot]]) -> None:
    print(
        f"new file written in '{event.params["auroraSessionId"]}': {event.data.after.to_dict()}"
    )

    status = event.data.after.get("status")

    if status != "start_matching":
        print(f"status '{status}' will not trigger aurora. Exiting...")
        return

    auroraSessionId = event.params["auroraSessionId"]
    demand_description = event.data.after.get("demandDescription")
    sources_internal = event.data.after.get("sources.internal")
    sources_external = event.data.after.get("sources.additional")

    prompt_message = create_prompt_message(
        auroraSessionId,
        demand_description,
        sources_internal,
        sources_external,
    )

    processRequest(auroraSessionId, prompt_message)


def create_prompt_message(
    auroraSessionId, demandDescription, useInternalSources, useExternalSources
):
    return (
        f"Research on the following demand: {demandDescription}."
        f"Use internal sources: {useInternalSources}, external sources: {useExternalSources}."
        f"session id: '{auroraSessionId}'."
    )


def get_engine():
    print("Triggering agent engine...")

    vertexai.init(
        project=project_id,
        location=agent_engine_resource_location,
        staging_bucket=f"gs://{agent_engine_bucket_name}",
    )

    all_engines = agent_engines.list(filter=f'display_name="{agent_engine_app_name}"')
    engine = next(all_engines)

    return engine


def processRequest(sessionId, prompt_message):
    engine = get_engine()

    print(f"Using agent engine app: {engine.display_name}")

    stream_query(engine, sessionId, prompt_message)


def stream_query(engine, sessionId, prompt_message):
    print(f"stream query for session: {sessionId}")

    print(f"query with message: {prompt_message}")

    events = engine.stream_query(
        user_id=f"{sessionId}",
        message=prompt_message,
    )

    for event in events:
        print(f"event: {event}")


# main is only used for local debugging
def main():
    print("starting function code in local debug mode")
    processRequest("hj2wWIrrxSRxAEIllmWH")


if __name__ == "__main__":
    main()
