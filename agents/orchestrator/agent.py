"""Orchestrator: entry point for diet/meal assistant; delegates to recommender, stats and content verifier."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import LlmAgent
from tools.agent_tools import (
    healthy_recommender_agent_tool,
    health_stats_agent_tool,
    content_verifier_agent_tool,
)
from tools.date_tools import get_current_date
from src.prompt_loader import load_agent_prompt


def get_orchestrator_instruction() -> str:
    return load_agent_prompt("orchestrator")


root_agent = LlmAgent(
    name="orchestrator",
    model="gemini-2.5-flash",
    description=(
        "Orchestrator agent: main entry point. "
        "Does NOT have direct access to user data or backend tools. "
        "Only coordinates and delegates to backend agents via tools: healthy_recommender_agent, "
        "health_stats_agent, content_verifier_agent. Helper: get_current_date."
    ),
    instruction=get_orchestrator_instruction(),
    tools=[
        healthy_recommender_agent_tool,
        health_stats_agent_tool,
        content_verifier_agent_tool,
        get_current_date,
    ],
    sub_agents=[],
)
