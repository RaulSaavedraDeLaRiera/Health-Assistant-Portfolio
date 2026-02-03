"""Tests for date tools: get_current_date, format_date_iso_to_dd_mm_yy, calculate_days_between_dates."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.date_tools import (
    get_current_date,
    format_date_iso_to_dd_mm_yy,
    calculate_days_between_dates,
)

print("=" * 80)
print("TESTS: date_tools")
print("=" * 80)

all_passed = True


# --- get_current_date ---
print("\n--- get_current_date ---")
try:
    r = get_current_date()
    assert "current_date_iso" in r
    assert "current_datetime_iso" in r
    assert "current_date_readable" in r
    assert "timestamp" in r
    assert "year" in r and "month" in r and "day" in r
    assert "weekday" in r
    print("  OK returns all expected keys")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False


# --- format_date_iso_to_dd_mm_yy ---
print("\n--- format_date_iso_to_dd_mm_yy ---")
test_cases = [
    ("2025-11-25T16:06:09Z", "25-11-25"),
    ("2025-09-11T10:00:00Z", "11-09-25"),
    ("2025-10-01T08:15:48Z", "01-10-25"),
    ("2025-11-25T16:06:09.029395+00:00", "25-11-25"),
    ("2025-09-11T10:00:00.000000+00:00", "11-09-25"),
    ("2025-10-15T10:00:00Z", "15-10-25"),
]
for date_iso, expected in test_cases:
    try:
        result = format_date_iso_to_dd_mm_yy(date_iso)
        if result != expected:
            print(f"  ERROR {date_iso}: expected {expected}, got {result}")
            all_passed = False
        else:
            print(f"  OK {date_iso} -> {result}")
    except Exception as e:
        print(f"  ERROR {date_iso}: {e}")
        all_passed = False


# --- calculate_days_between_dates ---
print("\n--- calculate_days_between_dates ---")
try:
    d = calculate_days_between_dates("2025-09-01T00:00:00Z", "2025-09-11T00:00:00Z")
    assert abs(d - 10.0) < 0.01
    print("  OK 2025-09-01 to 2025-09-11 -> 10 days")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    d = calculate_days_between_dates("2025-10-01T12:00:00Z", "2025-10-02T12:00:00Z")
    assert abs(d - 1.0) < 0.01
    print("  OK same time next day -> 1 day")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    d = calculate_days_between_dates("2025-11-20T00:00:00Z", "2025-11-25T00:00:00Z")
    assert abs(d - 5.0) < 0.01
    print("  OK 2025-11-20 to 2025-11-25 -> 5 days")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False


print("\n" + "=" * 80)
if all_passed:
    print("[OK] All date_tools tests passed!")
else:
    print("[ERROR] Some tests failed!")
print("=" * 80)
