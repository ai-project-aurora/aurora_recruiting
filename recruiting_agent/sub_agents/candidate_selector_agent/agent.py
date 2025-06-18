import sys

from . import prompt

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response

from google.adk import Agent

candidate_selector_agent = Agent(
    # A unique name for the agent.
    name="candidate_selector_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash",
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="List top candidates ordered by their score and ask the user the number or names of candidates to process.",
    # Instructions to set the agent's behavior.
    instruction=prompt.CANDIDATE_SELECTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="selected_candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)
