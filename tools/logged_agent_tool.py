"""Wrapper for AgentTool with optional debug logging."""

from __future__ import annotations
import os
from typing import Any
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext


def _tools_debug_enabled() -> bool:
    return (
        os.getenv("TOOLS_DEBUG", "FALSE").upper() == "TRUE"
        or os.getenv("DEBUG_INFO", "FALSE").upper() == "TRUE"
    )


def _tool_name(t: Any) -> str:
    name = getattr(t, "name", None)
    if isinstance(name, str) and name:
        return name
    fn_name = getattr(t, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name
    return type(t).__name__


_PRINTED_AGENT_TOOLSETS: set = set()


def _maybe_print_agent_toolset(agent: Any) -> None:
    if not _tools_debug_enabled():
        return
    agent_name = getattr(agent, "name", None) or "<unknown-agent>"
    if agent_name in _PRINTED_AGENT_TOOLSETS:
        return
    tools = getattr(agent, "tools", None) or []
    try:
        tool_names = [_tool_name(t) for t in tools]
    except Exception:
        tool_names = ["<error>"]
    print(f"[TOOLS_DEBUG] Agent '{agent_name}' tools={tool_names}")
    _PRINTED_AGENT_TOOLSETS.add(agent_name)


class LoggedAgentTool(AgentTool):
    async def run_async(self, *, args: dict, tool_context: ToolContext) -> Any:
        _maybe_print_agent_toolset(getattr(self, "agent", None))
        if _tools_debug_enabled():
            preview = ""
            try:
                if isinstance(args, dict) and "request" in args and isinstance(args["request"], str):
                    preview = args["request"][:500].replace("\n", "\\n")
            except Exception:
                pass
            print(f"[TOOLS_DEBUG] AgentTool -> {self.name} request_preview='{preview}'")
        result = await super().run_async(args=args, tool_context=tool_context)
        return result
