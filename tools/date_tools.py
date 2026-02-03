"""Date/time helpers for period calculation and formatting."""

from datetime import datetime
from typing import Any, Dict
from tools.logged_tool import logged_tool


@logged_tool
def get_current_date() -> Dict[str, Any]:
    """Returns current date and time in ISO and readable formats. Use for period bounds and today's date."""
    now = datetime.now()
    return {
        "current_date_iso": now.strftime("%Y-%m-%d"),
        "current_datetime_iso": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "current_date_readable": now.strftime("%d/%m/%Y"),
        "current_datetime_readable": now.strftime("%d/%m/%Y %H:%M:%S"),
        "timestamp": now.timestamp(),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "weekday": now.strftime("%A"),
        "weekday_short": now.strftime("%a"),
    }


@logged_tool
def format_date_iso_to_dd_mm_yy(date_iso: str) -> str:
    """Converts an ISO date string to DD-MM-YY format. Use when presenting dates to the user."""
    try:
        if not date_iso or not isinstance(date_iso, str):
            return str(date_iso) if date_iso else ""
        normalized = date_iso.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            date_part = (normalized.split("T")[0] if "T" in normalized else normalized.split(" ")[0])[:10]
            if len(date_part) >= 10:
                return f"{date_part[8:10]}-{date_part[5:7]}-{date_part[2:4]}"
            return date_iso
        return f"{dt.day:02d}-{dt.month:02d}-{dt.year % 100:02d}"
    except Exception:
        return date_iso


@logged_tool
def calculate_days_between_dates(date_iso_start: str, date_iso_end: str) -> float:
    """Calculates the difference in days between two ISO dates. Use for period_days or range checks."""
    try:
        if not date_iso_start or not date_iso_end:
            return 0.0
        for s in (date_iso_start, date_iso_end):
            s = s.replace("Z", "+00:00")
        start_part = date_iso_start.split("T")[0][:10]
        end_part = date_iso_end.split("T")[0][:10]
        dt_start = datetime.strptime(start_part, "%Y-%m-%d")
        dt_end = datetime.strptime(end_part, "%Y-%m-%d")
        return (dt_end - dt_start).total_seconds() / 86400.0
    except Exception:
        return 0.0
