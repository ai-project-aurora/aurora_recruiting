from google.adk import Agent
from google.adk.tools import google_search  # The Google Search tool

import sys

from . import prompt

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response


requirements_agent = Agent(
    # name: A unique name for the agent.
    name="requirements_agent",
    # description: A short description of the agent's purpose, so
    # other agents in a multi-agent system know when to call it.
    description="Fulfill the requirements for the position using Google Search.",
    # model: The LLM model that the agent will use:
    model="gemini-2.0-flash-001",
    # instruction: Instructions (or the prompt) for the agent.
    instruction=prompt.REQUIREMENTS_AGENT_PROMPT,
    # callbacks: Allow for you to run functions at certain points in
    # the agent's execution cycle. In this example, you will log the
    # request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[google_search]
)
