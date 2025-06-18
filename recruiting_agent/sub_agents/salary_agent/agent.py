import sys

from . import prompt

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response
from google.adk.tools import google_search  # The Google Search tool

from google.adk import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import FileWriterTool
salary_agent = Agent(
    # A unique name for the agent.
    name="candidate_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash",
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use the information provided by the previous agents and google google search to determine a suitable salary for the candidate based on their skills and experience.",
    # Instructions to set the agent's behavior.
    instruction=prompt.SALARY_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[ CrewaiTool(
        name="salary_file_writer_tool",
        description=(
            "Writes a file to disk when run with a"
            "filename, content, overwrite set to 'true',"
            "and an optional directory"
        ),
        tool=FileWriterTool()
    )]
)
