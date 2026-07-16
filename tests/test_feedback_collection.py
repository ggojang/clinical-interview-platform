from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FeedbackCollectionTests(unittest.TestCase):
    def test_feedback_action_is_separate_and_consent_gated(self):
        config = json.loads(
            (ROOT / "docs/gpt/custom-gpt-config.json").read_text(encoding="utf-8")
        )
        policy = config["anonymous_test_feedback"]
        self.assertEqual(policy["operation"], "submitAnonymousTestFeedback")
        self.assertTrue(policy["send_only_after_separate_affirmative_answer"])
        self.assertTrue(policy["completion_confirmation_is_not_feedback_consent"])
        self.assertFalse(policy["contains_raw_answers"])
        self.assertFalse(policy["contains_free_text"])
        self.assertTrue(policy["requires_editor_action_install_and_save"])

    def test_session_start_analytics_is_content_free_and_first_message_only(self):
        config = json.loads(
            (ROOT / "docs/gpt/custom-gpt-config.json").read_text(encoding="utf-8")
        )
        policy = config["anonymous_test_session_analytics"]
        self.assertEqual(policy["operation"], "recordAnonymousTestSessionStart")
        self.assertEqual(policy["trigger"], "once_after_first_user_message")
        self.assertFalse(policy["is_consequential"])
        self.assertTrue(policy["notice_required_before_call"])
        self.assertFalse(policy["literal_page_open_observable"])
        self.assertFalse(policy["contains_user_message"])
        self.assertFalse(policy["contains_reason_for_encounter"])
        self.assertFalse(policy["contains_demographics_or_identifiers"])
        self.assertFalse(policy["contains_network_identity"])

    def test_tracked_entry_counts_page_opens_without_identity(self):
        config = json.loads(
            (ROOT / "docs/gpt/custom-gpt-config.json").read_text(encoding="utf-8")
        )
        policy = config["anonymous_test_entry_analytics"]
        self.assertEqual(
            policy["url"],
            "https://clinical-interview-feedback.seungjong-yu.workers.dev/test",
        )
        self.assertEqual(policy["event_type"], "tracked_entry_opened")
        self.assertTrue(policy["counts_page_opens_not_unique_people"])
        self.assertFalse(policy["direct_gpt_page_open_observable"])
        self.assertFalse(policy["contains_user_input_or_answers"])
        self.assertFalse(policy["contains_network_identity_or_cookie"])

    def test_openapi_schema_has_no_free_text_or_patient_payload(self):
        schema = (
            ROOT / "services/feedback-worker/openapi.template.yaml"
        ).read_text(encoding="utf-8")
        property_lines = {
            line.strip().split(":", 1)[0]
            for line in schema.splitlines()
            if line.startswith("        ") and not line.startswith("          ")
        }
        for forbidden in (
            "answer", "answers", "transcript", "comment", "free_text",
            "name", "email", "phone", "age", "sex", "birth_date", "file",
        ):
            self.assertNotIn(forbidden, property_lines)
        self.assertIn("additionalProperties: false", schema)
        self.assertIn("consent: {type: boolean, const: true}", schema)
        self.assertIn("operationId: recordAnonymousTestSessionStart", schema)
        self.assertIn("event_type: {type: string, const: session_started}", schema)
        self.assertIn("x-openai-isConsequential: false", schema)
        self.assertIn("x-openai-isConsequential: true", schema)

    def test_openapi_renderer_requires_and_applies_https_origin(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "feedback.yaml"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/feedback/render_openapi.py"),
                    "--base-url", "https://feedback.test.invalid",
                    "--output", str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            rendered = output.read_text(encoding="utf-8")
            self.assertIn("https://feedback.test.invalid", rendered)
            self.assertNotIn("FEEDBACK_API_HOST", rendered)

    def test_worker_does_not_log_or_store_network_identity(self):
        worker = (ROOT / "services/feedback-worker/src/index.js").read_text(
            encoding="utf-8"
        )
        migration = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "services/feedback-worker/migrations").glob("*.sql"))
        )
        self.assertNotIn("console.", worker)
        for forbidden in ("ip_address", "user_agent", "transcript", "raw_text"):
            self.assertNotIn(forbidden, migration.lower())
        self.assertIn('url.pathname === "/test"', worker)
        self.assertIn("tracked_entry_opened", worker)

    def test_stats_client_uses_live_endpoint_and_non_default_user_agent(self):
        client = (ROOT / "tools/feedback/fetch_stats.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "https://clinical-interview-feedback.seungjong-yu.workers.dev",
            client,
        )
        self.assertIn("ClinicalInterviewResearchStats/1.0", client)
        self.assertIn("feedback-admin-key", client)

    def test_privacy_notice_discloses_retention_and_non_collection(self):
        notice = (ROOT / "docs/gpt/privacy-policy.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("separately agrees", notice)
        self.assertIn("90 days", notice)
        self.assertIn("does not accept answers", notice)
        self.assertIn("abandoned", notice)
        self.assertIn("first user message", notice)
        self.assertIn("dedicated research-test entry page", notice)
        self.assertIn("Opening the direct GPT URL bypasses this counter", notice)


if __name__ == "__main__":
    unittest.main()
