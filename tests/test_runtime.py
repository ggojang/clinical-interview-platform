from runtime.core import run_turn

def test_cough_demo_prioritizes_breathing():
    result = run_turn("test", "I have had a cough for about 5 days.")
    assert result["active_patterns"] == ["respiratory.cough"]
    assert result["selected_question"]["fact_id"] == "symptom.dyspnea"

def test_severe_dyspnea_escalates():
    result = run_turn("test", "I have a cough and it is very hard to breathe.")
    assert result["safety_status"]["level"] == "emergency"
