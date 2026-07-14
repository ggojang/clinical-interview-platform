from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.session import InterviewSession
from runtime.simulator import PatientSimulator

def run(case_name: str):
    case = json.loads((ROOT / "simulation/patients/respiratory" / case_name).read_text(encoding="utf-8"))
    patient = PatientSimulator(case)
    session = InterviewSession(case["id"])
    utterance = patient.initial()
    transcript = [{"speaker":"patient","text":utterance}]

    for _ in range(12):
        state = session.process(utterance)
        q = state["selected_question"]
        if not q:
            break
        transcript.append({"speaker":"interviewer","text":q["text"],"reason":q["reason"]})
        utterance = patient.answer(q["fact_id"])
        transcript.append({"speaker":"patient","text":utterance})

    return {"case": case["id"], "transcript": transcript, "final_state": state}

for filename in ["COUGH-COLD-001.json", "COUGH-GERD-001.json"]:
    result = run(filename)
    print("=" * 72)
    print(result["case"])
    for turn in result["transcript"]:
        reason = f" [{turn['reason']}]" if "reason" in turn else ""
        print(f"{turn['speaker'].upper()}: {turn['text']}{reason}")
    print("ACTIVE:", result["final_state"]["active_patterns"])
