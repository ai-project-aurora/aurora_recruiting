import sys

from . import prompt

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response

from google.adk import Agent

interview_agent = Agent(
    # A unique name for the agent.
    name="interview_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash-001",
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use position description and candidate's skills and experience to generate interview questions for the candidate. The questions should be relevant to the position and the candidate's skills and experience.",
    # Instructions to set the agent's behavior.
    instruction=prompt.INTERVIEW_AGENT_PROMPT,
    output_key="interview_output",

    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)
