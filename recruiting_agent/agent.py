# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

from google.adk.agents import SequentialAgent


import sys

from sub_agents.candidate_agent.agent import candidate_agent
from sub_agents.candidate_notification_agent import candidate_notification_agent
from sub_agents.candidate_selector_agent import candidate_selector_agent
from sub_agents.compliance_agent import compliance_agent
from sub_agents.crewai_tool_agent.agent import writer_agent
from sub_agents.interview_agent.agent import interview_agent
from sub_agents.requirements_agent.agent import requirements_agent
from sub_agents.salary_agent import salary_agent
from sub_agents.skill_extractor.agent import skill_extractor

sys.path.append("..")


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
        skill_extractor,
        candidate_agent,
        candidate_selector_agent,
        interview_agent,
        compliance_agent,
        salary_agent,
        candidate_notification_agent],
)

root_agent = orchestrator
