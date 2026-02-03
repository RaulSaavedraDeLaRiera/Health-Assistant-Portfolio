"""Agent tools: wrap specialized agents as tools for the orchestrator."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.logged_agent_tool import LoggedAgentTool
from agents.healthy_recommender_agent.agent import root_agent as healthy_recommender_agent
from agents.health_stats_agent.agent import root_agent as health_stats_agent
from agents.content_verifier_agent.agent import root_agent as content_verifier_agent

healthy_recommender_agent_tool = LoggedAgentTool(agent=healthy_recommender_agent)
health_stats_agent_tool = LoggedAgentTool(agent=health_stats_agent)
content_verifier_agent_tool = LoggedAgentTool(agent=content_verifier_agent)
