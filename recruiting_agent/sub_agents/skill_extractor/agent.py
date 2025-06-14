import sys

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
vertexai_search_tool = VertexAiSearchTool(
    data_store_id="projects/cap-global-genai-cx-sandbox/locations/global/collections/default_collection/dataStores/aurora-dataset01-unstructured_1749885872504"
    # data_store_id="projects/hacker2025-team-162-dev/locations/global/collections/default_collection/dataStores/dataset01-candidate-cvs-pdf_1749831357277"

)


skill_extractor = Agent(
    # A unique name for the agent.
    name="skill_extractor",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash-001",
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool to access the datastore containing the candidates CVs. Extract skills for each candidate from the candidate's CV using datastore",
    # Instructions to set the agent's behavior.
    instruction=prompt.SKILL_EXTRACTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the vertexai_search_tool tool to perform search on your data.
    tools=[vertexai_search_tool]
)
