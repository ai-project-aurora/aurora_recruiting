import vertexai
from vertexai import agent_engines

import os

from dotenv import load_dotenv


# 1. Load environment variables from the agent directory's .env file
load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.5-flash")
os.environ["DEPLOY"] = 'True'

from agent import orchestrator

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket="gs://" + os.getenv("GOOGLE_CLOUD_BUCKET"),
)

remote_app = agent_engines.create(
    display_name=os.getenv("APP_NAME", "Aurora Recruiting Agent App"),
    agent_engine=orchestrator,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "scikit-learn",
        "langchain-community",
        "wikipedia",
        "crewai_tools"
        "dateparser",
        "pydantic",
        "cloudpickle",
    ],
    extra_packages=[
        "agent.py",
        "tools.py",
        "prompt.py",
    ]
)
