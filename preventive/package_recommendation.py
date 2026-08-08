"""Deterministic comparison of screening-center add-on packages."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


def compare_add_on_packages(
    packages: list[dict[str, Any]],
    need_tags: set[str],
    *,
    national_baseline_items: set[str],
    voluntary_budget: int | float | None = None,
) -> dict[str, Any]:
    """Compare current catalog entries without inferring ability to pay.

    This function ranks catalog facts; it does not diagnose, determine medical
    necessity, or invent package contents. A caller must provide a versioned
    center catalog and a versioned recommendation policy.
    """
    evaluated: list[dict[str, Any]] = []
    for package in packages:
        required = {"id", "display_ko", "price_krw", "item_ids", "need_tags"}
        if not required <= set(package):
            raise ValueError(f"package is missing required fields: {package.get('id')}")
        items = set(package["item_ids"])
        matched = sorted(need_tags.intersection(package["need_tags"]))
        incremental = sorted(items - national_baseline_items)
        duplicates = sorted(items.intersection(national_baseline_items))
        evaluated.append({
            "package_id": package["id"],
            "display_ko": package["display_ko"],
            "price_krw": package["price_krw"],
            "matched_need_tags": matched,
            "incremental_item_ids": incremental,
            "duplicate_national_item_ids": duplicates,
            "within_voluntary_budget": (
                None if voluntary_budget is None
                else package["price_krw"] <= voluntary_budget
            ),
            "catalog_entry": deepcopy(package),
        })
    suitable = [
        item for item in evaluated
        if item["matched_need_tags"] and item["incremental_item_ids"]
    ]
    suitable.sort(key=lambda item: (-len(item["matched_need_tags"]), item["price_krw"], item["package_id"]))
    cheapest = min(suitable, key=lambda item: (item["price_krw"], item["package_id"])) if suitable else None
    best_match = suitable[0] if suitable else None
    selected_ids = []
    for item in (cheapest, best_match):
        if item and item["package_id"] not in selected_ids:
            selected_ids.append(item["package_id"])
    return {
        "recommendation_status": "candidate_comparison",
        "independent_diagnosis_or_treatment": False,
        "economic_capacity_inferred": False,
        "national_screening_assumed_baseline": True,
        "lowest_cost_suitable_package_id": cheapest["package_id"] if cheapest else None,
        "best_match_package_id": best_match["package_id"] if best_match else None,
        "presented_candidate_ids": selected_ids,
        "evaluated_packages": evaluated,
    }
