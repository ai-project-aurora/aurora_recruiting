import string

from random import random

import uuid

from uuid import UUID

import os
from dotenv import load_dotenv
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

import vertexai
from vertexai import agent_engines

# Load environment variables and initialize Vertex AI
load_dotenv()
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["GOOGLE_CLOUD_LOCATION"]
bucket = os.environ.get('"GOOGLE_CLOUD_BUCKET"')
app_name = os.environ.get("APP_NAME", "Aurora Recruiting Agent")
bucket_name = f"gs://{bucket}"

# Initialize Google Cloud Logging with the correct project ID
cloud_logging_client = google.cloud.logging.Client(project=project_id)
handler = CloudLoggingHandler(cloud_logging_client, name="AuroraRecruitingAgent")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
my_user_id = "123456"

# Initialize Vertex AI with the correct project and location
vertexai.init(
    project=project_id,
    location=location,
    staging_bucket=bucket_name,
)

# Filter agent engines by the app name in .env
ae_apps = agent_engines.list(filter=f'display_name="{app_name}"')
remote_app = next(ae_apps)

logging.info(f"Using remote app: {remote_app.display_name}")

# Get a session for the remote app
remote_session = remote_app.create_session(user_id=my_user_id)

messageRequest = """
      Virtual Agent: Hi, I'm a recruiting agent. How can I help you today?
      User: I'm looking for a mechanical engineer.
      Virtual Agent: I will search the requirements for a mechanical engineer.
                              I will access the datastore to check the matching candidates.
                              I will extract the skills and evaluate the candidates.
                              I will store the information in cloud storage and firestore.
"""

# Run the agent with this hard-coded input
events = remote_app.stream_query(
    user_id=my_user_id,
    session_id=remote_session["id"],
    message=messageRequest,
)

# Print responses
for event in events:
    for part in event["content"]["parts"]:
        if "text" in part:
            response_text = part["text"]
            print("[remote response]", response_text)
            logging.info("[remote response] " + response_text)

cloud_logging_client.flush_handlers()
