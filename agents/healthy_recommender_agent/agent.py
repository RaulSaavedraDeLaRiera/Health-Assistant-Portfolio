"""Backend agent: diet and meal recommendations. Does not access user identity directly; receives context from orchestrator."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import LlmAgent
from src.prompt_loader import load_agent_prompt
from tools.mock_health_tools import get_healthy_recommendations
from tools.date_tools import get_current_date


def get_instruction() -> str:
    return load_agent_prompt("healthy_recommender_agent")


root_agent = LlmAgent(
    name="healthy_recommender_agent",
    model="gemini-2.5-flash",
    description=(
        "Backend agent specialized in diet and meal recommendations. "
        "Does NOT have direct access to user identity; receives user context from the orchestrator when needed. "
        "Tools: get_healthy_recommendations(category, diet_preference, max_items, exclude_allergens, calorie_target), "
        "get_current_date(). Use parameterized calls, e.g. max_items, exclude_allergens, when the user request implies filters."
    ),
    instruction=get_instruction(),
    tools=[get_healthy_recommendations, get_current_date],
)
