import unittest

from tools.terminology.snomed_laterality import build_lateralized_finding


VERSION = "http://snomed.info/sct/900000000000207008/version/20260701"


class SnomedLateralityTests(unittest.TestCase):
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
