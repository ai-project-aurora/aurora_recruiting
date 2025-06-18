import sys
import os
from dotenv import load_dotenv

from . import prompt
from ...state_writer import save_to_state

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response

from google.adk import Agent
# from agents.tools.retrieval import VertexAISearchTool
from google.adk.tools import VertexAiSearchTool

# The data_store_id path follows the same format as the datstore parameter
# of google.genai.types.VertexAISearch. View its documentation here:
# https://googleapis.github.io/python-genai/genai.html#genai.types.VertexAISearch

# Create your vertexai_search_tool and update its path below
datastore1 = VertexAiSearchTool(
    data_store_id="projects/hacker2025-team-182-dev/locations/global/collections/default_collection/dataStores/aurora-dataset01-unstructured_1750257838490"
)
datastore2 = VertexAiSearchTool(
    data_store_id="projects/hacker2025-team-182-dev/locations/global/collections/default_collection/dataStores/aurora-dataset02-unstructured_1750258103806"
)
datastore3 = VertexAiSearchTool(
    data_store_id="projects/hacker2025-team-182-dev/locations/global/collections/default_collection/dataStores/aurora-dataset01-unstructured_1750257838490"
)
load_dotenv()
model_name = os.getenv("MODEL")

skill_extractor = Agent(
    # A unique name for the agent.
    name="skill_extractor",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool to access the datastore containing the candidates CVs. Extract skills for each candidate from the candidate's CV using datastore",
    # Instructions to set the agent's behavior.
    instruction=prompt.SKILL_EXTRACTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the vertexai_search_tool tool to perform search on your data.
    tools=[datastore1]
)
