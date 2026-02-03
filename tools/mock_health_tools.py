"""Health/diet tools for portfolio demo. All data is fake; no external APIs.
Tools are parameterized and use configurable limits via env: defaults and caps per tool.
Env vars: RECOMMENDATIONS_TOOL_LIMIT, RECOMMENDATIONS_DEFAULT_ITEMS; HEALTH_STATS_DEFAULT_DAYS, HEALTH_STATS_MAX_DAYS;
DIET_SUMMARY_DEFAULT_DAYS, DIET_SUMMARY_MAX_DAYS, DIET_SUMMARY_BREAKDOWN_MAX_DAYS."""

import os
from typing import Any, Dict, List, Optional
from tools.logged_tool import logged_tool
from tools.limit_cap import apply_limit_cap, apply_period_days_cap, get_breakdown_max_days


@logged_tool
def verify_content_safety(
    text: str,
    context: str = "diet",
    strict_mode: bool = False,
    return_categories_checked: bool = True,
) -> Dict[str, Any]:
    """Checks if the given text is appropriate: no offensive, harmful or misleading diet content.
    context: diet default for diet/meal advice, or general.
    strict_mode: if True, also flags borderline claims, e.g. strong medical language.
    return_categories_checked: if True, includes list of categories that were evaluated.
    Returns safe=True if OK; safe=False with issues list if something inappropriate is detected.
    Demo: always returns safe=True; structure simulates a real moderation API."""
    categories = ["offensive_language", "harmful_advice", "misleading_claims", "medical_claims"]
    if strict_mode:
        categories.append("borderline_medical")
    return {
        "safe": True,
        "checked": True,
        "issues": [],
        "summary": "Content checked. No inappropriate content detected.",
        "params_used": {"context": context, "strict_mode": strict_mode},
        "categories_checked": categories if return_categories_checked else None,
    }


@logged_tool
def get_healthy_recommendations(
    category: str = "general",
    diet_preference: str = "balanced",
    max_items: Optional[int] = None,
    exclude_allergens: Optional[str] = None,
    calorie_target: Optional[str] = None,
) -> Dict[str, Any]:
    """Returns mock healthy food and habit recommendations with parameterized filters.
    category: general, breakfast, lunch, dinner, snacks, exercise.
    diet_preference: balanced, vegetarian, low_carb, mediterranean.
    max_items: max recommendations to return. If None, uses RECOMMENDATIONS_DEFAULT_ITEMS from env, default 5.
    Cap: RECOMMENDATIONS_TOOL_LIMIT from env, default 10. For quick or brief requests pass lower max_items.
    exclude_allergens: comma-separated, e.g. nuts,dairy. Optional.
    calorie_target: optional low, medium, high for demo."""
    # Default when not specified; then cap from env RECOMMENDATIONS_TOOL_LIMIT and RECOMMENDATIONS_DEFAULT_ITEMS
    default_items = int(os.getenv("RECOMMENDATIONS_DEFAULT_ITEMS", "5") or 5)
    requested = default_items if max_items is None else max_items
    effective_limit = apply_limit_cap(requested, "RECOMMENDATIONS_TOOL_LIMIT", fallback_default=10)
    effective_limit = max(1, min(10, effective_limit))  # hard bounds between 1 and 10
    samples = {
        "general": [
            "Eat more vegetables and whole grains.",
            "Stay hydrated: aim for 6–8 glasses of water per day.",
            "Limit added sugars and processed foods.",
            "Include protein at each meal.",
            "Choose whole fruits over juice.",
            "Plan meals ahead to avoid impulse choices.",
            "Eat slowly and mindfully.",
            "Avoid skipping meals.",
        ],
        "breakfast": [
            "Oatmeal with berries and nuts.",
            "Greek yogurt with honey and seeds.",
            "Whole-grain toast with avocado and eggs.",
            "Smoothie with spinach, banana and almond milk.",
            "Scrambled eggs with vegetables.",
        ],
        "lunch": [
            "Salad with grilled chicken or chickpeas.",
            "Quinoa bowl with roasted vegetables.",
            "Lentil soup with whole-grain bread.",
            "Wrap with hummus and vegetables.",
            "Rice and beans with steamed greens.",
        ],
        "dinner": [
            "Baked fish with steamed vegetables.",
            "Stir-fried tofu with brown rice.",
            "Grilled chicken with sweet potato.",
            "Vegetable curry with basmati rice.",
            "Lean meat with salad and whole grain.",
        ],
        "snacks": [
            "Apple slices with almond butter.",
            "Carrot sticks with hummus.",
            "Handful of mixed nuts and dried fruit.",
            "Greek yogurt.",
            "Whole-grain crackers with cheese.",
        ],
        "exercise": [
            "30 minutes of brisk walking daily.",
            "Strength training 2–3 times per week.",
            "Stretching or yoga for flexibility.",
            "Cycling or swimming for cardio.",
            "Short walks after meals.",
        ],
    }
    recs = samples.get(category.lower(), samples["general"])
    recs = recs[:effective_limit]
    params_used = {
        "category": category,
        "diet_preference": diet_preference,
        "max_items": effective_limit,
        "exclude_allergens": exclude_allergens,
        "calorie_target": calorie_target,
    }
    return {
        "data_found": True,
        "recommendations": recs,
        "count": len(recs),
        "params_used": params_used,
        "limits_applied": {"max_items_cap": effective_limit},
        "summary": f"Demo recommendations for {category} and {diet_preference}, {len(recs)} items, limit applied. Demo data for portfolio.",
    }


@logged_tool
def get_health_stats(
    user_id: str = "demo-user",
    period_days: Optional[int] = None,
    metrics: Optional[str] = None,
    aggregate_by: str = "day",
) -> Dict[str, Any]:
    """Returns mock health statistics for a user. Parameterized by requested metrics and aggregation.
    user_id: identifier of the user, provided by orchestrator context.
    period_days: number of days to include. If None, uses HEALTH_STATS_DEFAULT_DAYS from env, default 7.
    Max: HEALTH_STATS_MAX_DAYS from env, default 90. For quick or brief use lower period_days, e.g. 3.
    metrics: comma-separated: meals, water, steps, sleep, activity. If omitted, all returned.
    aggregate_by: 'day' or 'week'. Default 'day'."""
    effective_days = apply_period_days_cap(
        period_days, "HEALTH_STATS_DEFAULT_DAYS", "HEALTH_STATS_MAX_DAYS"
    )
    all_stats = {
        "meals_logged": 18,
        "water_glasses_avg": 6,
        "steps_avg": 5200,
        "sleep_hours_avg": 7.2,
        "active_days": 5,
        "meals_per_day_avg": 2.6,
        "hydration_compliance_pct": 85,
    }
    metric_to_key = {
        "meals": "meals_logged",
        "water": "water_glasses_avg",
        "steps": "steps_avg",
        "sleep": "sleep_hours_avg",
        "activity": "active_days",
        "meals_logged": "meals_logged",
        "water_glasses_avg": "water_glasses_avg",
        "steps_avg": "steps_avg",
        "sleep_hours_avg": "sleep_hours_avg",
        "active_days": "active_days",
    }
    if metrics:
        requested = [m.strip().lower() for m in metrics.split(",")]
        keys_to_include = {metric_to_key.get(m, m) for m in requested if metric_to_key.get(m, m) in all_stats}
        if keys_to_include:
            all_stats = {k: v for k, v in all_stats.items() if k in keys_to_include}
    return {
        "data_found": True,
        "user_id": user_id,
        "period_days": effective_days,
        "aggregate_by": aggregate_by,
        "metrics_requested": metrics,
        "stats": all_stats,
        "limits_applied": {"period_days_default": os.getenv("HEALTH_STATS_DEFAULT_DAYS", "7"), "period_days_max": os.getenv("HEALTH_STATS_MAX_DAYS", "90")},
        "summary": f"Demo stats for user {user_id}, last {effective_days} days, aggregate by {aggregate_by}. Portfolio demo only.",
    }


@logged_tool
def get_user_diet_summary(
    user_id: str = "demo-user",
    period_days: Optional[int] = None,
    include_breakdown: bool = False,
    group_by: str = "day",
) -> Dict[str, Any]:
    """Returns mock diet/meal summary for a user. Parameterized by breakdown and grouping.
    user_id: identifier of the user.
    period_days: number of days. If None, uses DIET_SUMMARY_DEFAULT_DAYS from env, default 7.
    Max: DIET_SUMMARY_MAX_DAYS from env, default 90. For quick or brief use lower period_days.
    include_breakdown: if True, includes per-day or per-week breakdown as demo list.
    Breakdown length capped by DIET_SUMMARY_BREAKDOWN_MAX_DAYS from env, default 7, to limit response size.
    group_by: day or week when include_breakdown is True."""
    effective_days = apply_period_days_cap(
        period_days, "DIET_SUMMARY_DEFAULT_DAYS", "DIET_SUMMARY_MAX_DAYS"
    )
    breakdown_cap = get_breakdown_max_days()
    diet_summary = {
        "meals_per_day_avg": 3.2,
        "calories_estimate_avg": 1850,
        "water_glasses_avg": 6,
        "vegetables_servings_avg": 2.5,
        "protein_meals_pct": 78,
    }
    result = {
        "data_found": True,
        "user_id": user_id,
        "period_days": effective_days,
        "diet_summary": diet_summary,
        "limits_applied": {
            "period_days_default": os.getenv("DIET_SUMMARY_DEFAULT_DAYS", "7"),
            "period_days_max": os.getenv("DIET_SUMMARY_MAX_DAYS", "90"),
            "breakdown_max_days": breakdown_cap,
        },
        "summary": f"Demo diet summary for user {user_id}, last {effective_days} days. Demo only.",
    }
    if include_breakdown:
        result["breakdown"] = [
            {"period": f"Day {i}", "meals": 3, "calories_est": 1800 + (i % 3) * 50, "water_glasses": 6}
            for i in range(1, min(effective_days + 1, breakdown_cap + 1))
        ]
        result["breakdown_group_by"] = group_by
    return result
