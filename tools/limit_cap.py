"""Configurable limits and caps per tool, env-based.

Rules: same idea as production.
- Each tool has its own cap or default via env, e.g. RECOMMENDATIONS_TOOL_LIMIT, HEALTH_STATS_MAX_DAYS.
- If cap is set: limit=None uses default; limit > cap is clamped to cap; limit <= cap is respected.
- If cap not set or 0: use sensible in-code default and max.

Used for: max_items for recommendations, period_days for stats or diet summary, breakdown length.
"""

from __future__ import annotations

import os
from typing import Optional


def _parse_int(raw: str, default: Optional[int] = None) -> Optional[int]:
    raw = (raw or "").strip()
    if not raw:
        return default
    try:
        v = int(raw)
        return v if v > 0 else default
    except Exception:
        return default


def apply_limit_cap(limit: Optional[int], tool_cap_env_var: str, fallback_default: int = 10) -> int:
    """Apply cap to a limit, e.g. max_items. If limit is None, use cap as default.
    If limit > cap, clamp to cap. Returns effective limit, always an int.
    Env var e.g. RECOMMENDATIONS_TOOL_LIMIT: max allowed; when limit is None this value is used as default too."""
    cap = _parse_int(os.getenv(tool_cap_env_var, ""), default=None)
    if cap is None:
        return limit if limit is not None else fallback_default
    if limit is None:
        return cap
    return min(limit, cap)


def apply_period_days_cap(
    period_days: Optional[int],
    default_days_env: str,
    max_days_env: str,
    min_days: int = 1,
) -> int:
    """Apply default and max to period_days, e.g. last X days. If period_days is None, use default from env.
    Clamp result to min_days and max_from_env. Returns effective period_days, always an int."""
    default = _parse_int(os.getenv(default_days_env, ""), default=7)
    max_days = _parse_int(os.getenv(max_days_env, ""), default=90)
    default = default if default is not None else 7
    max_days = max_days if max_days is not None else 90
    effective = period_days if period_days is not None else default
    return max(min_days, min(max_days, effective))


def get_breakdown_max_days(env_var: str = "DIET_SUMMARY_BREAKDOWN_MAX_DAYS") -> int:
    """Max number of rows to return in a breakdown, e.g. per-day. Prevents huge lists."""
    return _parse_int(os.getenv(env_var, ""), default=7) or 7
