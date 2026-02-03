"""Tests for health/diet tools with different parameter combinations.
Tests the real tool functions used by the app: recommendations, stats, diet summary, content safety."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.mock_health_tools import (
    verify_content_safety,
    get_healthy_recommendations,
    get_health_stats,
    get_user_diet_summary,
)

print("=" * 80)
print("TESTS: health_tools")
print("=" * 80)

all_passed = True


# --- verify_content_safety ---
print("\n--- verify_content_safety ---")
try:
    r = verify_content_safety("Hello, eat more vegetables.")
    assert r.get("safe") is True and r.get("checked") is True
    assert "params_used" in r
    print("  OK default diet strict_mode=False")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    r = verify_content_safety("Sample text", context="general", strict_mode=True)
    assert r.get("safe") is True
    assert r.get("params_used", {}).get("strict_mode") is True
    assert "borderline_medical" in (r.get("categories_checked") or [])
    print("  OK context=general, strict_mode=True")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False


# --- get_healthy_recommendations ---
print("\n--- get_healthy_recommendations ---")
for category in ("general", "breakfast", "lunch", "dinner", "snacks", "exercise"):
    try:
        r = get_healthy_recommendations(category=category, diet_preference="balanced")
        assert r.get("data_found") is True
        assert "recommendations" in r and len(r["recommendations"]) >= 1
        assert r.get("params_used", {}).get("category") == category
        print(f"  OK category={category}")
    except Exception as e:
        print(f"  ERROR category={category}: {e}")
        all_passed = False

try:
    r = get_healthy_recommendations("breakfast", "vegetarian", max_items=3, exclude_allergens="nuts", calorie_target="low")
    assert r.get("data_found") is True
    assert len(r["recommendations"]) <= 3
    assert r["params_used"].get("diet_preference") == "vegetarian"
    assert r["params_used"].get("exclude_allergens") == "nuts"
    print("  OK parametrized (max_items=3, vegetarian, exclude_allergens, calorie_target)")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    r = get_healthy_recommendations("lunch", max_items=None)
    assert r.get("data_found") is True
    assert "recommendations" in r
    print("  OK max_items=None uses default")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False


# --- get_health_stats ---
print("\n--- get_health_stats ---")
try:
    r = get_health_stats("user-1", period_days=7)
    assert r.get("data_found") is True
    assert r.get("user_id") == "user-1"
    assert r.get("period_days") == 7
    assert "stats" in r and len(r["stats"]) >= 1
    print("  OK user_id, period_days=7")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    r = get_health_stats("user-2", period_days=None, metrics="meals,steps", aggregate_by="week")
    assert r.get("data_found") is True
    assert "stats" in r
    assert r.get("aggregate_by") == "week"
    assert r.get("metrics_requested") == "meals,steps"
    print("  OK period_days=None, metrics=meals,steps, aggregate_by=week")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    r = get_health_stats("user-3", period_days=30, metrics="water,sleep")
    assert r.get("data_found") is True
    assert r.get("period_days") == 30
    print("  OK period_days=30, metrics=water,sleep")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False


# --- get_user_diet_summary ---
print("\n--- get_user_diet_summary ---")
try:
    r = get_user_diet_summary("user-1", period_days=7)
    assert r.get("data_found") is True
    assert "diet_summary" in r
    assert "breakdown" not in r
    print("  OK without breakdown")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    r = get_user_diet_summary("user-2", period_days=14, include_breakdown=True, group_by="day")
    assert r.get("data_found") is True
    assert "breakdown" in r
    assert r.get("breakdown_group_by") == "day"
    assert len(r["breakdown"]) >= 1
    print("  OK with breakdown, group_by=day")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False

try:
    r = get_user_diet_summary("user-3", period_days=None, include_breakdown=True, group_by="week")
    assert r.get("data_found") is True
    assert "breakdown" in r
    assert r.get("breakdown_group_by") == "week"
    print("  OK period_days=None, include_breakdown=True, group_by=week")
except Exception as e:
    print(f"  ERROR: {e}")
    all_passed = False


print("\n" + "=" * 80)
if all_passed:
    print("[OK] All health_tools tests passed!")
else:
    print("[ERROR] Some tests failed!")
print("=" * 80)
