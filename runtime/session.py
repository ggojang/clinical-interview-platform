"""Package-driven multi-turn interview session.

This Runtime executes compiled repository knowledge. It does not query external
medical sources or create new medical rules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re

from runtime.memory import ClinicalMemory
from runtime.package import DEFAULT_PACKAGE, load_package


def duration_class(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    amount, unit = value.get("amount"), value.get("unit")
    if not isinstance(amount, (int, float)):
        return None
    multiplier = {"day": 1, "week": 7, "month": 30}.get(unit)
    if multiplier is None:
        return None
    days = amount * multiplier
    if days < 21:
        return "acute"
    if days <= 56:
        return "subacute"
    return "chronic"


def fact(value: Any, text: str, turn: int, confidence: float = .9) -> dict[str, Any]:
    return {
        "status": "known",
        "value": value,
        "raw_text": text,
        "confidence": confidence,
        "evidence": [{"speaker": "patient", "turn": turn, "text": text}],
    }


def extract(text: str, turn: int, expected_fact: str | None = None) -> dict[str, dict[str, Any]]:
    """Small replaceable extractor constrained to Fact identifiers in the package."""
    low = text.lower().strip()
    low_normalized = low.rstrip(".!?")
    out: dict[str, dict[str, Any]] = {}

    temperature = re.search(r"(\d{2}(?:\.\d+)?)\s*(?:°\s*)?(c|f|도)", low)
    if temperature:
        unit = "Cel" if temperature.group(2) in {"c", "도"} else "[degF]"
        out["observation.body_temperature"] = fact(
            {"amount": float(temperature.group(1)), "unit": unit}, text, turn, .97
        )

    match = re.search(r"(\d+)\s*(day|days|week|weeks|month|months)", low)
    if match:
        unit = match.group(2).rstrip("s")
        out["symptom.duration"] = fact(
            {"amount": int(match.group(1)), "unit": unit}, text, turn, .97
        )
    else:
        ko_match = re.search(r"(\d+)\s*(일|주|개월|달)", text)
        if ko_match:
            unit = {"일": "day", "주": "week", "개월": "month", "달": "month"}[ko_match.group(2)]
            out["symptom.duration"] = fact(
                {"amount": int(ko_match.group(1)), "unit": unit}, text, turn, .95
            )
        elif "yesterday" in low or "어제" in text:
            out["symptom.duration"] = fact({"amount": 1, "unit": "day"}, text, turn, .95)
        elif "닷새" in text:
            out["symptom.duration"] = fact({"amount": 5, "unit": "day"}, text, turn, .95)

    lexical_true = {
        "symptom.rhinorrhea": ["runny nose", "blocked nose", "stuffy nose", "콧물", "코막힘"],
        "symptom.sore_throat": ["sore throat", "scratchy throat", "목이 아", "목 아"],
        "symptom.sneezing": ["sneez", "재채기"],
        "symptom.fever": ["fever", "feverish", "열이", "발열"],
        "symptom.dyspnea": [
            "short of breath", "trouble breathing", "hard to breathe",
            "harder to breathe", "숨이 차", "숨쉬기 힘",
        ],
        "symptom.hemoptysis": ["coughing blood", "blood when", "피가 섞", "피를"],
        "symptom.chest_pain": ["chest pain", "가슴 통증", "가슴이 아"],
        "symptom.heartburn": ["heartburn", "burning in my chest", "속쓰림", "가슴이 타"],
        "symptom.regurgitation": ["sour fluid", "bitter fluid", "acid comes up", "신물이", "쓴물이"],
        "symptom.cough_after_meals": ["after meals", "after eating", "식후", "먹고 나면"],
        "symptom.cough_lying_down": ["lying down", "lie down", "누우면"],
        "symptom.wheeze": ["wheez", "whistling", "쌕쌕"],
        "symptom.cyanosis": ["blue lips", "blue skin", "grey lips", "lips have turned blue", "청색증", "입술이 파래"],
        "symptom.stridor": ["stridor", "noisy breathing in", "숨 들이쉴 때 소리"],
        "symptom.syncope": ["fainted", "passed out", "syncope", "실신", "기절"],
        "symptom.palpitations": ["palpitations", "heart racing", "heart flutter", "두근거"],
        "symptom.unilateral_leg_pain_swelling": ["one leg swollen", "one leg pain", "한쪽 다리가 붓", "한쪽 다리가 아"],
        "symptom.orthopnea": ["worse lying flat", "sleep propped up", "누우면 숨", "베개를 높여"],
        "symptom.paroxysmal_nocturnal_dyspnea": ["wake up short of breath", "wake gasping", "자다가 숨이 차"],
        "symptom.ankle_swelling": ["swollen ankles", "ankle swelling", "발목이 붓"],
        "symptom.postnasal_drip": ["draining into", "clear my throat", "후비루", "목 뒤로 넘어"],
        "exposure.sick_contact": ["sick contact", "someone around", "가족도 감기", "주변에 감기"],
    }
    explicit_negative = {
        "symptom.fever": ["no fever", "열은 없", "열이 없"],
        "symptom.dyspnea": ["not short of breath", "no trouble breathing", "숨은 안 차", "호흡곤란은 없"],
        "symptom.hemoptysis": ["no blood", "피는 없", "피가 안"],
        "symptom.chest_pain": ["no chest pain", "가슴 통증은 없"],
    }
    for fact_id, cues in lexical_true.items():
        negatives = explicit_negative.get(fact_id, [])
        if any(cue in low or cue in text for cue in negatives):
            out[fact_id] = fact(False, text, turn, .95)
        elif any(cue in low or cue in text for cue in cues):
            out[fact_id] = fact(True, text, turn, .88)

    if "symptom.dyspnea" in out and out["symptom.dyspnea"]["value"] is True:
        if any(cue in low for cue in ["very hard", "severe", "can't breathe", "cannot breathe"]) or "매우 힘" in text or "더 힘든" in text:
            out["symptom.dyspnea"]["value"] = "severe"
        elif any(cue in low for cue in ["moderate", "noticeable", "quite hard"]) or "꽤 힘" in text:
            out["symptom.dyspnea"]["value"] = "moderate"
        else:
            out["symptom.dyspnea"]["value"] = "mild"

    if expected_fact:
        yes = low_normalized in {"yes", "yeah", "yep", "네", "예", "맞아요", "조금 있어요"}
        no = low_normalized in {"no", "nope", "아니요", "없어요", "전혀 없어요"}
        if yes and expected_fact not in out:
            value: Any = "mild" if expected_fact == "symptom.dyspnea" else True
            out[expected_fact] = fact(value, text, turn, .90)
        if no:
            value: Any = "none" if expected_fact == "symptom.dyspnea" else False
            out[expected_fact] = fact(value, text, turn, .95)
        if (
            expected_fact == "patient.smoking.status"
            and low_normalized in {"current", "former", "never"}
        ):
            out[expected_fact] = fact(low_normalized, text, turn, .95)

    return out


def _condition_matches(condition: dict[str, Any], memory: ClinicalMemory) -> bool:
    if "all" in condition:
        return all(_condition_matches(item, memory) for item in condition["all"])
    fact_id = condition.get("fact")
    if fact_id:
        value = memory.value(fact_id)
        if "equals" in condition:
            return value == condition["equals"]
        if "in" in condition:
            return value in condition["in"]
    return False


@dataclass
class InterviewSession:
    session_id: str
    package_path: Path | str = DEFAULT_PACKAGE
    execution_mode: str = "research_test"
    reason_for_encounter: str | None = None
    max_turns: int = 40
    asked: list[str] = field(default_factory=list)
    active_patterns: list[str] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    last_question_fact: str | None = None
    package: dict[str, Any] = field(init=False)
    memory: ClinicalMemory = field(init=False)
    active_intents: list[str] = field(init=False, default_factory=list)
    active_targets: dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.package = load_package(self.package_path, self.execution_mode)
        package_rfes = self.package.get("scope", {}).get("reasons_for_encounter", [])
        if self.reason_for_encounter is None:
            if len(package_rfes) != 1:
                raise ValueError("Runtime requires one explicit Reason for Encounter")
            self.reason_for_encounter = package_rfes[0]
        if self.reason_for_encounter not in package_rfes:
            raise ValueError(
                f"Reason for Encounter {self.reason_for_encounter!r} is outside package scope"
            )
        self.memory = ClinicalMemory(
            self.session_id,
            self.package["package_id"],
            self.package["package_version"],
        )
        activation = [
            rule for rule in self.package["rule_graph"]["rules"]
            if rule["type"] == "activation"
            and rule.get("when", {}).get("rfe") == self.reason_for_encounter
        ]
        self.active_intents = sorted({
            intent
            for rule in activation
            for intent in rule.get("then", {}).get("activate_intents", [])
        })
        targets = self.package["indexes"]["intent_targets"]
        self.active_targets = {
            target: "active"
            for intent in self.active_intents
            for target in targets.get(intent, [])
        }

    @property
    def turn(self) -> int:
        return self.memory.turn

    @property
    def facts(self) -> dict[str, dict[str, Any]]:
        return self.memory.facts

    def process(self, patient_text: str) -> dict[str, Any]:
        turn = self.memory.next_turn()
        self.memory.observe(patient_text)
        additions = extract(patient_text, turn, self.last_question_fact)
        low = patient_text.lower().strip()
        low_normalized = low.rstrip(".!?")
        for node in self.package["knowledge_graph"]["nodes"]:
            if node["type"] != "Fact" or node["id"] in additions:
                continue
            cues = node.get("extraction_cues", [])
            if node.get("value_type") == "boolean" and any(
                cue.lower() in low and f"no {cue.lower()}" not in low
                for cue in cues
            ):
                additions[node["id"]] = fact(True, patient_text, turn, .78)

        if self.last_question_fact and self.last_question_fact not in additions:
            node = next(
                (
                    item for item in self.package["knowledge_graph"]["nodes"]
                    if item["id"] == self.last_question_fact
                ),
                None,
            )
            if node:
                allowed = node.get("allowed_values", [])
                normalized = low_normalized
                if normalized in allowed:
                    additions[self.last_question_fact] = fact(
                        normalized, patient_text, turn, .92
                    )
        if any(marker in patient_text.lower() for marker in ("i meant", "sorry, i meant")) or "정정" in patient_text or "아니, " in patient_text:
            for candidate in additions.values():
                candidate["correction"] = True
        merge_results: dict[str, str] = {}
        allowed_facts = {
            node["id"] for node in self.package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        for fact_id, candidate in additions.items():
            if fact_id in allowed_facts:
                merge_results[fact_id] = self.memory.merge(fact_id, candidate)
        if self.last_question_fact and self.last_question_fact not in additions:
            if low_normalized in {
                "i am not sure", "i'm not sure", "not sure",
                "모르겠어요", "잘 모르겠어요",
            }:
                self.memory.mark_absent(
                    self.last_question_fact, patient_text, "asked-unknown"
                )
                merge_results[self.last_question_fact] = "asked-unknown"
            elif low_normalized in {
                "i prefer not to answer", "i'd rather not answer",
                "prefer not to say", "답하고 싶지 않아요", "말하고 싶지 않아요",
            }:
                self.memory.mark_absent(
                    self.last_question_fact, patient_text, "asked-declined"
                )
                merge_results[self.last_question_fact] = "asked-declined"
            elif low_normalized in {
                "not applicable", "does not apply", "해당되지 않아요",
            }:
                self.memory.mark_absent(
                    self.last_question_fact, patient_text, "not-applicable"
                )
                merge_results[self.last_question_fact] = "not-applicable"

        classification = duration_class(self.memory.value("symptom.duration"))
        self._update_patterns(classification)
        self._update_target_states(classification)

        safety = self._safety()
        completion = self._completion(classification, safety)
        budget = self._question_budget(safety["level"])
        budget_reached = len(self.asked) >= budget
        question = None
        if (
            safety["level"] not in {"urgent", "emergency"}
            and not completion["complete"]
            and not budget_reached
            and turn < self.max_turns
        ):
            question = self._choose(
                classification, safety["level"], set(completion["required_facts"])
            )
        self.last_question_fact = question["fact_id"] if question else None
        if self.last_question_fact:
            self.asked.append(self.last_question_fact)

        stop_reason = None
        if safety["level"] in {"urgent", "emergency"}:
            stop_reason = f"{safety['level']}_escalation"
        elif completion["complete"]:
            stop_reason = (
                "required_targets_addressed_with_absent_data"
                if completion["data_absent_facts"]
                else "all_required_targets_resolved"
            )
        elif budget_reached:
            stop_reason = "question_budget_reached"
        elif turn >= self.max_turns:
            stop_reason = "maximum_turn_policy"
        elif question is None:
            stop_reason = "no_eligible_question"

        trace_entry = {
            "turn": turn,
            "observed": patient_text,
            "facts_added": list(additions),
            "merge_results": merge_results,
            "duration_class": classification,
            "active_intents": self.active_intents,
            "active_targets": dict(self.active_targets),
            "active_patterns": list(self.active_patterns),
            "safety": safety,
            "completion": completion,
            "selected_question": question,
            "stop_reason": stop_reason,
            "package": {
                "id": self.package["package_id"],
                "version": self.package["package_version"],
                "semantic_digest": self.package["semantic_digest"],
            },
        }
        self.trace.append(trace_entry)
        return self.snapshot(question, safety, classification, stop_reason, completion)

    def _update_patterns(self, classification: str | None) -> None:
        if self.reason_for_encounter == "rfe.fever":
            self._update_fever_patterns()
            return
        if self.reason_for_encounter == "rfe.dyspnea":
            self._update_dyspnea_patterns()
            return
        if self.reason_for_encounter == "rfe.abdominal_pain":
            self._update_abdominal_pain_patterns()
            return
        active = ["respiratory.cough"]
        cold_support = sum(
            self.memory.value(fact_id) is True
            for fact_id in (
                "symptom.rhinorrhea", "symptom.sore_throat", "symptom.sneezing",
                "exposure.sick_contact",
            )
        )
        if classification == "acute" and cold_support >= 2:
            active.append("infectious.common_cold")
        if classification in {"subacute", "chronic"}:
            if any(self.memory.value(item) is True for item in (
                "symptom.postnasal_drip", "symptom.rhinorrhea",
            )):
                active.append("upper_airway.uacs")
            if any(self.memory.value(item) is True for item in (
                "symptom.wheeze", "symptom.cough_nocturnal",
                "symptom.cough_exercise_trigger", "symptom.cough_cold_air_trigger",
            )):
                active.append("respiratory.asthma_features")
            if any(self.memory.value(item) is True for item in (
                "symptom.heartburn", "symptom.regurgitation",
                "symptom.cough_lying_down", "symptom.cough_after_meals",
            )):
                active.append("gastrointestinal.gerd_cough")
        self.active_patterns = active

    def _update_abdominal_pain_patterns(self) -> None:
        active = ["gastrointestinal.abdominal_pain"]
        if any(self.memory.value(item) is True for item in (
            "symptom.vomiting", "symptom.diarrhea", "symptom.constipation",
            "symptom.bloody_or_black_stool", "symptom.hematemesis",
            "symptom.unable_to_pass_stool_or_gas",
        )):
            active.append("abdominal_pain.gastrointestinal_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.urinary_symptoms", "symptom.unable_to_urinate",
        )):
            active.append("abdominal_pain.urinary_features")
        if self.memory.value("pregnancy.possible") == "possible" or any(
            self.memory.value(item) is True for item in (
                "symptom.missed_period", "symptom.vaginal_bleeding_or_discharge",
                "symptom.shoulder_tip_pain",
            )
        ):
            active.append("abdominal_pain.pregnancy_related_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.unintentional_weight_loss", "symptom.persistent_bloating",
            "symptom.early_satiety_or_appetite_loss",
        )):
            active.append("abdominal_pain.persistent_warning_features")
        self.active_patterns = active

    def _update_dyspnea_patterns(self) -> None:
        active = ["respiratory.dyspnea"]
        if any(self.memory.value(item) is True for item in (
            "symptom.wheeze", "symptom.cough", "symptom.sputum",
        )):
            active.append("dyspnea.airway_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.orthopnea", "symptom.paroxysmal_nocturnal_dyspnea",
            "symptom.ankle_swelling",
        )):
            active.append("dyspnea.congestion_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.pleuritic_chest_pain", "symptom.hemoptysis",
            "symptom.unilateral_leg_pain_swelling",
            "risk.recent_immobility_or_surgery", "history.venous_thromboembolism",
        )):
            active.append("dyspnea.thromboembolic_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.cyanosis", "symptom.confusion", "symptom.syncope",
            "symptom.stridor",
        )) or self.memory.value("symptom.dyspnea") == "severe":
            active.append("dyspnea.immediate_safety_features")
        self.active_patterns = active

    def _update_fever_patterns(self) -> None:
        active = ["systemic.fever"]
        if any(self.memory.value(item) is True for item in (
            "symptom.confusion", "symptom.severe_pain", "symptom.systemic_unwellness",
        )):
            active.append("fever.systemic_infection_warning")
        if any(self.memory.value(item) is True for item in (
            "symptom.headache", "symptom.neck_stiffness", "symptom.non_blanching_rash",
        )):
            active.append("fever.meningitis_warning")
        if any(self.memory.value(item) is True for item in (
            "symptom.cough", "symptom.sore_throat", "symptom.dyspnea",
        )):
            active.append("fever.respiratory_source_features")
        if self.memory.value("symptom.urinary_symptoms") is True:
            active.append("fever.urinary_source_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.abdominal_pain", "symptom.vomiting", "symptom.diarrhea",
        )):
            active.append("fever.gastrointestinal_source_features")
        if self.memory.value("symptom.skin_infection_features") is True:
            active.append("fever.skin_source_features")
        self.active_patterns = active

    def _update_target_states(self, classification: str | None) -> None:
        for target, facts in self.package["indexes"]["target_facts"].items():
            branches: set[str] = set()
            for rule in self.package["rule_graph"]["rules"]:
                if rule["type"] != "priority" or rule.get("then", {}).get("target") != target:
                    continue
                requirement = rule.get("when", {}).get("duration_class")
                if isinstance(requirement, str):
                    branches.add(requirement)
                elif isinstance(requirement, dict):
                    branches.update(requirement.get("in", []))
                else:
                    branches.add("any")
            if classification == "acute" and branches and "any" not in branches and "acute" not in branches:
                self.active_targets[target] = "not_applicable"
                continue
            if classification in {"subacute", "chronic"} and branches and "any" not in branches and not branches.intersection({"subacute", "chronic"}):
                self.active_targets[target] = "not_applicable"
                continue
            states = [self.memory.state(fact_id) for fact_id in facts]
            if "conflicted" in states:
                self.active_targets[target] = "conflicted"
            elif states and all(state == "known" for state in states):
                self.active_targets[target] = "satisfied"
            elif states and all(
                state in {"known", "unknown", "not_applicable"} for state in states
            ):
                self.active_targets[target] = "unresolved"
            else:
                self.active_targets[target] = "active"

    def _required_facts(
        self, classification: str | None, safety: dict[str, Any]
    ) -> list[str]:
        policy = self.package["interview_completion_policy"]
        configured = policy.get("required_facts", {})
        required = set(configured.get("always", []))
        if safety["level"] == "clarify":
            followups = policy.get("clarification_facts_by_rule", {})
            for rule_id in safety["triggered_rules"]:
                required.update(followups.get(rule_id, []))
        elif classification:
            required.update(configured.get("routine", []))
            required.update(configured.get(classification, []))
        else:
            required.update(configured.get("routine", []))
        return sorted(required)

    def _completion(
        self, classification: str | None, safety: dict[str, Any]
    ) -> dict[str, Any]:
        required = self._required_facts(classification, safety)
        known = [fact_id for fact_id in required if self.memory.state(fact_id) == "known"]
        absent = [
            fact_id for fact_id in required
            if self.memory.state(fact_id) in {"unknown", "not_applicable"}
        ]
        conflicted = [
            fact_id for fact_id in required if self.memory.state(fact_id) == "conflicted"
        ]
        missing = [
            fact_id for fact_id in required
            if self.memory.state(fact_id) not in {
                "known", "unknown", "not_applicable", "conflicted"
            }
        ]
        return {
            "complete": bool(required) and not missing and not conflicted,
            "required_facts": required,
            "known_facts": known,
            "data_absent_facts": absent,
            "missing_facts": missing,
            "conflicted_facts": conflicted,
        }

    def _question_budget(self, safety_level: str) -> int:
        policy = self.package["interview_completion_policy"]
        budgets = policy.get("question_budget", {})
        return int(budgets.get("clarify" if safety_level == "clarify" else "routine", 18))

    def _safety(self) -> dict[str, Any]:
        matched = []
        level_order = {"routine": 0, "clarify": 1, "urgent": 2, "emergency": 3}
        level = "routine"
        action = None
        for rule in self.package["rule_graph"]["rules"]:
            if rule["type"] != "safety":
                continue
            if _condition_matches(rule["when"], self.memory):
                matched.append(rule["id"])
                candidate = rule["then"]["safety_level"]
                if level_order[candidate] > level_order[level]:
                    level = candidate
                    action = rule["then"].get("action")
        return {
            "level": level,
            "triggered_rules": matched,
            "action": action,
            "review_status": "unreviewed",
            "production_enabled": False,
        }

    def _choose(
        self,
        classification: str | None,
        safety_level: str,
        required_facts: set[str],
    ) -> dict[str, Any] | None:
        if safety_level in {"urgent", "emergency"}:
            return None

        questions = self.package["indexes"]["questions_by_fact"]
        for conflict in self.memory.contradictions:
            if conflict["status"] == "unresolved" and conflict["fact_id"] in questions:
                fact_id = conflict["fact_id"]
                template = questions[fact_id]
                return {
                    "target_id": self._target_for_fact(fact_id),
                    "fact_id": fact_id,
                    "template_id": template["template_id"],
                    "text": f"I heard different answers about this. {template['wording']}",
                    "score": 900,
                    "reason": "contradiction_resolution",
                }

        candidates: list[dict[str, Any]] = []
        for rule in self.package["rule_graph"]["rules"]:
            if rule["type"] != "priority":
                continue
            target = rule["then"]["target"]
            facts = self.package["indexes"]["target_facts"].get(target, [])
            if not facts:
                continue
            fact_id = facts[0]
            if self.memory.state(fact_id) in {"known", "unknown", "not_applicable"}:
                continue
            if fact_id in self.asked:
                continue
            when = rule["when"]
            if "fact_state" in when:
                required = next(iter(when["fact_state"]))
                if self.memory.state(required) != "not_asked":
                    continue
            duration_requirement = when.get("duration_class")
            if duration_requirement and fact_id not in required_facts:
                current = classification or "unknown"
                if isinstance(duration_requirement, str) and current != duration_requirement:
                    continue
                if isinstance(duration_requirement, dict) and current not in duration_requirement.get("in", []):
                    continue
            template = questions.get(fact_id)
            if template is None:
                continue
            base_score = rule["priority"]
            score = base_score + (200 if fact_id in required_facts else 0)
            candidates.append({
                "target_id": target,
                "fact_id": fact_id,
                "template_id": template["template_id"],
                "text": template["wording"],
                "score": score,
                "base_score": base_score,
                "reason": rule["then"].get("reason", rule["id"]),
                "rule_id": rule["id"],
            })
        if not candidates:
            return None
        return max(candidates, key=lambda item: (item["score"], item["rule_id"]))

    def _target_for_fact(self, fact_id: str) -> str | None:
        for target, facts in self.package["indexes"]["target_facts"].items():
            if fact_id in facts:
                return target
        return None

    def snapshot(
        self,
        question: dict[str, Any] | None,
        safety: dict[str, Any],
        classification: str | None,
        stop_reason: str | None,
        completion: dict[str, Any],
    ) -> dict[str, Any]:
        memory = self.memory.snapshot()
        return {
            "session_id": self.session_id,
            "turn": self.turn,
            "patient_context": {},
            "duration_class": classification,
            "facts": memory["facts"],
            "data_absent_facts": memory["data_absent_facts"],
            "active_intents": list(self.active_intents),
            "active_targets": dict(self.active_targets),
            "active_patterns": list(self.active_patterns),
            "contradictions": memory["contradictions"],
            "safety_status": safety,
            "selected_question": question,
            "stop_reason": stop_reason,
            "completion_status": completion,
            "events": memory["events"],
            "trace": list(self.trace),
            "package": memory["package"],
            "knowledge_warnings": list(self.package.get("_runtime_warnings", [])),
        }
