"""Backend agent: content safety. Does not generate user-facing content; only evaluates draft text."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import LlmAgent
from src.prompt_loader import load_agent_prompt
from tools.mock_health_tools import verify_content_safety


def get_instruction() -> str:
    return load_agent_prompt("content_verifier_agent")


root_agent = LlmAgent(
    name="content_verifier_agent",
    model="gemini-2.5-flash",
    description=(
        "Backend agent specialized in content safety verification. "
        "Does NOT generate user-facing responses; only evaluates draft text for inappropriate content "
        "such as offensive, harmful or misleading diet/meal advice. "
        "Tools: verify_content_safety(text, context, strict_mode, return_categories_checked). "
        "Use parameterized calls, e.g. context='diet' and strict_mode=True, when verifying diet/meal advice."
    ),
    instruction=get_instruction(),
    tools=[verify_content_safety],
)
