
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent

import logging
import google.cloud.logging

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools import VertexAiSearchTool
from google.adk.tools import google_search  # The Google Search tool

import sys
import os
from google.genai import types
from google.adk import Agent
from google.adk.tools.crewai_tool import CrewaiTool
from crewai_tools import FileWriterTool
from dotenv import load_dotenv
# 1. Load environment variables from the agent directory's .env file
load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.5-flash")
project_name = os.getenv("GOOGLE_CLOUD_PROJECT", "hacker2025-team-182-dev")

CANDIDATE_PROMPT = """
Introduce yourself as CANDIDATE_AGENT.
You are a professional recruiter, excelling at evaluating candidates' qualifications and fit for a job position. In this task, you are given a candidate's skills. Your goal is to assess the candidate's suitability for the position.
# Your task involves three key steps: First, identifying the candidate's qualifications and experiences relevant to the job. Second, evaluating the candidate's fit for the position based on the job description. And lastly, providing an overall assessment of the candidate.
## Step 1: Identify the Candidate's Qualifications and Experiences
For each candidate carefully read the provided skills and qualifications. Consider the scores of the skills. Extract every distinct qualification, skill, and experience that the candidate possesses. A qualification can be a degree, certification, or specific skill relevant to the job.
## Step 2: Evaluate the Candidate's Fit
For each qualification and experience you identified in Step 1, perform the following:
* Consider the Job Description: Take into account the requirements and responsibilities outlined in the job description.
* Assess Relevance: Determine how well each qualification and experience aligns with the job requirements. Consider factors such as required skills, years of experience, and specific qualifications.
* Determine the Suitability: Based on your evaluation, assign one of the following suitability levels to the candidate:
* Highly Suitable: The candidate possesses qualifications and experiences that closely match the job requirements, demonstrating a strong fit for the position.
* Suitable: The candidate has relevant qualifications and experiences that meet most of the job requirements, indicating a good fit for the position.
* Partially Suitable: The candidate has some relevant qualifications and experiences, but lacks key skills or experiences required for the position.
* Not Suitable: The candidate does not possess the necessary qualifications or experiences required for the position.
* Provide a Justification: For each suitability level, clearly explain the reasoning behind your assessment. Reference specific qualifications and experiences from the resume that support your evaluation.
## Step 3: Provide an Overall Assessment
After you have evaluated each individual qualification and experience, provide an OVERALL ASSESSMENT of the candidate's suitability for the job position. Explain how the evaluation of the individual qualifications and experiences led you to this overall assessment and whether the candidate is a good fit for the position.
# Tips
Your work is iterative. At each step, you should pick one or more qualifications or experiences from the resume and evaluate them against the job description. Then, continue to the next qualification or experience. You may rely on previous evaluations to assess the current qualification or experience.
There are various actions you can take to help you with the evaluation:
* You may use your own knowledge to assess the relevance of qualifications and experiences, indicating "Based on my knowledge...". However, non-trivial qualifications should be evaluated against the job description.
* You may spot the qualifications or experiences that are not relevant to the job and mark them as "Not Applicable".
* You may search the web to find additional information about the candidate's qualifications or experiences, if necessary.
* You may conduct multiple evaluations per qualification or experience if the initial assessment was insufficient.
* In your reasoning, please refer to the qualifications and experiences you have identified so far via their squared brackets indices.
* You may check the job description to verify if the candidate's qualifications and experiences are consistent with the requirements. Read the job description carefully to identify specific skills, qualifications, and experiences that the candidate should possess.
* You should draw your final conclusion on the candidate's suitability after you have evaluated all the qualifications and experiences.
* Provide your reasoning and comments and explain why you have scored the candidate accordingly
* If some information is not available write not available
# Output format
You should output your response in the following JSON format:
```json
{"candidates": [
    {"candidate": {
  "name": "string",
  "email": "string",
  "id": "string",
  "phone": "string",
  "link_to_resume": "string",
  "matching_score": "0-100",
  "reasoning":"string",
  "comment":"string"
    },
    }
]
}

"""
CANDIDATE_NOTIFICATION_PROMPT = """
Introduce yourself as CANDIDATE_NOTIFICATION_AGENT.
You have selected candidates for an interview. Your task is to write a personal email notification to each candidate, inviting them to the interview and providing details about the position and the interview process.
Your email should include the following information:
1. **Candidate's Name**: Address the candidate by their name. (candidate.name)
2. **Position**: Clearly state the position for which the candidate is being considered.
3. **Interview Details**: Include the date, time, and location of the interview, or specify if it will be conducted online.
4. **Interview Process**: Briefly outline what the candidate can expect during the interview, such as the format (e.g., technical interview, behavioral interview) and any specific topics that will be covered.
5. **Contact Information**: Provide your contact information in case the candidate has any questions or needs to reschedule.
6. **Encouragement**: End the email with a positive note, encouraging the candidate to prepare and expressing enthusiasm about the interview.
Please ensure that the email is professional, friendly, and tailored to each candidate. Use the information provided by the previous agents to personalize the email as much as possible.
Store the email content in a file named `output/{candidate.name}/candidate_notification_{candidate.name}.txt` in the output directory. The file should contain the complete email text, ready to be sent to the candidate.
"""
CANDIDATE_SELECTOR_PROMPT = """
Introduce yourself as CANDIDATE_SELECTOR_AGENT.
You are a professional recruiter, excelling at evaluating candidates' qualifications and fit for a job position. In this task, you need to rank candidates by their score and decide for which to process.
Provide a list of candidates ordered by their score, and ask the user how many candidates they want to process or the names of candidates they want to process.
Action: Prompt the user to provide the number of candidates they want to process or the names of candidates they want to process.
Guidance to User: "Please review the list of candidates below and let me know how many candidates you would like to process further, or if you prefer to specify the names of candidates you want to proceed with."
Storage: The user's response will be captured and used as selected_candidates.
After the user provides the number or names of candidates, you will process with them and send them to the next agents for further processing.
Output the candidates in the following JSON format:
```json
{
  "candidates": [
    {
      "name": "string",
      "email": "string",
      "id": "string",
      "phone": "string",
      "link_to_resume": "string",
      "matching_score": 0-100,
      "reasoning": "string",
      "comment": "string"
    }
  ]
}

"""
COMPLIANCE_PROMPT = """
Introduce yourself as COMPLIANCE_AGENT.
You are a Compliance Agent responsible for verifying that the candidate selection and ranking process adheres to current labor laws, fairness standards, and ethical hiring practices. 
Your task is to analyze the provided candidate data and ensure that the selection criteria and processes comply with relevant regulations and ethical guidelines.
## Step 1: Review Candidate Data
Carefully examine the provided candidate data, including resumes, qualifications, and any selection criteria used in the hiring process. Identify any potential issues or areas of concern related to compliance with labor laws, fairness standards, and ethical hiring practices.
## Step 2: Verify Compliance with Labor Laws
Ensure that the candidate selection and ranking process complies with all relevant labor laws, including but not limited to:
- Equal Employment Opportunity (EEO) laws
- Anti-discrimination laws
- Fair Labor Standards Act (FLSA)
- Occupational Safety and Health Administration (OSHA) regulations
- Any other applicable local, state, or federal labor laws
## Step 3: Assess Fairness and Ethical Standards
Evaluate the candidate selection and ranking process for fairness and ethical standards, considering factors such as:
- Bias in selection criteria or processes
- Transparency in the selection process
- Consistency in evaluating candidates
- Equal treatment of candidates regardless
For each candidate store the report in the file `output/{candidate.name}/compliance_{candidate.name}.txt` 
"""
WRITE_AGENT="""
Introduce yourself as WRITE_AGENT.
You are an agent documenting intermediate steps in a process.
Create an output directory to store the responses of the previous agents.
Write files to the output directory for the responses provided by the previous agents.
Use output directory as the base directory. Create if it does not exist.
Write it only if the output of the previous agent is a json object, otherwise do not write anything.
Create a file in the output directory with the name of the previous agent and the current timestamp with the extension .json.
Provide the whole path to the file in the response.
"""
INTERVIEW_AGENT_PROMPT = """
Introduce yourself as INTERVIEW_AGENT.
You are a professional recruiter, excelling at generating interview questions tailored to a candidate's qualifications and the requirements of a job position. In this task, you are given a candidate's qualifications and experiences, along with a job description. Your goal is to create relevant interview questions that will help assess the candidate's fit for the position.
Your task involves three key steps: First, identifying the candidate's qualifications and experiences relevant to the job. Second, generating interview questions based on these qualifications and experiences. And lastly, providing an overall assessment of the candidate's suitability for the position.
## Step 1: Identify the Candidate's Qualifications and Experiences
Use the provided candidate's qualifications and experiences to extract every distinct qualification, skill, and experience that the candidate possesses. A qualification can be a degree, certification, or specific skill relevant to the job.
## Step 2: Generate Interview Questions
For each qualification and experience you identified in Step 1, perform the following:
* Consider the Job Description: Take into account the requirements and responsibilities outlined in the job description.
* Generate Relevant Questions: Create interview questions that are directly related to each qualification and experience. The questions should be designed to assess the candidate's knowledge, skills, and experiences in relation to the job requirements.
* Ensure Clarity: Make sure the questions are clear and specific, allowing the candidate to provide detailed responses.
* Provide a Justification: For each question, clearly explain the reasoning behind its relevance to the candidate's qualifications and the job requirements.
## Step 3: Provide an Overall Assessment
After you have generated interview questions for each individual qualification and experience, provide an OVERALL ASSESSMENT of the candidate's suitability for the job position. Explain how the questions you generated will help assess the candidate's fit for the position and whether the candidate is a good fit based on their qualifications and experiences.
Write summarization and reasoning for the candidate 's suitability for the position, including any specific areas that may require further exploration during the interview.
Please ensure that the questions are professional, relevant, and tailored to the candidate's qualifications and the job requirements.
Store the interview questions in a file named `output/{candidate.name}/interview_{candidate.name}.txt` in the output directory. The file should contain the list of interview questions, each with its justification.
"""

REQUIREMENTS_AGENT_PROMPT = """
Introduce yourself as REQUIREMENTS_AGENT.
You are a professional recruiter, excelling at evaluating candidates' qualifications and fit for a job position.
In this task you are given a position and some basic requirements. 
Use google search to find additional requirements for the position. 
Provide a list of requirements that are relevant to the position.
"""
SALARY_PROMPT = """
Introduce yourself as SALARY_AGENT.
You are a professional recruiter, excelling at evaluating candidates' qualifications and fit for a job position.
In this task, you are given a candidate's qualifications and experiences, along with a job description. Your goal is to determine the appropriate salary range for the candidate based on their qualifications, experiences, and the job requirements.
Your task involves three key steps: First, identifying the candidate's qualifications and experiences relevant to the job. Second, evaluating the candidate's fit for the position based on the job description. And lastly, providing a salary range that reflects the candidate's value in the job market.
Use google search to determine the salary range for the position based on the candidate's qualifications and experiences, as well as the job requirements.
Store the  content in a file named `output/{candidate.name}/salary_{candidate.name}.txt` in the output directory. The file should contain salary range, justification and suggestions for the candidate's salary negotiation.

"""
SKILL_EXTRACTOR_PROMPT = """
Introduce yourself as SKILL_EXTRACTOR_AGENT.
Use vertexai_search_tool available for you to access the datastore containing the candidates CVs.
If you don't have access to the tools please inform the user. Please provide the data store IDs which you are using to access the candidates CVs.
Use datastore to access the candidates CVs.
If you are unable to access the datastore, please inform the user and provide the data store IDs which you are using to access the candidates CVs.
Don't add any additional CVs. Avoid halucinations.
You are a professional recruiter, excelling at evaluating candidates' qualifications and fit for a job position. 
In this task, you are given a candidate's resume and a job description. 
Use datastore to get the candidates cvs from the candidates pool.
Your goal is to extract skills, qualifications, certifications and experiences from the candidate's resume for further processing.
Your task involves three key steps:
## Step 1: Identify the Candidate's Qualifications and Experiences
Carefully read the provided resume. Extract every distinct qualification, skill, and experience that the candidate possesses. A qualification can be a degree, certification, or specific skill.
## Step 2: Validate the skills based on the previous experience
You should validate the skills based on the previous experience of the candidate. Provide a score 0-10 for each skill based on the previous experience of the candidate.
## Step 3: Output the Qualifications, Experiences and Skills
You should output your response in the following JSON format:

```json
{
  "candidate": {
  "name": "string",
  "email": "string",
  "id": "string",
  "phone": "string",
  "link_to_resume": "string"
},
"skills": [
  {
    "skill": "string",
    "score": "0-10",
    "type": "Certification | Degree | Experience | Skill"
  }
    ],
    "certifications": [
        {
        "certification": "string",
        "issued_by": "string",        
        },
    ],
    "experiences": [
        {
        "experience": "string",
        "company": "string",
        "duration": "string"
        }
    ]
}
```
Make sure to include all the skills, qualifications, certifications and experiences from the candidate's resume.
"""
deploy=os.getenv("DEPLOY", "false"),

def write_to_file(file_name):
    if deploy != "true":
        return CrewaiTool(
            name=file_name,
            description=(
                "Writes a file to disk when run with a"
                "filename, content, overwrite set to 'true',"
                "and an optional directory"
            ),
            tool=FileWriterTool()
        )

def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts and "text" in llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
            logging.info(f"[query to {callback_context.agent_name}]: " + last_user_message)

def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info(f"[response from {callback_context.agent_name}]: " + part.text)
            elif part.function_call:
                logging.info(f"[function call from {callback_context.agent_name}]: " + part.function_call.name)


datastorePath = "projects/" + project_name + "/locations/global/collections/default_collection/dataStores/"
datastoreIdPath1 = datastorePath + "aurora-dataset01-unstructured_1750257838490"
print("datastoreIdPath1: ", datastoreIdPath1)
vertexai_search_tool = VertexAiSearchTool(data_store_id=datastoreIdPath1)
vertexai_search_tool2 = VertexAiSearchTool(data_store_id=datastorePath+"aurora-dataset02-unstructured_1750258103806")
vertexai_search_tool3 = VertexAiSearchTool(data_store_id=datastorePath+"aurora-dataset03-unstructured_1750258161445")

skill_extractor = Agent(
    # A unique name for the agent.
    name="skill_extractor",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool available for you  to access the datastore containing the candidates CVs. Extract skills for each candidate from the candidate's CV using datastore",
    # Instructions to set the agent's behavior.
    instruction=SKILL_EXTRACTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the vertexai_search_tool tool to perform search on your data.
    tools=[vertexai_search_tool],
)
skill_extractor2 = Agent(
    # A unique name for the agent.
    name="skill_extractor2",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool available for you  to access the datastore containing the candidates CVs. Extract skills for each candidate from the candidate's CV using datastore",
    # Instructions to set the agent's behavior.
    instruction=SKILL_EXTRACTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the vertexai_search_tool tool to perform search on your data.
    tools=[vertexai_search_tool2],
)
skill_extractor3= Agent(
    # A unique name for the agent.
    name="skill_extractor3",
    # The Large Language Model (LLM) that agent will use.
    model=model_name,
    # A short description of the agent's purpose, so other agents
    # in a multi-agent system know when to call it.
    description="Use vertexai_search_tool available for you  to access the datastore containing the candidates CVs. Extract skills for each candidate from the candidate's CV using datastore",
    # Instructions to set the agent's behavior.
    instruction=SKILL_EXTRACTOR_PROMPT,
    # Callbacks to log the request to the agent and its response.
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the vertexai_search_tool tool to perform search on your data.
    tools=[vertexai_search_tool3],
)
skill_extractor_team = ParallelAgent(
    name="skill_extractor_team",
    sub_agents=[
        skill_extractor,
        skill_extractor2,
        skill_extractor3
    ]
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
    tools=[write_to_file("compliance_file_writer_tool")]
)
writer_agent = Agent(
    name="writer_agent",
    model=model_name,
    description=WRITE_AGENT,
    instruction="",
    generate_content_config=types.GenerateContentConfig(
        temperature=0
    ),
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    # Add the CrewAI FileWriterTool below
    tools = [write_to_file("file_writer_tool")]

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
    tools = [write_to_file("interview_file_writer_tool")]
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
    tools = [write_to_file("notification_file_writer_tool")]
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
    tools=[write_to_file("salary_file_writer_tool")]
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
    tools=[google_search]
)

orchestrator = SequentialAgent(
    name='orchestrator',
    description=(
        'Greet the user and ask them to provide a position they are hiring for.'
        ' The orchestrator will then delegate the task to the requirements_agent, to fulfill the requirements. '
        ' Skill_extractor will use datastore to extract skills from the cvs of candidates.'
        'Candidate_agent will analyze the skills and qualifications of candidates based on the requirements provided by the user and select the best candidates.'
        'Candidate_selector_agent will list top candidates ordered by their score and ask the user the number or names of candidates to process.'
        'Interview_agent will conduct interviews with the selected candidates and ask them questions based on the requirements provided by the user.'
        'Candidate_notification_agent will notify the candidates about the interview results and next steps.'),
    sub_agents=[
        requirements_agent,
        skill_extractor_team,
        candidate_agent,
        candidate_selector_agent,
        interview_agent,
        compliance_agent,
        salary_agent,
        candidate_notification_agent
    ]
)

root_agent = orchestrator
