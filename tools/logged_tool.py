"""Optional logging wrapper for tools. Enable with TOOLS_DEBUG=TRUE or DEBUG_INFO=TRUE."""

from __future__ import annotations
import inspect
import os
import time
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def tools_debug_enabled() -> bool:
    return (
        os.getenv("TOOLS_DEBUG", "FALSE").upper() == "TRUE"
        or os.getenv("DEBUG_INFO", "FALSE").upper() == "TRUE"
    )


def _truncate(s: str, max_len: int) -> str:
    return s[:max_len] + "…" if len(s) > max_len else s


def _safe_repr(value: Any, max_len: int = 300) -> str:
    try:
        if isinstance(value, str):
            return _truncate(value.replace("\n", "\\n"), max_len)
        return _truncate(repr(value), max_len)
    except Exception:
        return f"<{type(value).__name__}>"


def _summarize_result(result: Any) -> str:
    try:
        if isinstance(result, dict):
            return f"dict keys={list(result.keys())[:30]}"
        if isinstance(result, list):
            return f"list len={len(result)}"
        if isinstance(result, str):
            return f"str len={len(result)} preview='{_truncate(result.replace(chr(10), ' '), 200)}'"
        return type(result).__name__
    except Exception:
        return f"<{type(result).__name__}>"


def logged_tool(func: F) -> F:
    @wraps(func)
    def _wrapper(*args: Any, **kwargs: Any) -> Any:
        if tools_debug_enabled():
            args_preview = [_safe_repr(a, 120) for a in args[:10]]
            kwargs_preview = {k: _safe_repr(v, 120) for k, v in list(kwargs.items())[:30]}
            print(f"--- Tool: {func.__name__} called ---")
            print(f"args={args_preview} kwargs={kwargs_preview}")
        t0 = time.time()
        result = func(*args, **kwargs)
        if tools_debug_enabled():
            dt_ms = int((time.time() - t0) * 1000)
            print(f"--- Tool: {func.__name__} returned ({dt_ms}ms) --- {_summarize_result(result)}")
        return result
    return _wrapper  # type: ignore[return-value]
