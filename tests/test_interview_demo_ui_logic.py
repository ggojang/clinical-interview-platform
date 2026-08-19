from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APP_JS = REPOSITORY_ROOT / "services/interview_api/static/app.js"


@unittest.skipUnless(shutil.which("node"), "Node.js is required for browser logic regression")
class InterviewDemoUiLogicTests(unittest.TestCase):
    def test_clinical_material_mime_fallback_supports_scan_and_electronic_media(self):
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify([
  clinicalMaterialContentType({{name:'scan.dcm',type:''}}),
  clinicalMaterialContentType({{name:'result.json',type:'application/fhir+json'}}),
  clinicalMaterialContentType({{name:'note.txt',type:''}})
])`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(
            json.loads(completed.stdout),
            ["application/dicom", "application/fhir+json", "text/plain"],
        )

    def test_choice_prompt_does_not_repeat_button_labels_in_message(self):
        question = {
            "questionRef": "Q2",
            "text": "우선 비교하고 싶은 영역은 무엇인가요?",
            "options": [
                {"input": "1", "label": "기본·종합 검진"},
                {"input": "2", "label": "암 검진"},
            ],
            "sourceLabel": "[공동 작업 지식]",
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`adaptiveChoicePrompt(${{JSON.stringify({json.dumps(question)})}})`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertIn("아래 버튼에서 답변을 선택", completed.stdout)
        self.assertNotIn("기본·종합 검진", completed.stdout)
        self.assertNotIn("암 검진", completed.stdout)

    def test_slider_extensions_preserve_range_step_and_control(self):
        item = {
            "linkId": "pain-today",
            "type": "integer",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-sliderStepValue",
                    "valueInteger": 1,
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/minValue",
                    "valueInteger": 0,
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/maxValue",
                    "valueInteger": 10,
                },
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/questionnaire-item-control",
                                "code": "slider",
                            }
                        ]
                    },
                },
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify(numericControlConfig(${{JSON.stringify({json.dumps(item)})}}))`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(
            json.loads(completed.stdout),
            {"minimum": 0, "maximum": 10, "step": 1, "slider": True},
        )

    def test_empty_group_with_only_hidden_children_is_not_renderable(self):
        group = {
            "linkId": "nolf-assessment",
            "type": "group",
            "text": "[NOLF] Assessment",
            "item": [
                {
                    "linkId": "internal",
                    "type": "text",
                    "extension": [
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-hidden",
                            "valueBoolean": True,
                        }
                    ],
                }
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify(hasRenderableQuestionnaireContent(${{JSON.stringify({json.dumps(group)})}}))`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertFalse(json.loads(completed.stdout))

    def test_korean_ime_enter_does_not_submit_mid_composition(self):
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify([
  shouldSubmitOnEnter({{key:'Enter',isComposing:true,keyCode:229,repeat:false}}),
  shouldSubmitOnEnter({{key:'Enter',isComposing:false,keyCode:13,repeat:false}}),
  shouldSubmitOnEnter({{key:'Enter',isComposing:false,keyCode:13,repeat:true}})
])`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(json.loads(completed.stdout), [False, True, False])

    def test_quantity_answer_keeps_amount_and_questionnaire_unit_together(self):
        questionnaire_items = [
            {
                "linkId": "smoking-amount",
                "type": "quantity",
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption",
                        "valueCoding": {"code": "개비", "display": "개비"},
                    }
                ],
            },
            {
                "linkId": "alcohol-amount",
                "type": "quantity",
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption",
                        "valueCoding": {
                            "system": "http://unitsofmeasure.org",
                            "code": "{glass}",
                            "display": "잔",
                        },
                    },
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption",
                        "valueCoding": {"code": "병", "display": "병"},
                    },
                ],
            },
        ]
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
const result = vm.runInContext(`
  const items = ${{JSON.stringify({json.dumps(questionnaire_items)})}};
  const smokingUnits = quantityUnitOptions(items[0]);
  const alcoholUnits = quantityUnitOptions(items[1]);
  JSON.stringify({{
    smoking: typedStructuredAnswer(items[0], '10', smokingUnits[0]),
    alcohol: typedStructuredAnswer(items[1], '2', alcoholUnits[0]),
    fixedAlcohol: answerValue(items[1], '2 잔'),
    unitCounts: [smokingUnits.length, alcoholUnits.length]
  }});
`, context);
console.log(result);
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["unitCounts"], [1, 2])
        self.assertEqual(
            result["smoking"],
            {"valueQuantity": {"value": 10, "unit": "개비", "code": "개비"}},
        )
        self.assertEqual(
            result["alcohol"],
            {
                "valueQuantity": {
                    "value": 2,
                    "unit": "잔",
                    "system": "http://unitsofmeasure.org",
                    "code": "{glass}",
                }
            },
        )
        self.assertEqual(
            result["fixedAlcohol"],
            {
                "valueQuantity": {
                    "value": 2,
                    "unit": "잔",
                    "system": "http://unitsofmeasure.org",
                    "code": "{glass}",
                }
            },
        )

    def test_r4_questionnaire_unit_is_supported_as_fixed_quantity_unit(self):
        item = {
            "linkId": "duration",
            "type": "quantity",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-unit",
                    "valueCoding": {
                        "system": "http://unitsofmeasure.org",
                        "code": "a",
                        "display": "년",
                    },
                }
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify(quantityUnitOptions(${{JSON.stringify({json.dumps(item)})}}))`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(
            json.loads(completed.stdout),
            [{"system": "http://unitsofmeasure.org", "code": "a", "display": "년"}],
        )

    def test_answer_display_uses_korean_rendering_and_english_base_display(self):
        option = {
            "valueCoding": {
                "system": "http://snomed.info/sct",
                "code": "81680005",
                "display": "Neck pain",
                "_display": {
                    "extension": [
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/rendering-xhtml",
                            "valueString": "뒷목 통증",
                        }
                    ]
                },
            }
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(JSON.stringify([
  vm.runInContext(`displayAnswer(${{JSON.stringify({json.dumps(option)})}}, 'ko-KR')`, context),
  vm.runInContext(`displayAnswer(${{JSON.stringify({json.dumps(option)})}}, 'en-US')`, context)
]));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(json.loads(completed.stdout), ["뒷목 통증", "Neck pain"])

    def test_answer_display_supports_fhir_translation_extension(self):
        option = {
            "valueString": "Original text",
            "_valueString": {
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/translation",
                        "extension": [
                            {"url": "lang", "valueCode": "ko"},
                            {"url": "content", "valueString": "번역된 문구"},
                        ],
                    }
                ]
            },
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`displayAnswer(${{JSON.stringify({json.dumps(option)})}}, 'ko')`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(completed.stdout.strip(), "번역된 문구")

    def test_fixed_conversation_prompt_contains_current_and_total_number(self):
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`fixedPrompt({{text:'흡연 상태는 어떻게 되나요?',answerOption:[{{valueString:'현재 흡연'}}]}}, 2, 9)`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertTrue(completed.stdout.startswith("[3/9] "))
        self.assertIn("1. 현재 흡연", completed.stdout)

    def test_hidden_questionnaire_items_are_not_asked_or_counted(self):
        questionnaire = {
            "resourceType": "Questionnaire",
            "status": "active",
            "item": [
                {
                    "linkId": "internal-calculation",
                    "type": "string",
                    "extension": [
                        {
                            "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-hidden",
                            "valueBoolean": True,
                        }
                    ],
                },
                {"linkId": "visible-question", "text": "보이는 질문", "type": "string"},
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify({{
  all: answerBearingItems(${{JSON.stringify({json.dumps(questionnaire)})}}).map(item => item.linkId),
  active: activeAnswerBearingItems(${{JSON.stringify({json.dumps(questionnaire)})}}).map(item => item.linkId)
}})`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(
            json.loads(completed.stdout),
            {"all": ["visible-question"], "active": ["visible-question"]},
        )

    def test_adaptive_runtime_question_keeps_number_options_and_instruction(self):
        document = {
            "state": {
                "adapter_state": {
                    "selected_question": {
                        "question_ref": "Q7",
                        "target_id": "target.smoking_status",
                        "fact_id": "patient.smoking.status",
                        "template_id": "question.smoking_status",
                        "text": "흡연 상태를 선택해 주세요.",
                        "response_instruction_ko": "보기 번호 또는 상태를 입력해 주세요.",
                        "answer_options": [
                            {"input": "1", "display_ko": "현재 흡연", "internal_value": "current"},
                            {"input": "2", "display_ko": "과거 흡연", "internal_value": "former"},
                        ],
                    }
                }
            },
            "presentation": {"text": "흡연 상태를 선택해 주세요."},
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`(() => {{
  const question = adaptiveQuestion(${{JSON.stringify({json.dumps(document)})}});
  return JSON.stringify({{ question, prompt: adaptivePrompt(question) }});
}})()`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["question"]["questionRef"], "Q7")
        self.assertEqual(result["question"]["knowledgeFact"], "patient.smoking.status")
        self.assertIn("[Q7] 흡연 상태를 선택해 주세요.", result["prompt"])
        self.assertIn("1. 현재 흡연", result["prompt"])
        self.assertIn("응답 안내: 보기 번호 또는 상태를 입력해 주세요.", result["prompt"])
        self.assertIn("출처: [공동 작업 지식]", result["prompt"])

    def test_adaptive_selector_prefers_runtime_stem_and_keeps_absence_actions(self):
        document = {
            "state": {
                "adapter_state": {
                    "selected_question": {
                        "question_ref": "Q1",
                        "fact_id": "abdominal_pain.primary_group",
                        "text": "긴 원본 분류 질문",
                        "stem_text": "이번 복통은 어떤 상황에 가장 가깝나요?",
                        "answer_value_set": "https://example.org/ValueSet/abdominal-context",
                        "answer_options": [
                            {
                                "input": "1",
                                "display_ko": "갑자기 시작하거나 매우 심함",
                                "internal_value": "acute_sudden_or_severe",
                                "coding": {
                                    "system": "https://example.org/CodeSystem/local",
                                    "code": "abdominal--acute",
                                    "display": "acute_sudden_or_severe",
                                },
                            }
                        ],
                        "data_absent_actions": [
                            {
                                "input": "2",
                                "display_ko": "잘 모르겠음",
                                "answer_text": "잘 모르겠습니다",
                                "dataAbsentReason": "asked-unknown",
                            }
                        ],
                    }
                }
            },
            "presentation": {"text": "LLM이 길게 바꾼 설명"},
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`(() => {{
  const question = adaptiveQuestion(${{JSON.stringify({json.dumps(document)})}});
  return JSON.stringify({{ question, prompt: adaptivePrompt(question) }});
}})()`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script], check=True, capture_output=True, text=True,
            cwd=REPOSITORY_ROOT,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(
            result["question"]["text"], "이번 복통은 어떤 상황에 가장 가깝나요?"
        )
        self.assertEqual(result["question"]["type"], "open-choice")
        self.assertIn("1. 갑자기 시작하거나 매우 심함", result["prompt"])
        self.assertIn("2. 잘 모르겠음", result["prompt"])
        self.assertEqual(
            result["question"]["answerValueSet"],
            "https://example.org/ValueSet/abdominal-context",
        )

    def test_terminology_internal_code_is_not_a_patient_label(self):
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`JSON.stringify([
  patientSafeCodingLabel({{code:'fact--acute',display:'acute_sudden_or_severe'}}, 'ko-KR'),
  patientSafeCodingLabel({{
    code:'fact--acute', display:'Acute',
    designation:[{{language:'ko',value:'갑작스러운 증상'}}]
  }}, 'ko-KR')
])`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script], check=True, capture_output=True, text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(json.loads(completed.stdout), ["", "갑작스러운 증상"])

    def test_adaptive_free_text_question_uses_runtime_presentation_contract(self):
        document = {
            "state": {
                "adapter_state": {
                    "selected_question": {
                        "question_ref": "Q1",
                        "target_id": "target.cough_duration",
                        "fact_id": "symptom.duration",
                        "template_id": "question.symptom_duration",
                        "text": "How long have you had the cough?",
                        "display_suggestions": [
                            {"input": "1", "display_ko": "오늘부터", "answer_text": "1일"},
                            {"input": "2", "display_ko": "3일 정도", "answer_text": "3일"},
                        ],
                        "data_absent_actions": [
                            {"input": "5", "display_ko": "잘 모르겠음", "answer_text": "잘 모르겠습니다", "dataAbsentReason": "asked-unknown"},
                            {"input": "6", "display_ko": "답변하지 않음", "answer_text": "답변하지 않음", "dataAbsentReason": "asked-declined"},
                        ],
                        "response_instruction_ko": "번호로 답하거나 내용을 직접 입력해 주세요.",
                    }
                }
            },
            "presentation": {"text": "기침이 얼마나 지속되고 있나요?"},
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(`(() => {{
  const question = adaptiveQuestion(${{JSON.stringify({json.dumps(document)})}});
  return JSON.stringify({{ question, prompt: adaptivePrompt(question) }});
}})()`, context));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["question"]["type"], "string")
        self.assertEqual(result["question"]["answerOption"], [])
        self.assertEqual(
            [item["label"] for item in result["question"]["suggestions"]],
            ["오늘부터", "3일 정도"],
        )
        self.assertIn("1. 오늘부터", result["prompt"])
        self.assertIn("2. 3일 정도", result["prompt"])
        self.assertIn("5. 잘 모르겠음", result["prompt"])
        self.assertIn("6. 답변하지 않음", result["prompt"])
        self.assertNotIn("answerValueSet", result["question"])

    def test_adaptive_ui_does_not_invent_client_side_clinical_suggestions(self):
        source = APP_JS.read_text(encoding="utf-8")
        self.assertNotIn("inferredAdaptiveSuggestions", source)

    def test_fixed_skip_is_explicit_data_absence_not_negative_answer(self):
        response_item = {
            "linkId": "unknown-screening-answer",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/data-absent-reason",
                    "valueCode": "asked-unknown",
                }
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(
  `fixedAnswerSummary(${{JSON.stringify({json.dumps(response_item)})}})`,
  context
));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(completed.stdout.strip(), "답변할 수 없음(건너뜀)")

    def test_f677_autocomplete_control_is_not_generic_select(self):
        item = {
            "linkId": "f677-family-history-search",
            "type": "choice",
            "answerValueSet": "http://www.hl7korea.or.kr/fhir/krcore/ValueSet/krcore-kcd8-codes",
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl",
                    "valueCodeableConcept": {
                        "coding": [{"code": "autocomplete"}]
                    },
                }
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
console.log(vm.runInContext(
  `JSON.stringify({{control:questionnaireItemControlCode(${{JSON.stringify({json.dumps(item)})}}), searchable: structuredControl.toString().includes('structuredAutocompleteControl')}})`,
  context
));
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        self.assertEqual(
            json.loads(completed.stdout),
            {"control": "autocomplete", "searchable": True},
        )

    def test_enable_when_reveals_only_selected_repeated_body_area_questions(self):
        questionnaire = {
            "resourceType": "Questionnaire",
            "status": "draft",
            "item": [
                {
                    "linkId": "body-area",
                    "text": "현재 제일 불편한 부위를 선택해 주세요.",
                    "type": "choice",
                    "repeats": True,
                },
                {
                    "linkId": "neck-side",
                    "text": "불편한 부위가 어느쪽인가요?",
                    "type": "choice",
                    "enableWhen": [
                        {
                            "question": "body-area",
                            "operator": "=",
                            "answerCoding": {"system": "test", "code": "neck", "display": "Neck pain"},
                        }
                    ],
                },
                {
                    "linkId": "scapula-side",
                    "text": "불편한 부위가 어느쪽인가요?",
                    "type": "choice",
                    "enableWhen": [
                        {
                            "question": "body-area",
                            "operator": "=",
                            "answerCoding": {"system": "test", "code": "scapula", "display": "Scapula pain"},
                        }
                    ],
                },
            ],
        }
        script = fr"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8').replace(/initialize\(\);\s*$/, '');
const context = {{ console }};
vm.createContext(context);
vm.runInContext(source, context);
const result = vm.runInContext(`
  state.questionnaire = ${{JSON.stringify({json.dumps(questionnaire)})}};
  state.structuredAnswers = new Map();
  const ids = () => activeAnswerBearingItems(state.questionnaire).map((item) => item.linkId);
  const initial = ids();
  state.structuredAnswers.set('body-area', {{linkId:'body-area', answer:[{{valueCoding:{{system:'test',code:'neck'}}}}]}});
  const neck = ids();
  state.structuredAnswers.set('body-area', {{linkId:'body-area', answer:[{{valueCoding:{{system:'test',code:'neck'}}}},{{valueCoding:{{system:'test',code:'scapula'}}}}]}});
  const both = ids();
  state.structuredAnswers.set('neck-side', {{linkId:'neck-side', answer:[{{valueCoding:{{system:'test',code:'left'}}}}]}});
  state.structuredAnswers.set('body-area', {{linkId:'body-area', answer:[{{valueCoding:{{system:'test',code:'scapula'}}}}]}});
  pruneDisabledAnswers();
  JSON.stringify({{initial, neck, both, neckAnswerRetained:state.structuredAnswers.has('neck-side')}});
`, context);
console.log(result);
"""
        completed = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPOSITORY_ROOT,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["initial"], ["body-area"])
        self.assertEqual(result["neck"], ["body-area", "neck-side"])
        self.assertEqual(
            result["both"], ["body-area", "neck-side", "scapula-side"]
        )
        self.assertFalse(result["neckAnswerRetained"])


if __name__ == "__main__":
    unittest.main()
