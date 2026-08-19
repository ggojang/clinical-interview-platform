from pathlib import Path
import unittest

from runtime.clinical_output import build_completed_clinical_outputs


ROOT = Path(__file__).resolve().parents[1]


class CompletedClinicalOutputTest(unittest.TestCase):
    def test_completed_conversation_becomes_chart_and_fhir_projection(self):
        conversation = [
            {"role": "user", "content": "기침이 나요"},
            {
                "role": "assistant",
                "content": (
                    "Q1. 기침은 언제 시작되었나요?\n"
                    "출처: [공동 작업 지식] question.symptom_onset"
                ),
            },
            {"role": "user", "content": "어제"},
            {
                "role": "assistant",
                "content": (
                    "Q2. 기침과 함께 가래가 있나요?\n"
                    "1 예\n2 아니오\n3 잘 모르겠음\n4 답변하지 않음\n"
                    "출처: [공동 작업 지식] question.symptom_sputum"
                ),
            },
            {"role": "user", "content": "2"},
            {
                "role": "assistant",
                "content": (
                    "Q3. 만 나이는 몇 세인가요?\n"
                    "출처: [공동 작업 지식] question.clinician-context.age"
                ),
            },
            {"role": "user", "content": "55"},
            {
                "role": "assistant",
                "content": (
                    "Q4. 앞 질문에 없었지만 의료진에게 꼭 전달할 내용이나 원하는 도움이 있나요?\n"
                    "출처: [공동 작업 지식] question.clinician-context.final-comment"
                ),
            },
            {"role": "user", "content": "없음"},
        ]
        output = build_completed_clinical_outputs(
            session_id="12345678-1234-1234-1234-123456789012",
            reason_for_encounter="rfe.cough",
            conversation=conversation,
            repository_root=ROOT,
        )

        handoff = output["clinical_handoff"]
        self.assertEqual(handoff["format"], "clinical_chart_note")
        self.assertIn("Chief Complaint: cough", handoff["chart_note_text"])
        self.assertNotIn("Q1", handoff["chart_note_text"])
        self.assertIn("Onset: 어제", handoff["chart_note_text"])

        questionnaire = output["questionnaire"]
        self.assertEqual(questionnaire["resourceType"], "Questionnaire")
        self.assertEqual(questionnaire["status"], "draft")
        age_item = next(item for item in questionnaire["item"] if item["linkId"] == "Q3")
        self.assertEqual(age_item["code"][0]["system"], "http://loinc.org")
        self.assertEqual(age_item["code"][0]["code"], "30525-0")

        response = output["questionnaire_response"]
        sputum = next(item for item in response["item"] if item["linkId"] == "Q2")
        self.assertEqual(
            sputum["answer"][0]["valueCoding"]["code"], "373067005"
        )
        self.assertEqual(output["sdc_extraction"]["status"], "draft_projection")
        resource_types = {
            entry["resource"]["resourceType"]
            for entry in output["sdc_extraction"]["bundle"]["entry"]
        }
        self.assertTrue({"Patient", "Encounter", "Observation"}.issubset(resource_types))

    def test_unknown_is_not_encoded_as_a_negative_answer(self):
        output = build_completed_clinical_outputs(
            session_id="87654321-1234-1234-1234-123456789012",
            reason_for_encounter="rfe.cough",
            conversation=[
                {"role": "user", "content": "기침"},
                {
                    "role": "assistant",
                    "content": (
                        "Q1. 기침과 함께 가래가 있나요?\n"
                        "1 예\n2 아니오\n3 잘 모르겠음\n4 답변하지 않음\n"
                        "출처: question.symptom_sputum"
                    ),
                },
                {"role": "user", "content": "3"},
            ],
            repository_root=ROOT,
        )
        answer = output["questionnaire_response"]["item"][0]["answer"][0]
        self.assertNotIn("valueCoding", answer)
        self.assertEqual(answer["extension"][0]["valueCode"], "unknown")


if __name__ == "__main__":
    unittest.main()
