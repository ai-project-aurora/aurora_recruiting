import sys

from . import prompt

sys.path.append("..")
from callback_logging import log_query_to_model, log_model_response
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import FileWriterTool
from google.adk import Agent

compliance_agent = Agent(
    # A unique name for the agent.
    name="compliance_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash",
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Agent for verifying compliance rules, fairness and local laws. ",
    # Instructions to set the agent's behavior.
    instruction=prompt.COMPLIANCE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[ CrewaiTool(
        name="compliance_file_writer_tool",
        description=(
            "Writes a file to disk when run with a"
            "filename, content, overwrite set to 'true',"
            "and an optional directory"
        ),
        tool=FileWriterTool()
    )]
)
