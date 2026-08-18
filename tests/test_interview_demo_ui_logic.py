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
        script = f"""
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
