import unittest

from tools.terminology.snomed_laterality import (
    assess_lateralizable_site,
    build_lateralized_finding,
)


VERSION = "http://snomed.info/sct/900000000000207008/version/20260701"


class SnomedLateralityTests(unittest.TestCase):
    @staticmethod
    def _lookup(code="117590005", *, inactive=False, version=VERSION):
        parameters = [
            {"name": "code", "valueCode": code},
            {"name": "display", "valueString": "Ear structure (body structure)"},
            {"name": "version", "valueString": version},
        ]
        parameters.append({
            "name": "property",
            "part": [
                {"name": "code", "valueCode": "inactive"},
                {"name": "value", "valueBoolean": inactive},
            ],
        })
        return {"resourceType": "Parameters", "parameter": parameters}

    @staticmethod
    def _membership(code="117590005", *, member_view_active=False):
        return {"content": [{
            "refset": {"id": "723264001"},
            "referencedComponent": {"id": code, "name": "Ear structure"},
            "referencedComponentActive": member_view_active,
        }]}

    def test_membership_requires_separate_active_lookup_and_mrcm(self):
        result = assess_lateralizable_site(
            finding_site_code="117590005",
            membership_response=self._membership(member_view_active=False),
            lookup_response=self._lookup(),
            finding_site_attribute_allowed=True,
            expected_terminology_version=VERSION,
        )
        self.assertTrue(result["membership_row_present"])
        self.assertFalse(result["member_view_active_field_is_authoritative"])
        self.assertTrue(result["lookup_active"])
        self.assertTrue(result["laterality_question_eligible"])

    def test_nonmember_inactive_or_wrong_version_is_not_eligible(self):
        cases = [
            ({"content": []}, self._lookup(), True, VERSION),
            (self._membership(), self._lookup(inactive=True), True, VERSION),
            (self._membership(), self._lookup(), False, VERSION),
            (self._membership(), self._lookup(), True, VERSION + "-different"),
        ]
        for membership, lookup, mrcm, version in cases:
            with self.subTest(mrcm=mrcm, version=version):
                result = assess_lateralizable_site(
                    finding_site_code="117590005",
                    membership_response=membership,
                    lookup_response=lookup,
                    finding_site_attribute_allowed=mrcm,
                    expected_terminology_version=version,
                )
                self.assertFalse(result["laterality_question_eligible"])
                self.assertEqual(
                    result["fallback"],
                    "preserve_separate_site_and_laterality_facts",
                )

    def test_left_is_nested_on_finding_site(self):
        result = build_lateralized_finding(
            focus_code="301354004",
            finding_site_code="117590005",
            laterality="left",
            terminology_version=VERSION,
            refset_member=True,
            finding_site_attribute_allowed=True,
        )
        self.assertEqual(result["finding_site"]["lateralizable_refset_id"], "723264001")
        self.assertEqual(result["laterality"]["input_qualifier_code"], "7771000")
        self.assertIn("363698007 = ( 117590005 : 272741003 = 7771000 )", result["classifiable_expression"])
        self.assertFalse(result["bilateral_expanded_to_left_and_right"])

    def test_bilateral_expands_to_separate_left_and_right_groups(self):
        result = build_lateralized_finding(
            focus_code="301354004",
            finding_site_code="117590005",
            laterality="bilateral",
            terminology_version=VERSION,
            refset_member=True,
            finding_site_attribute_allowed=True,
        )
        expression = result["classifiable_expression"]
        self.assertIn("272741003 = 7771000", expression)
        self.assertIn("272741003 = 24028007", expression)
        self.assertNotIn("272741003 = 51440002", expression)
        self.assertTrue(result["bilateral_expanded_to_left_and_right"])

    def test_nonmember_and_already_lateralized_sites_are_rejected(self):
        common = dict(
            focus_code="301354004",
            finding_site_code="117590005",
            laterality="right",
            terminology_version=VERSION,
            finding_site_attribute_allowed=True,
        )
        with self.assertRaises(ValueError):
            build_lateralized_finding(**common, refset_member=False)
        with self.assertRaises(ValueError):
            build_lateralized_finding(
                **common, refset_member=True, finding_site_already_lateralized=True
            )

    def test_different_repeated_finding_sites_are_rejected(self):
        with self.assertRaises(ValueError):
            build_lateralized_finding(
                focus_code="288228002",
                finding_site_code="14975008",
                laterality="left",
                terminology_version=VERSION,
                refset_member=True,
                finding_site_attribute_allowed=True,
                finding_sites_in_normal_form=2,
                repeated_finding_sites_identical=False,
            )


if __name__ == "__main__":
    unittest.main()
