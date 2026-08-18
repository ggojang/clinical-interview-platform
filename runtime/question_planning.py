"""Deterministic patient-facing question planning for adaptive interviews.

The compiler may use broad selector Facts to choose a conditional completion
branch.  Those Facts are useful implementation state, but selectors such as a
``primary_group`` commonly combine location, severity, timing and associated
symptoms.  Presenting them as one patient question violates the repository's
atomic-question contract.

This module keeps the distinction explicit:

* internal routing selectors are never patient-facing questions;
* ordinary scheduled interviews start with concise characterization axes;
* dedicated proactive safety screens can be deferred, while observed safety
  Facts continue to run through the safety Rule graph after every turn; and
* urgent/emergency contexts retain safety-first ordering.

No medical rule is created here.  The planner only orders or suppresses
questions already present in the immutable compiled Knowledge Package.
"""
from __future__ import annotations

from typing import Any


_INTERNAL_ROUTING_MARKERS = (
    ".primary_group",
    ".primary_context",
    ".primary_symptom_group",
    ".primary_concern_group",
    ".primary_follow_up_focus",
    ".primary_followup_context",
)


def ordered_unique(values: list[str]) -> list[str]:
    """Return stable first-seen order without using a set for presentation."""
    return list(dict.fromkeys(value for value in values if isinstance(value, str)))


def internal_routing_fact_ids(completion_policy: dict[str, Any]) -> set[str]:
    """Return conditional selectors that are broad internal routing state.

    Status, product-type, goal and other genuinely single-axis selectors remain
    patient-facing.  The markers below identify the generated broad clinical
    grouping selectors whose answer options intentionally combine meanings.
    """
    selectors = {
        item["selector_fact"]
        for item in completion_policy.get("conditional_required_facts", [])
        if isinstance(item, dict) and isinstance(item.get("selector_fact"), str)
    }
    return {
        fact_id
        for fact_id in selectors
        if any(marker in fact_id for marker in _INTERNAL_ROUTING_MARKERS)
        or fact_id in {
            "symptom.upper_respiratory.main_type",
            "symptom.urinary.presentation",
        }
    }


def is_core_characterization_fact(fact_id: str) -> bool:
    """Whether a Fact is an ordinary symptom-characterization axis.

    Some of these Facts also participate in safety Rules (for example sudden
    onset plus severe pain).  Their safety use must not turn the ordinary
    atomic question itself into a deferred red-flag screen.
    """
    low = fact_id.casefold()
    exact_suffixes = (
        ".location",
        ".severity",
        ".onset",
        ".duration",
        ".character",
        ".frequency",
        ".worsening",
        ".course",
        ".progression",
    )
    return (
        low in {"symptom.duration", "pain.nrs_score", "pain.frequency"}
        or low.endswith(exact_suffixes)
    )


def proactive_safety_fact_ids(package: dict[str, Any]) -> set[str]:
    """Return dedicated safety-screen Facts that may be deferred routinely.

    The compiler's ``always`` list contains both essential characterization
    axes and dedicated red-flag screens.  A Fact is treated as a proactive
    screen only when it participates in a safety Rule, is not part of the
    routine history list, and is not itself a core characterization axis.
    Explicit priority rules labelled safety/red-flag are also included.
    """
    policy = package.get("interview_completion_policy", {})
    configured = policy.get("required_facts", {})
    always = set(configured.get("always", []))
    routine = set(configured.get("routine", []))
    safety_inputs: set[str] = set()

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("fact"), str):
                safety_inputs.add(value["fact"])
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    indexes = package.get("indexes", {})
    target_facts = indexes.get("target_facts", {})
    explicit_priority_screens: set[str] = set()
    for rule in package.get("rule_graph", {}).get("rules", []):
        if rule.get("type") == "safety":
            collect(rule.get("when", {}))
        elif rule.get("type") == "priority":
            then = rule.get("then", {})
            reason = str(then.get("reason", "")).casefold()
            if "safety" in reason or "red_flag" in reason:
                explicit_priority_screens.update(
                    target_facts.get(then.get("target"), [])
                )

    dedicated = {
        fact_id
        for fact_id in safety_inputs
        if fact_id in always
        and fact_id not in routine
        and not is_core_characterization_fact(fact_id)
    }
    return dedicated | explicit_priority_screens


def semantic_question_rank(fact_id: str, target_id: str | None = None) -> int:
    """Return a stable clinical-history phase for one already-authored Fact.

    Lower values are asked earlier.  The rank is deliberately based on stable
    semantic identifiers rather than question prose or an LLM judgment.
    Priority Rule scores remain the deterministic tie-breaker inside a phase.
    """
    low = fact_id.casefold()
    target = (target_id or "").casefold()
    text = f"{low} {target}"

    # Exact core axes precede richer details on the same topic.
    if low.endswith(".location"):
        return 10
    if low.endswith(".severity"):
        return 20
    if low.endswith(".onset"):
        return 30
    if low == "symptom.duration" or low.endswith(".duration"):
        return 40
    if low.endswith(".character"):
        return 50
    # A standardized numeric pain score remains required when authored, but it
    # should not immediately repeat a just-answered categorical severity item.
    if low == "pain.nrs_score":
        return 55
    if low.endswith((".frequency", ".course", ".progression", ".worsening")):
        return 60

    if any(token in text for token in ("laterality", "exact_point", "site-detail")):
        return 65
    if any(token in text for token in ("radiation", "migration")):
        return 70
    if any(token in text for token in (
        "aggravat", "reliev", "trigger", "relationship", "relation",
        "precipitat", "provok",
    )):
        return 80
    if any(token in text for token in (
        "continuous", "episodic", "pattern", "trend", "timing",
        "date_time", "preceding_event",
    )):
        return 85
    if low.startswith("symptom."):
        return 90
    if any(token in text for token in (
        "function", "mobility", "selfcare", "sleep", "work", "school",
        "daily_activ",
    )):
        return 100
    if any(token in text for token in ("age", "life_stage", "baseline")):
        return 105
    if any(token in text for token in (
        "history", "prior_episode", "family", "occupation", "exposure",
        "travel", "surgery", "procedure",
    )):
        return 110
    if any(token in text for token in (
        "medicine", "medication", "drug", "allerg", "anticoagulant",
    )):
        return 120
    if any(token in text for token in (
        "prior_assessment", "prior-test", "imaging", "laboratory", "treatment",
        "therapy", "response",
    )):
        return 130
    if any(token in text for token in ("concern", "goal", "expectation")):
        return 140
    if any(token in text for token in (
        "information_source", "information-source", "proxy", "reliability",
    )):
        return 150
    return 95
