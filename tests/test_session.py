from runtime.session import InterviewSession

def test_acute_common_cold_branch_after_safety_gate():
    s = InterviewSession("acute")
    state = s.process("I have had a cough for 4 days.")
    assert state["selected_question"]["fact_id"] == "symptom.dyspnea"
    state = s.process("No.")
    assert "infectious.common_cold" not in state["active_patterns"]
    assert state["selected_question"]["fact_id"] == "symptom.rhinorrhea"
    state = s.process("Yes.")
    assert "infectious.common_cold" not in state["active_patterns"]
    assert state["selected_question"]["fact_id"] == "symptom.sore_throat"
    state = s.process("Yes.")
    assert "infectious.common_cold" in state["active_patterns"]

def test_chronic_branch_interleaves_common_causes():
    s = InterviewSession("chronic")
    state = s.process("I have had a cough for 3 months.")
    assert state["selected_question"]["fact_id"] == "symptom.dyspnea"
    state = s.process("No.")
    assert "gastrointestinal.gerd_cough" not in state["active_patterns"]
    assert state["selected_question"]["fact_id"] == "symptom.postnasal_drip"
    state = s.process("No.")
    assert state["selected_question"]["fact_id"] == "symptom.wheeze"
    state = s.process("No.")
    assert state["selected_question"]["fact_id"] == "medication.ace_inhibitor_exposure"
    state = s.process("No.")
    assert state["selected_question"]["fact_id"] == "symptom.heartburn"
    state = s.process("Yes.")
    assert "gastrointestinal.gerd_cough" in state["active_patterns"]

def test_gerd_is_not_a_diagnosis_output():
    s = InterviewSession("gerd")
    s.process("I have had a cough for 3 months.")
    state = s.process("No.")
    assert all(not p.startswith("diagnosis.") for p in state["active_patterns"])

def test_declined_answer_preserves_data_absent_reason():
    s = InterviewSession("declined")
    state = s.process("I have had a cough for 4 days.")
    assert state["selected_question"]["fact_id"] == "symptom.dyspnea"
    state = s.process("I prefer not to answer.")
    record = state["facts"]["symptom.dyspnea"]
    assert record["status"] == "unknown"
    assert record["value"] is None
    assert record["dataAbsentReason"]["code"] == "asked-declined"
