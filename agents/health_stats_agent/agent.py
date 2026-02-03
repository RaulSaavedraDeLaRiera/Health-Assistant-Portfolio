"""Backend agent: user stats such as meals, water, steps, sleep. Does not resolve user identity; receives user_id from orchestrator."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import LlmAgent
from src.prompt_loader import load_agent_prompt
from tools.mock_health_tools import get_health_stats, get_user_diet_summary
from tools.date_tools import get_current_date, format_date_iso_to_dd_mm_yy, calculate_days_between_dates


def get_instruction() -> str:
    return load_agent_prompt("health_stats_agent")


root_agent = LlmAgent(
    name="health_stats_agent",
    model="gemini-2.5-flash",
    description=(
        "Backend agent specialized in user health and diet statistics: meals logged, water, steps, sleep, activity. "
        "Does NOT resolve user identity; receives user_id from the orchestrator context. "
        "Tools: get_health_stats(user_id, period_days, metrics, aggregate_by), "
        "get_user_diet_summary(user_id, period_days, include_breakdown, group_by), "
        "get_current_date(), format_date_iso_to_dd_mm_yy(date_iso), calculate_days_between_dates(start, end). "
        "Use parameterized calls, e.g. metrics, period_days, include_breakdown, when the user asks for specific stats or breakdowns."
    ),
    instruction=get_instruction(),
    tools=[
        get_health_stats,
        get_user_diet_summary,
        get_current_date,
        format_date_iso_to_dd_mm_yy,
        calculate_days_between_dates,
    ],
)
