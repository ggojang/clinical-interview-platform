from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.core import run_turn

utterance = "I have had a cough for about 5 days and I am bringing up some phlegm."
result = run_turn("demo-cough-001", utterance)
print(json.dumps(result, ensure_ascii=False, indent=2))
