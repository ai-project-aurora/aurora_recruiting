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

from .sub_agents.candidate_agent.agent import candidate_agent
from .sub_agents.crewai_tool_agent.agent import writer_agent
from .sub_agents.skill_extractor.agent import skill_extractor

sys.path.append("..")


orchestrator = SequentialAgent(
    name='orchestrator',
    description=(
        'Greet the user and ask them to provide requirements for the candidate.'
        ' The orchestrator will then delegate the task to the candidate agent, which will search for relevant information in the CV pool set data store.'
        'Next, the skill extractor will extract skills for each candidate from the candidate\'s CV using the datastore.'
    ),
    sub_agents=[skill_extractor,candidate_agent, writer_agent],
)

root_agent = orchestrator
