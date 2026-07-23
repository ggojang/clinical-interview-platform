"""Validation helpers for the official LOINC Answer List reference catalog."""
from __future__ import annotations

import re
from typing import Any


LOINC_SYSTEM_URL = "http://loinc.org"
LOINC_ANSWER_LIST_AGGREGATE_URL = "http://loinc.org/vs/ll"
LOINC_ANSWER_LIST_CANONICAL_PREFIX = "http://loinc.org/vs/"
CODE_PATTERN = re.compile(r"^LL[0-9]+-[0-9]+$")


class LoincAnswerListCatalogError(ValueError):
    """Raised when a catalog is incomplete or internally inconsistent."""


def answer_list_canonical(code: str) -> str:
    if not CODE_PATTERN.fullmatch(code):
        raise LoincAnswerListCatalogError(
            f"invalid LOINC Answer List identifier: {code}"
        )
    return LOINC_ANSWER_LIST_CANONICAL_PREFIX + code


def validate_catalog(catalog: dict[str, Any]) -> dict[str, int]:
    if catalog.get("id") != "catalog.loinc-answer-lists":
        raise LoincAnswerListCatalogError("unexpected catalog id")
    if catalog.get("status") != "research_only":
        raise LoincAnswerListCatalogError("catalog must remain research_only")
    if catalog.get("review_status") != "unreviewed":
        raise LoincAnswerListCatalogError("catalog must remain unreviewed")
    if catalog.get("aggregate_canonical") != LOINC_ANSWER_LIST_AGGREGATE_URL:
        raise LoincAnswerListCatalogError("unexpected aggregate canonical")
    entries = catalog.get("entries")
    if not isinstance(entries, list) or not entries:
        raise LoincAnswerListCatalogError("catalog entries are missing")
    declared_total = catalog.get("total")
    if declared_total != len(entries):
        raise LoincAnswerListCatalogError(
            "declared total does not match catalog entries"
        )
    codes: set[str] = set()
    canonicals: set[str] = set()
    membership_total = 0
    for entry in entries:
        code = entry.get("code")
        canonical = entry.get("canonical")
        member_count = entry.get("member_count")
        if not isinstance(code, str) or canonical != answer_list_canonical(code):
            raise LoincAnswerListCatalogError(
                f"invalid catalog entry: {entry!r}"
            )
        if code in codes or canonical in canonicals:
            raise LoincAnswerListCatalogError(
                f"duplicate catalog entry: {code}"
            )
        if not isinstance(member_count, int) or member_count <= 0:
            raise LoincAnswerListCatalogError(
                f"invalid member count for {code}"
            )
        codes.add(code)
        canonicals.add(canonical)
        membership_total += member_count
    if catalog.get("membership_total") != membership_total:
        raise LoincAnswerListCatalogError(
            "declared membership total does not match entries"
        )
    return {
        "answer_list_count": len(entries),
        "membership_total": membership_total,
    }
