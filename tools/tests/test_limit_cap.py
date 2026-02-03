"""Tests for limit_cap: apply_limit_cap, apply_period_days_cap, get_breakdown_max_days."""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.limit_cap import apply_limit_cap, apply_period_days_cap, get_breakdown_max_days

print("=" * 80)
print("TESTS: limit_cap")
print("=" * 80)

all_passed = True

# Save env to restore later
saved = {}
env_vars = [
    "RECOMMENDATIONS_TOOL_LIMIT",
    "HEALTH_STATS_DEFAULT_DAYS",
    "HEALTH_STATS_MAX_DAYS",
    "DIET_SUMMARY_BREAKDOWN_MAX_DAYS",
]
for k in env_vars:
    saved[k] = os.environ.pop(k, None)


def restore_env():
    for k, v in saved.items():
        if v is not None:
            os.environ[k] = v
        elif k in os.environ:
            del os.environ[k]


try:
    # --- apply_limit_cap, no env set, use fallback ---
    print("\n--- apply_limit_cap, no env ---")
    r = apply_limit_cap(5, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    assert r == 5
    print("  OK limit=5 -> 5, no cap set")

    r = apply_limit_cap(None, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    assert r == 10
    print("  OK limit=None -> fallback_default=10")

    r = apply_limit_cap(100, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    assert r == 100
    print("  OK limit=100 -> 100, no cap")

    # --- apply_limit_cap with env set ---
    os.environ["RECOMMENDATIONS_TOOL_LIMIT"] = "8"
    r = apply_limit_cap(5, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    assert r == 5
    print("  OK limit=5, cap=8 -> 5")

    r = apply_limit_cap(20, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    assert r == 8
    print("  OK limit=20, cap=8 -> 8, clamped")

    r = apply_limit_cap(None, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    assert r == 8
    print("  OK limit=None, cap=8 -> 8, default")

    del os.environ["RECOMMENDATIONS_TOOL_LIMIT"]

    # --- apply_period_days_cap, no env, use in-code default and max ---
    print("\n--- apply_period_days_cap, no env ---")
    r = apply_period_days_cap(7, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS")
    assert r == 7
    print("  OK period_days=7 -> 7")

    r = apply_period_days_cap(None, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS")
    assert r == 7
    print("  OK period_days=None -> default 7")

    r = apply_period_days_cap(50, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS")
    assert r == 50
    print("  OK period_days=50 -> 50")

    r = apply_period_days_cap(200, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS")
    assert r == 90
    print("  OK period_days=200 -> 90 (clamped to max)")

    # --- apply_period_days_cap with env set ---
    os.environ["HEALTH_STATS_DEFAULT_DAYS"] = "14"
    os.environ["HEALTH_STATS_MAX_DAYS"] = "30"
    r = apply_period_days_cap(None, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS")
    assert r == 14
    print("  OK period_days=None, default_env=14 -> 14")

    r = apply_period_days_cap(100, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS")
    assert r == 30
    print("  OK period_days=100, max_env=30 -> 30, clamped")

    del os.environ["HEALTH_STATS_DEFAULT_DAYS"]
    del os.environ["HEALTH_STATS_MAX_DAYS"]

    # --- get_breakdown_max_days ---
    print("\n--- get_breakdown_max_days ---")
    r = get_breakdown_max_days()
    assert r == 7
    print("  OK no env -> 7")

    os.environ["DIET_SUMMARY_BREAKDOWN_MAX_DAYS"] = "14"
    r = get_breakdown_max_days()
    assert r == 14
    print("  OK env=14 -> 14")

    del os.environ["DIET_SUMMARY_BREAKDOWN_MAX_DAYS"]

except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False
finally:
    restore_env()


print("\n" + "=" * 80)
if all_passed:
    print("[OK] All limit_cap tests passed!")
else:
    print("[ERROR] Some tests failed!")
print("=" * 80)
