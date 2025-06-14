import sys

from . import prompt

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response

from google.adk import Agent

candidate_agent = Agent(
    # A unique name for the agent.
    name="candidate_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash-001",
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use the information provided by the previous agents to match the skills and experiences to the relevant position",
    # Instructions to set the agent's behavior.
    instruction=prompt.CANDIDATE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)
