import os
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent

from google.adk.tools import VertexAiSearchTool
from google.adk.tools import google_search  # The Google Search tool

from google.genai import types
from google.adk import Agent
from dotenv import load_dotenv

# 1. Load environment variables from the agent directory's .env file
load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.5-flash")
project_name = os.getenv("GOOGLE_CLOUD_PROJECT", "hacker2025-team-182-dev")
deploy = os.getenv("DEPLOY", "False")
print("deploy: ", deploy)
if deploy != "True":
    print("Running the agent locally")
    from .prompt import *
    from .tools import *
else:
    print("Deploying the agent to Agent Engine")
    from prompt import *
    from tools import *

datastorePath = (
    "projects/"
    + project_name
    + "/locations/global/collections/default_collection/dataStores/"
)

print("datastoreIdPath: ", datastorePath)

vertexai_search_tool = VertexAiSearchTool(
    data_store_id=datastorePath + "aurora-dataset01-unstructured_1750257838490"
)
vertexai_search_tool2 = VertexAiSearchTool(
    data_store_id=datastorePath + "aurora-dataset02-unstructured_1750258103806"
)
vertexai_search_tool3 = VertexAiSearchTool(
    data_store_id=datastorePath + "aurora-dataset03-unstructured_1750258161445"
)

datastore_agent1 = Agent(
    # A unique name for the agent.
    name="datastore_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool available for you to access the datastore containing the candidates CVs.",
    # Instructions to set the agent's behavior.
    instruction=DATASTORE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[vertexai_search_tool],
)

datastore_agent2 = Agent(
    # A unique name for the agent.
    name="datastore_agent2",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool2 available for you  to access the datastore containing the candidates CVs. ",
    # Instructions to set the agent's behavior.
    instruction=DATASTORE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[vertexai_search_tool2],
)

datastore_agent3 = Agent(
    # A unique name for the agent.
    name="datastore_agent3",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool3 available for you to access the datastore containing the candidates CVs.",
    # Instructions to set the agent's behavior.
    instruction=DATASTORE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[vertexai_search_tool3],
)

skill_extractor = Agent(
    # A unique name for the agent.
    name="skill_extractor",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Extract skills for each candidate from the candidate's CV using datastore",
    # Instructions to set the agent's behavior.
    instruction=SKILL_EXTRACTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

initialization_agent = Agent(
    name="initialization_agent",
    model=model_name,
    description="Store request document in the firestore using store_wizard.",
    instruction=INIT_AGENT_PROMPT,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[store_wizard],
)

user_uploads_agent = Agent(
    name="user_uploads_agent",
    model=model_name,
    description="Get user uploads if requested.",
    instruction=USER_UPLOADS_AGENT_PROMPT,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[read_from_gcs],
)

data_retriever_team = ParallelAgent(
    name="data_retriever_team",
    sub_agents=[
        datastore_agent1,
        datastore_agent2,
        datastore_agent3,
        user_uploads_agent,
    ],
)

candidate_agent = Agent(
    # A unique name for the agent.
    name="candidate_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use the information provided by the previous agents to match the skills and experiences to the relevant position",
    # Instructions to set the agent's behavior.
    instruction=CANDIDATE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

candidate_selector_agent = Agent(
    # A unique name for the agent.
    name="candidate_selector_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="List top candidates ordered by their score and ask the user the number or names of candidates to process.",
    # Instructions to set the agent's behavior.
    instruction=CANDIDATE_SELECTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="selected_candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

compliance_agent = Agent(
    # A unique name for the agent.
    name="compliance_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Agent for verifying compliance rules, fairness and local laws. ",
    # Instructions to set the agent's behavior.
    instruction=COMPLIANCE_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[upload_to_gcs],
)
writer_agent = Agent(
    name="writer_agent",
    model=model_name,
    description=WRITE_AGENT,
    instruction="",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the CrewAI FileWriterTool below
    tools=[upload_to_gcs],
)
interview_agent = Agent(
    # A unique name for the agent.
    name="interview_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use position description and candidate's skills and experience to generate interview questions for the candidate. The questions should be relevant to the position and the candidate's skills and experience.",
    # Instructions to set the agent's behavior.
    instruction=INTERVIEW_AGENT_PROMPT,
    output_key="interview_output",
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[upload_to_gcs],
)
candidate_notification_agent = Agent(
    # A unique name for the agent.
    name="candidate_notification_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use the information provided by the previous agents to write a personal interview notification email to the candidate.",
    # Instructions to set the agent's behavior.
    instruction=CANDIDATE_NOTIFICATION_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[upload_to_gcs],
)

salary_agent = Agent(
    # A unique name for the agent.
    name="candidate_agent",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use the information provided by the previous agents and google google search to determine a suitable salary for the candidate based on their skills and experience.",
    # Instructions to set the agent's behavior.
    instruction=SALARY_PROMPT,
    # Callbacks to log the request to the agent and its response.
    output_key="candidate_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[upload_to_gcs],
)

requirements_agent = Agent(
    # name: A unique name for the agent.
    name="requirements_agent",
    # description: A short description of the agent's purpose, so
    # other agents in a multi-agent system know when to call it.
    description="Fulfill the requirements for the position using Google Search.",
    # model: The LLM model that the agent will use:
    model=os.getenv("MODEL"),
    # instruction: Instructions (or the prompt) for the agent.
    instruction=REQUIREMENTS_AGENT_PROMPT,
    # callbacks: Allow for you to run functions at certain points in
    # the agent's execution cycle. In this example, you will log the
    # request to the agent and its response.
    output_key="requirements_output",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[google_search],
)

initialization_team = ParallelAgent(
    name="initialization_team", sub_agents=[initialization_agent, requirements_agent]
)

documentation_agent = Agent(
    name="documentation_agent",
    model=model_name,
    description="Use the information provided by the previous agents to store the requirements, skills, and interview questions in a structured format in the firestore using the Firestore tool.",
    instruction=DOCUMENTATION_AGENT_PROMPT,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[store_candidate],
)

wizard_agent = Agent(
    name="wizard_agent",
    model=model_name,
    description="Use the information provided by the previous agents to store the data in a structured format in the firestore using the Firestore tool.",
    instruction=WIZARD_AGENT_PROMPT,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    tools=[store_wizard],
)

orchestrator = SequentialAgent(
    name="orchestrator",
    description=(
        "Greet the user and ask them to provide a position they are hiring for."
        "Ask user to upload candidate resumes or use external datastores. "
        "Delegate to other agents dependent on their tasks. "
        " The orchestrator will then delegate the task to the requirements_agent, to fulfill the requirements. "
        " Skill_extractor will use datastore to extract skills from the cvs of candidates."
        "Candidate_agent will analyze the skills and qualifications of candidates based on the requirements provided by the user and select the best candidates."
        "Candidate_selector_agent will list top candidates ordered by their score and ask the user the number or names of candidates to process."
        "Wizard agent will store all matching candidates into the firestore wizard collection."
        "Interview_agent will conduct interviews with the selected candidates and ask them questions based on the requirements provided by the user."
        "Candidate_notification_agent will notify the candidates about the interview results and next steps."
    ),
    sub_agents=[
        initialization_team,
        data_retriever_team,
        skill_extractor,
        candidate_agent,
        candidate_selector_agent,
        wizard_agent,
        # interview_agent,
        # compliance_agent,
        # salary_agent,
        # candidate_notification_agent,
        # documentation_agent,
    ],
)

root_agent = orchestrator
