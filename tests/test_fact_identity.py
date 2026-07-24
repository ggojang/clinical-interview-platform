from __future__ import annotations

import unittest
from collections import defaultdict

from builder.build_knowledge import PROFILES
from compiler.build_package import compile_package


class CrossPackageFactIdentityTest(unittest.TestCase):
    def test_shared_fact_ids_keep_one_value_semantics(self):
        occurrences: dict[str, list[tuple[str, dict]]] = defaultdict(list)
        for profile in sorted(PROFILES):
            package = compile_package(profile=profile)
            for node in package["knowledge_graph"]["nodes"]:
                if node.get("type") == "Fact":
                    occurrences[node["id"]].append((profile, node))

        conflicts = {}
        for fact_id, rows in occurrences.items():
            value_types = {node.get("value_type") for _, node in rows}
            allowed_values = {
                tuple(node.get("allowed_values", []))
                for _, node in rows
                if node.get("value_type") == "coded"
            }
            if len(value_types) > 1 or len(allowed_values) > 1:
                conflicts[fact_id] = {
                    profile: {
                        "value_type": node.get("value_type"),
                        "allowed_values": node.get("allowed_values", []),
                    }
                    for profile, node in rows
                }

        self.assertEqual(conflicts, {})

    def test_recently_split_fact_ids_have_explicit_semantics(self):
        packages = {
            profile: compile_package(profile=profile)
            for profile in ("cough", "fever", "urinary_symptoms", "fatigue")
        }

        def fact(profile: str, fact_id: str) -> dict:
            return next(
                node for node in packages[profile]["knowledge_graph"]["nodes"]
                if node.get("type") == "Fact" and node["id"] == fact_id
            )

        self.assertEqual(
            fact("cough", "symptom.systemic_unwellness")["value_type"],
            "severity",
        )
        self.assertEqual(
            fact("fever", "symptom.systemically_unwell")["value_type"],
            "boolean",
        )
        self.assertEqual(
            fact("urinary_symptoms", "pregnancy.possibility_status")[
                "value_type"
            ],
            "coded",
        )
        self.assertEqual(
            fact("fatigue", "pain.nrs_score")["value_type"],
            "integer",
        )


if __name__ == "__main__":
    unittest.main()
