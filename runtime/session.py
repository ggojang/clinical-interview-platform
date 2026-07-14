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
            "harder to breathe", "숨이 차", "숨도 차", "숨쉬기 힘", "숨쉬기가",
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

    # Preserve the semantic relation when a Korean modifier separates "blood"
    # from "mixed" (for example, "피가 조금 섞여"). Requiring a nearby cough
    # or sputum cue avoids treating unrelated bleeding as hemoptysis.
    if re.search(r"(?:기침|가래).{0,20}피가\s*(?:조금|약간|살짝)?\s*(?:섞|나)", text):
        out["symptom.hemoptysis"] = fact(True, text, turn, .93)

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
    pending_edit_fact: str | None = None
    edit_reference_map: dict[str, str] = field(default_factory=dict)
    amended_after_completion: bool = False
    clarification_counts: dict[str, int] = field(default_factory=dict)
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
        edit_action = self._parse_edit_command(patient_text)
        if edit_action and edit_action[0] == "menu":
            return self._edit_menu_state(turn)
        if edit_action and edit_action[0] == "select" and edit_action[2] is None:
            return self._edit_prompt_state(turn, edit_action[1])

        correction_target = self.pending_edit_fact
        answer_text = patient_text
        if edit_action and edit_action[0] == "select":
            correction_target = self._resolve_edit_target(edit_action[1])
            if correction_target is None:
                return self._edit_menu_state(turn, "수정할 수 있는 항목을 찾지 못했습니다.")
            answer_text = edit_action[2] or ""
        expected_fact = correction_target or self.last_question_fact
        additions = extract(answer_text, turn, expected_fact)
        low = answer_text.lower().strip()
        low_normalized = low.rstrip(".!?")
        for node in self.package["knowledge_graph"]["nodes"]:
            if node["type"] != "Fact" or node["id"] in additions:
                continue
            cues = node.get("extraction_cues", [])
            if node.get("value_type") == "boolean" and any(
                cue.lower() in low and f"no {cue.lower()}" not in low
                for cue in cues
            ):
                additions[node["id"]] = fact(True, answer_text, turn, .78)

        if expected_fact and expected_fact not in additions:
            node = next(
                (
                    item for item in self.package["knowledge_graph"]["nodes"]
                    if item["id"] == expected_fact
                ),
                None,
            )
            if node:
                allowed = node.get("allowed_values", [])
                normalized = low_normalized
                if expected_fact == "symptom.dyspnea" and normalized in {"1", "2"}:
                    additions[expected_fact] = fact(
                        "mild" if normalized == "1" else "none", answer_text, turn, .95
                    )
                elif node.get("value_type") == "boolean" and normalized in {"1", "2"}:
                    additions[expected_fact] = fact(
                        normalized == "1", answer_text, turn, .95
                    )
                elif normalized in allowed:
                    additions[expected_fact] = fact(
                        normalized, answer_text, turn, .92
                    )
                elif node.get("value_type") == "integer" and re.fullmatch(
                    r"\d+", normalized
                ):
                    additions[expected_fact] = fact(
                        int(normalized), answer_text, turn, .95
                    )
                elif (
                    node.get("value_type") == "string"
                    and normalized
                    and normalized not in {
                        "i am not sure", "i'm not sure", "not sure",
                        "모르겠어요", "잘 모르겠어요",
                        "i prefer not to answer", "i'd rather not answer",
                        "prefer not to say", "답하고 싶지 않아요",
                        "말하고 싶지 않아요", "not applicable",
                        "does not apply", "해당되지 않아요",
                    }
                ):
                    additions[expected_fact] = fact(
                        answer_text.strip(), answer_text, turn, .85
                    )
        if correction_target:
            additions = {
                fact_id: candidate for fact_id, candidate in additions.items()
                if fact_id == correction_target
            }
        if correction_target:
            for candidate in additions.values():
                candidate["correction"] = True
        elif any(marker in patient_text.lower() for marker in ("i meant", "sorry, i meant")) or "정정" in patient_text or "아니, " in patient_text:
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
        if expected_fact and expected_fact not in additions:
            if low_normalized in {
                "3",
                "i am not sure", "i'm not sure", "not sure",
                "모르겠어요", "잘 모르겠어요",
            }:
                self.memory.mark_absent(
                    expected_fact, answer_text, "asked-unknown",
                    correction=bool(correction_target),
                )
                merge_results[expected_fact] = "corrected" if correction_target else "asked-unknown"
            elif low_normalized in {
                "4",
                "i prefer not to answer", "i'd rather not answer",
                "prefer not to say", "답하고 싶지 않아요", "말하고 싶지 않아요",
            }:
                self.memory.mark_absent(
                    expected_fact, answer_text, "asked-declined",
                    correction=bool(correction_target),
                )
                merge_results[expected_fact] = "corrected" if correction_target else "asked-declined"
            elif low_normalized in {
                "not applicable", "does not apply", "해당되지 않아요",
            }:
                self.memory.mark_absent(
                    expected_fact, answer_text, "not-applicable",
                    correction=bool(correction_target),
                )
                merge_results[expected_fact] = "corrected" if correction_target else "not-applicable"

        was_complete = bool(self.trace and self.trace[-1]["completion"]["complete"])
        if correction_target and correction_target not in merge_results:
            return self._edit_prompt_state(
                turn,
                correction_target,
                error="새 답변을 해석하지 못했습니다. 값 또는 1 예, 2 아니오, 3 잘 모르겠음, 4 답변하지 않음을 입력해 주세요.",
            )
        if correction_target:
            self.pending_edit_fact = None
            self.amended_after_completion = self.amended_after_completion or was_complete
            self.memory.record_event("answer_revised", {
                "actor": "patient",
                "turn": turn,
                "fact_id": correction_target,
                "outcome": merge_results.get(correction_target),
                "after_completion": was_complete,
            })

        needs_clarification = bool(
            expected_fact
            and expected_fact not in merge_results
            and not correction_target
        )
        if expected_fact and expected_fact in merge_results:
            self.clarification_counts.pop(expected_fact, None)

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
        clarification = None
        if (
            needs_clarification
            and expected_fact
            and safety["level"] not in {"urgent", "emergency"}
            and turn < self.max_turns
        ):
            self.clarification_counts[expected_fact] = (
                self.clarification_counts.get(expected_fact, 0) + 1
            )
            question = self._question_for_fact(
                expected_fact, "answer_not_understood_reconfirmation"
            )
            clarification = self._clarification_payload(
                expected_fact, patient_text, self.clarification_counts[expected_fact]
            )
            self.memory.record_event("answer_clarification_requested", {
                "actor": "runtime",
                "turn": turn,
                "fact_id": expected_fact,
                "attempt": self.clarification_counts[expected_fact],
                "reason": "answer_not_understood",
            })
        resume_fact = self.last_question_fact if correction_target else None
        if (
            resume_fact
            and self.memory.state(resume_fact) == "not_asked"
            and safety["level"] not in {"urgent", "emergency"}
            and not completion["complete"]
        ):
            question = self._question_for_fact(resume_fact, "resume_after_correction")
        self.last_question_fact = question["fact_id"] if question else None
        if self.last_question_fact:
            if self.last_question_fact not in self.asked:
                self.asked.append(self.last_question_fact)

        stop_reason = None
        if safety["level"] in {"urgent", "emergency"}:
            stop_reason = f"{safety['level']}_escalation"
        elif clarification is not None:
            stop_reason = None
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
            "answer_clarification": clarification,
            "stop_reason": stop_reason,
            "package": {
                "id": self.package["package_id"],
                "version": self.package["package_version"],
                "semantic_digest": self.package["semantic_digest"],
            },
        }
        self.trace.append(trace_entry)
        state = self.snapshot(question, safety, classification, stop_reason, completion)
        state["answer_clarification"] = clarification
        return state

    def _clarification_payload(
        self, fact_id: str, raw_response: str, attempt: int
    ) -> dict[str, Any]:
        node = next(
            item for item in self.package["knowledge_graph"]["nodes"]
            if item["type"] == "Fact" and item["id"] == fact_id
        )
        payload = {
            "required": True,
            "fact_id": fact_id,
            "reason": "possible_typo_invalid_option_or_ambiguous_meaning",
            "attempt": attempt,
            "raw_response": raw_response,
            "suggested_interpretation": None,
            "confirmation_required_before_fact_merge": True,
            "message_ko": "응답을 명확히 이해하지 못했습니다. 원래 질문에 다시 답해 주세요.",
            "binary_numeric_codes": {
                "1": "yes", "2": "no", "3": "asked-unknown", "4": "asked-declined"
            },
        }
        if node.get("allowed_values"):
            payload["allowed_values"] = list(node["allowed_values"])
        payload["value_type"] = node.get("value_type")
        return payload

    def _parse_edit_command(self, text: str) -> tuple[str, str | None, str | None] | None:
        stripped = text.strip()
        if stripped.lower() in {"수정", "답변 수정", "edit", "edit answer", "change answer"}:
            return ("menu", None, None)
        match = re.fullmatch(
            r"(?:수정|edit)\s+([Ee]\d+|[A-Za-z][A-Za-z0-9_.-]*)(?:\s*[:=]\s*(.+))?",
            stripped,
            re.IGNORECASE,
        )
        if match:
            return ("select", match.group(1), match.group(2))
        return None

    def _editable_answers(self) -> list[dict[str, Any]]:
        ordered = list(dict.fromkeys(self.asked + list(self.memory.facts)))
        editable = [
            fact_id for fact_id in ordered
            if self.memory.state(fact_id) in {"known", "unknown", "not_applicable", "conflicted"}
        ]
        self.edit_reference_map = {
            f"E{index}": fact_id for index, fact_id in enumerate(editable, 1)
        }
        questions = self.package["indexes"]["questions_by_fact"]
        items = []
        for edit_ref, fact_id in self.edit_reference_map.items():
            record = self.memory.facts[fact_id]
            items.append({
                "edit_ref": edit_ref,
                "fact_id": fact_id,
                "label": questions.get(fact_id, {}).get("wording", fact_id),
                "status": record.get("status"),
                "current_value": record.get("value"),
                "dataAbsentReason": record.get("dataAbsentReason"),
            })
        return items

    def _resolve_edit_target(self, reference: str | None) -> str | None:
        if reference is None:
            return None
        if not self.edit_reference_map:
            self._editable_answers()
        normalized = reference.upper() if re.fullmatch(r"[Ee]\d+", reference) else reference
        target = self.edit_reference_map.get(normalized, normalized)
        return target if target in self.memory.facts else None

    def _edit_menu_state(self, turn: int, error: str | None = None) -> dict[str, Any]:
        self.pending_edit_fact = None
        items = self._editable_answers()
        self.memory.record_event("answer_revision_menu_opened", {
            "actor": "patient",
            "turn": turn,
            "editable_fact_ids": [item["fact_id"] for item in items],
        })
        state = self._current_state()
        state["edit_menu"] = {
            "instruction_ko": "수정할 항목의 E번호를 '수정 E2'처럼 입력해 주세요.",
            "items": items,
            "error": error,
        }
        return state

    def _edit_prompt_state(
        self, turn: int, reference: str | None, error: str | None = None
    ) -> dict[str, Any]:
        target = self._resolve_edit_target(reference)
        if target is None:
            return self._edit_menu_state(turn, "수정할 수 있는 항목을 찾지 못했습니다.")
        self.pending_edit_fact = target
        record = self.memory.facts[target]
        state = self._current_state()
        state["edit_prompt"] = {
            "fact_id": target,
            "label": self.package["indexes"]["questions_by_fact"].get(target, {}).get("wording", target),
            "current_status": record.get("status"),
            "current_value": record.get("value"),
            "dataAbsentReason": record.get("dataAbsentReason"),
            "instruction_ko": "새 답변을 입력해 주세요. 가능한 경우 1 예, 2 아니오, 3 잘 모르겠음, 4 답변하지 않음을 사용할 수 있습니다.",
            "error": error,
        }
        return state

    def _question_for_fact(self, fact_id: str, reason: str) -> dict[str, Any] | None:
        template = self.package["indexes"]["questions_by_fact"].get(fact_id)
        if not template:
            return None
        return {
            "target_id": self._target_for_fact(fact_id),
            "fact_id": fact_id,
            "template_id": template["template_id"],
            "text": template["wording"],
            "score": 1000,
            "reason": reason,
        }

    def _current_state(self) -> dict[str, Any]:
        classification = duration_class(self.memory.value("symptom.duration"))
        self._update_patterns(classification)
        self._update_target_states(classification)
        safety = self._safety()
        completion = self._completion(classification, safety)
        question = (
            self._question_for_fact(self.last_question_fact, "preserved_during_correction")
            if self.last_question_fact else None
        )
        return self.snapshot(question, safety, classification, None, completion)

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
        if self.reason_for_encounter == "rfe.chest_pain":
            self._update_chest_pain_patterns()
            return
        if self.reason_for_encounter == "rfe.headache":
            self._update_headache_patterns()
            return
        if self.reason_for_encounter == "rfe.dizziness_syncope":
            self._update_dizziness_syncope_patterns()
            return
        if self.reason_for_encounter == "rfe.vomiting_diarrhea":
            self._update_vomiting_diarrhea_patterns()
            return
        if self.reason_for_encounter == "rfe.urinary_symptoms":
            self._update_urinary_symptom_patterns()
            return
        if self.reason_for_encounter == "rfe.fatigue":
            self._update_fatigue_patterns()
            return
        if self.reason_for_encounter == "rfe.back_pain":
            self._update_back_pain_patterns()
            return
        if self.reason_for_encounter == "rfe.skin_complaint":
            self._update_skin_complaint_patterns()
            return
        if self.reason_for_encounter == "rfe.medication_review":
            self._update_medication_review_patterns()
            return
        if self.reason_for_encounter == "rfe.upper_respiratory_symptoms":
            self._update_upper_respiratory_patterns()
            return
        if self.reason_for_encounter == "rfe.palpitations":
            self._update_palpitations_patterns()
            return
        if self.reason_for_encounter == "rfe.bowel_symptoms":
            self._update_bowel_patterns()
            return
        if self.reason_for_encounter == "rfe.focal_weakness_numbness":
            self._update_focal_neurology_patterns()
            return
        if self.reason_for_encounter == "rfe.joint_limb_complaint":
            self._update_joint_limb_patterns()
            return
        if self.reason_for_encounter == "rfe.mental_health_sleep":
            self._update_mental_health_sleep_patterns()
            return
        if self.reason_for_encounter == "rfe.edema":
            self._update_edema_patterns()
            return
        if self.reason_for_encounter == "rfe.hypertension_follow_up":
            self._update_hypertension_follow_up_patterns()
            return
        if self.reason_for_encounter == "rfe.weight_constitutional_change":
            self._update_weight_constitutional_patterns()
            return
        if self.reason_for_encounter == "rfe.reproductive_genital_symptoms":
            self._update_reproductive_genital_patterns()
            return
        if self.reason_for_encounter == "rfe.eye_symptoms":
            self._update_eye_patterns()
            return
        if self.reason_for_encounter == "rfe.ear_hearing_symptoms":
            self._update_ear_hearing_patterns()
            return
        if self.reason_for_encounter == "rfe.diabetes_follow_up":
            self._update_diabetes_follow_up_patterns()
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

    def _update_chest_pain_patterns(self) -> None:
        active = ["cardiovascular.chest_pain"]
        if any(self.memory.value(item) is True for item in (
            "symptom.chest_pain.radiation", "symptom.chest_pain.exertional",
            "symptom.marked_sweating", "symptom.nausea_or_vomiting",
        )) or self.memory.value("symptom.chest_pain.quality") in {
            "pressure", "tightness", "heaviness",
        }:
            active.append("chest_pain.coronary_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.chest_pain.pleuritic", "symptom.hemoptysis",
            "symptom.unilateral_leg_pain_swelling", "history.previous_vte",
            "history.recent_immobility_or_surgery",
        )):
            active.append("chest_pain.thromboembolic_warning_features")
        if (
            self.memory.value("symptom.chest_pain.onset") == "sudden"
            and self.memory.value("symptom.chest_pain.severity") == "severe"
        ) or self.memory.value("symptom.neurological_deficit") is True:
            active.append("chest_pain.aortic_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.chest_pain.positional", "symptom.chest_pain.reproducible",
            "symptom.fever", "symptom.palpitations",
        )):
            active.append("chest_pain.other_associated_features")
        self.active_patterns = active

    def _update_headache_patterns(self) -> None:
        active = ["neurological.headache"]
        if any(self.memory.value(item) is True for item in (
            "symptom.nausea_or_vomiting", "symptom.light_sensitivity",
            "symptom.sound_sensitivity", "symptom.aura_visual",
            "symptom.aura_sensory", "symptom.aura_speech",
        )) or self.memory.value("symptom.headache.quality") == "pulsating":
            active.append("headache.migraine_associated_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.fever", "symptom.neck_stiffness",
            "symptom.altered_consciousness_or_cognition",
        )):
            active.append("headache.meningeal_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.headache.maximum_within_5_minutes",
            "symptom.neurological_deficit", "history.recent_head_trauma",
            "symptom.headache.cough_or_valsalva_trigger",
            "symptom.headache.exercise_trigger", "symptom.headache.postural",
            "symptom.headache.worsening", "symptom.painful_red_eye",
            "symptom.visual_disturbance", "patient.immunocompromised",
            "history.malignancy", "symptom.unexplained_vomiting",
        )):
            active.append("headache.secondary_warning_features")
        self.active_patterns = active

    def _update_dizziness_syncope_patterns(self) -> None:
        active = ["neurological.dizziness_or_syncope"]
        if any(self.memory.value(item) is True for item in (
            "symptom.neurological_deficit", "symptom.new_gait_unsteadiness",
            "symptom.new_hearing_loss", "symptom.nausea_or_vomiting",
        )) and self.memory.value("symptom.dizziness.sudden_onset") is True:
            active.append("dizziness.neurological_warning_features")
        if self.memory.value("symptom.syncope.occurred") is True:
            active.append("syncope.transient_loss_of_consciousness")
            if any(self.memory.value(item) is True for item in (
                "symptom.chest_pain", "symptom.palpitations",
                "event.syncope.during_exertion", "history.heart_failure",
                "history.cardiac_disease",
                "family_history.sudden_cardiac_death_under_40",
            )):
                active.append("syncope.cardiovascular_warning_features")
            if any(self.memory.value(item) is True for item in (
                "event.syncope.limb_jerking", "event.syncope.lateral_tongue_bite",
                "event.syncope.post_event_confusion",
            )):
                active.append("syncope.seizure_associated_features")
        if any(self.memory.value(item) is True for item in (
            "event.syncope.reflex_prodrome", "event.syncope.reflex_trigger",
            "symptom.dizziness.postural_trigger",
            "symptom.dizziness.head_movement_trigger",
        )):
            active.append("dizziness_syncope.reflex_or_postural_features")
        self.active_patterns = active

    def _update_vomiting_diarrhea_patterns(self) -> None:
        active = ["gastrointestinal.vomiting_or_diarrhea"]
        if any(self.memory.value(item) is True for item in (
            "symptom.unable_to_keep_fluids", "symptom.dehydration_signs",
            "symptom.reduced_urine_output",
        )):
            active.append("vomiting_diarrhea.dehydration_warning_features")
        if any(self.memory.value(item) is True for item in (
            "exposure.sick_contact_gastrointestinal",
            "exposure.suspect_food_or_water",
            "exposure.recent_international_travel",
        )):
            active.append("vomiting_diarrhea.infectious_exposure_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.vomiting_over_two_days", "symptom.diarrhea_over_seven_days",
            "symptom.unintentional_weight_loss",
            "symptom.persistent_abdominal_or_back_pain",
        )):
            active.append("vomiting_diarrhea.persistent_warning_features")
        self.active_patterns = active

    def _update_urinary_symptom_patterns(self) -> None:
        active = ["genitourinary.urinary_symptoms"]
        if any(self.memory.value(item) is True for item in (
            "symptom.dysuria", "symptom.urinary_frequency",
            "symptom.urinary_urgency", "symptom.cloudy_urine",
        )):
            active.append("urinary.lower_tract_infection_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.flank_pain", "symptom.fever", "symptom.rigors",
            "symptom.systemically_unwell",
        )):
            active.append("urinary.upper_tract_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.urinary_hesitancy", "symptom.weak_urine_stream",
            "symptom.incomplete_bladder_emptying", "symptom.unable_to_urinate",
        )):
            active.append("urinary.voiding_or_retention_features")
        if self.memory.value("symptom.visible_hematuria") is True:
            active.append("urinary.haematuria_evaluation_features")
        self.active_patterns = active

    def _update_fatigue_patterns(self) -> None:
        active = ["systemic.fatigue"]
        if any(self.memory.value(item) is True for item in (
            "symptom.post_exertional_malaise",
            "symptom.post_exertional_delayed_or_prolonged",
            "symptom.unrefreshing_sleep", "symptom.cognitive_difficulty",
        )):
            active.append("fatigue.post_exertional_features")
        if any(self.memory.value(item) is True for item in (
            "sleep.insomnia", "sleep.snoring_gasping_or_choking",
        )):
            active.append("fatigue.sleep_related_features")
        if any(self.memory.value(item) is True for item in (
            "mental_health.low_mood", "mental_health.anhedonia",
            "mental_health.suicidal_ideation",
        )):
            active.append("fatigue.mood_related_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.fever", "symptom.unintentional_weight_loss",
            "symptom.appetite_loss", "symptom.cough",
            "symptom.thirst_and_polyuria",
        )):
            active.append("fatigue.systemic_warning_features")
        self.active_patterns = active

    def _update_back_pain_patterns(self) -> None:
        active = ["musculoskeletal.back_pain"]
        if any(self.memory.value(item) is True for item in (
            "symptom.radicular_leg_pain", "symptom.unilateral_leg_numbness",
            "symptom.unilateral_leg_weakness",
        )):
            active.append("back_pain.radicular_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.bilateral_leg_neurological_symptoms",
            "symptom.saddle_sensory_loss", "symptom.new_bladder_dysfunction",
            "symptom.new_bowel_control_change",
            "symptom.new_sexual_sensory_or_function_change",
            "symptom.progressive_leg_weakness",
        )):
            active.append("back_pain.cauda_equina_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.fever", "symptom.back_pain.night_or_rest_pain",
            "symptom.unintentional_weight_loss", "history.malignancy",
            "patient.immunocompromised",
        )):
            active.append("back_pain.systemic_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.inflammatory_back_features", "event.mechanical_trigger",
        )):
            active.append("back_pain.mechanical_or_inflammatory_context")
        self.active_patterns = active

    def _update_skin_complaint_patterns(self) -> None:
        active = ["dermatological.skin_complaint"]
        if any(self.memory.value(item) is True for item in (
            "symptom.throat_or_tongue_swelling",
            "symptom.severe_breathing_difficulty",
            "symptom.collapse_or_unresponsiveness",
        )):
            active.append("skin.acute_allergic_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.skin_blistering_or_peeling", "symptom.mucosal_sores",
            "symptom.eye_pain_or_vision_change", "medication.new_recent",
        )):
            active.append("skin.severe_cutaneous_reaction_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.skin_hot_painful_swollen", "symptom.fever",
            "symptom.systemically_unwell", "symptom.skin_complaint.rapid_spread",
        )):
            active.append("skin.infection_warning_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.pigmented_lesion_change_size",
            "symptom.pigmented_lesion_irregular_shape",
            "symptom.pigmented_lesion_irregular_colour",
            "symptom.skin_lesion_oozing_bleeding_nonhealing",
        )):
            active.append("skin.concerning_lesion_features")
        self.active_patterns = active

    def _update_medication_review_patterns(self) -> None:
        active = ["medication.review"]
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "medication.actual_use_differs", "medication.duplicate_or_unknown_product",
            "medication.recent_care_transition",
        )):
            active.append("medication.reconciliation_discrepancy")
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "medication.suspected_adverse_effects", "medication.monitoring_due_or_overdue",
            "history.kidney_impairment", "history.liver_impairment",
        )):
            active.append("medication.benefit_harm_or_monitoring")
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "medication.intentional_nonadherence_reason",
            "medication.administration_difficulty", "medication.access_or_cost_problem",
        )):
            active.append("medication.use_support_need")
        self.active_patterns = active

    def _update_upper_respiratory_patterns(self) -> None:
        active = ["upper_respiratory.symptoms"]
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "symptom.throat_pain", "symptom.painful_swallowing",
            "observation.tonsillar_exudate_or_pus", "symptom.tender_anterior_neck_nodes",
        )):
            active.append("upper_respiratory.throat_features")
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "symptom.nasal_obstruction", "symptom.nasal_discharge",
            "symptom.facial_pain_or_pressure", "symptom.reduced_or_lost_smell",
        )):
            active.append("upper_respiratory.nasal_sinus_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.sneezing_or_itchy_nose", "symptom.itchy_red_watery_eyes",
        )):
            active.append("upper_respiratory.allergic_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.hoarseness_persistent_three_weeks",
            "symptom.persistent_mouth_ulcer_or_neck_lump",
        )):
            active.append("upper_respiratory.persistent_warning_features")
        self.active_patterns = active

    def _update_palpitations_patterns(self) -> None:
        active = ["cardiovascular.palpitations"]
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "symptom.palpitations.sensation", "observation.pulse_rate_during_episode",
            "observation.pulse_regular_during_episode",
        )):
            active.append("palpitations.rhythm_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.chest_pain", "symptom.severe_dyspnea", "symptom.syncope",
            "symptom.presyncope", "symptom.new_focal_neurologic_deficit",
        )):
            active.append("palpitations.immediate_safety_features")
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "trigger.palpitations.exertion", "trigger.palpitations.postural",
            "trigger.palpitations.stress_or_panic", "exposure.caffeine_or_energy_drinks",
            "medication.recent_change_palpitations",
        )):
            active.append("palpitations.trigger_features")
        self.active_patterns = active

    def _update_bowel_patterns(self) -> None:
        active = ["gastrointestinal.bowel_symptoms"]
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "symptom.bowel.frequency", "symptom.stool_form", "symptom.straining",
            "symptom.incomplete_evacuations", "symptom.narrow_stool",
        )):
            active.append("bowel.changed_habit_features")
        if any(self.memory.value(item) not in (None, False, "", "none") for item in (
            "symptom.blood_appearance", "symptom.rectal_bleeding.recurrent_or_persistent",
            "symptom.black_tarry_stool", "symptom.bloody_diarrhea",
        )):
            active.append("bowel.bleeding_features")
        if any(self.memory.value(item) is True for item in (
            "symptom.unable_to_pass_stool_or_flatus", "symptom.abdominal_distension",
            "symptom.repeated_vomiting",
        )):
            active.append("bowel.obstruction_warning_features")
        self.active_patterns = active

    def _update_focal_neurology_patterns(self) -> None:
        active = ["neurological.focal_weakness_numbness"]
        if any(self.memory.value(x) is True for x in ("symptom.face_droop", "symptom.arm_drift_or_cannot_raise", "symptom.speech_or_language_disturbance", "symptom.sudden_visual_loss_or_field_defect")):
            active.append("focal_neurology.stroke_warning_features")
        if any(self.memory.value(x) is True for x in ("symptom.severe_back_pain_radiating_leg", "symptom.new_bladder_bowel_or_sexual_dysfunction", "symptom.perineal_or_saddle_numbness")):
            active.append("focal_neurology.spinal_warning_features")
        self.active_patterns = active

    def _update_joint_limb_patterns(self) -> None:
        active = ["musculoskeletal.joint_limb_complaint"]
        if any(self.memory.value(x) is True for x in ("event.joint_limb.recent_injury", "symptom.joint_limb.visible_deformity", "symptom.joint_limb.open_wound_or_exposed_bone")):
            active.append("joint_limb.trauma_features")
        if any(self.memory.value(x) is True for x in ("symptom.hot_swollen_joint", "symptom.fever", "symptom.systemically_unwell")):
            active.append("joint_limb.infection_inflammation_features")
        if any(self.memory.value(x) is True for x in ("symptom.joint_limb.postinjury_numbness", "symptom.joint_limb.cold_pale_blue_distal", "symptom.neck_pain_with_bilateral_weakness_or_clumsiness")):
            active.append("joint_limb.neurovascular_warning_features")
        self.active_patterns = active

    def _update_mental_health_sleep_patterns(self) -> None:
        active = ["mental_health.sleep_concern"]
        if any(self.memory.value(x) is True for x in ("risk.suicidal_thoughts_current", "risk.suicide_plan_or_intent", "risk.unable_to_stay_safe", "event.recent_self_harm_or_suicide_attempt")):
            active.append("mental_health.self_harm_warning_features")
        if any(self.memory.value(x) is True for x in ("symptom.command_hallucination_to_harm", "symptom.first_onset_hallucination_or_delusion", "symptom.markedly_reduced_sleep_with_high_energy")):
            active.append("mental_health.psychosis_mania_features")
        if any(self.memory.value(x) not in (None, False, "", "none") for x in ("symptom.low_mood", "symptom.excessive_anxiety_or_worry", "sleep.main_problem")):
            active.append("mental_health.common_symptom_features")
        self.active_patterns = active

    def _update_edema_patterns(self) -> None:
        active = ["cardiovascular.edema"]
        if any(self.memory.value(x) is True for x in ("symptom.severe_dyspnea", "symptom.chest_pain", "symptom.hemoptysis", "symptom.faint_confused_clammy")):
            active.append("edema.cardiopulmonary_warning_features")
        if any(self.memory.value(x) is True for x in ("symptom.unilateral_leg_pain_swelling", "risk.recent_immobility_or_surgery", "history.venous_thromboembolism")):
            active.append("edema.vte_features")
        if any(self.memory.value(x) is True for x in ("symptom.dyspnea_on_exertion", "symptom.orthopnea", "symptom.paroxysmal_nocturnal_dyspnea", "symptom.rapid_weight_gain")):
            active.append("edema.systemic_fluid_features")
        self.active_patterns = active

    def _update_hypertension_follow_up_patterns(self) -> None:
        active = ["cardiovascular.hypertension_follow_up"]
        if self.memory.value("blood_pressure.repeated_180_120_or_higher") is True:
            active.append("hypertension.severe_reading")
        if any(self.memory.value(x) not in (None, False, "", "none") for x in (
            "medication.missed_dose_frequency", "medication.suspected_adverse_effects",
            "medication.recent_start_stop_dose_change",
        )):
            active.append("hypertension.medication_follow_up")
        if any(self.memory.value(x) is True for x in ("symptom.postural_dizziness", "event.recent_fall", "symptom.current_syncope")):
            active.append("hypertension.postural_features")
        if self.memory.value("patient.pregnant_or_postpartum") in ("pregnant", "postpartum_6_weeks"):
            active.append("hypertension.pregnancy_context")
        self.active_patterns = active

    def _update_weight_constitutional_patterns(self) -> None:
        active = ["general.weight_constitutional_change"]
        concern = self.memory.value("constitutional.primary_concern")
        if concern:
            active.append(f"constitutional.{concern}")
        if any(self.memory.value(x) is True for x in (
            "symptom.sudden_focal_weakness_or_speech_change",
            "symptom.rapidly_progressive_symmetric_weakness",
            "symptom.weakness_swallowing_or_voice_change",
        )):
            active.append("constitutional.neurological_warning_features")
        if any(self.memory.value(x) is True for x in (
            "symptom.night_sweats", "symptom.high_fever_or_systemically_very_unwell",
            "symptom.unexplained_lymph_node_or_mass",
        )):
            active.append("constitutional.systemic_features")
        if any(self.memory.value(x) is True for x in (
            "nutrition.little_or_no_intake_over_five_days",
            "nutrition.unable_to_keep_fluids_or_severe_dehydration",
        )):
            active.append("constitutional.nutrition_risk")
        self.active_patterns = active

    def _update_reproductive_genital_patterns(self) -> None:
        active = ["genitourinary.reproductive_genital_symptoms"]
        branch = self.memory.value("genital.primary_symptom_group")
        if branch:
            active.append(f"genital.branch.{branch}")
        if any(self.memory.value(x) is True for x in (
            "genital.severe_injury_or_uncontrolled_bleeding",
            "genital.rapid_spread_discoloration_or_tissue_change",
            "symptom.unable_to_urinate",
        )):
            active.append("genital.immediate_safety_features")
        if self.memory.value("pregnancy.possible_or_test_result") in ("possible", "positive", "uncertain"):
            active.append("genital.pregnancy_context")
        if any(self.memory.value(x) not in (None, False, "", "no") for x in (
            "sexual_health.recent_new_or_unprotected_contact",
            "sexual_health.partner_symptoms_or_sti_notice",
        )):
            active.append("genital.sexual_health_context")
        self.active_patterns = active

    def _update_eye_patterns(self) -> None:
        active = ["ophthalmic.eye_symptoms"]
        branch = self.memory.value("eye.primary_symptom_group")
        if branch:
            active.append(f"eye.branch.{branch}")
        if any(self.memory.value(x) is True for x in (
            "eye.sudden_complete_or_major_vision_loss", "eye.chemical_exposure",
            "eye.penetrating_or_high_velocity_injury", "eye.object_embedded_or_globe_deformed",
        )):
            active.append("eye.immediate_sight_threat_features")
        if any(self.memory.value(x) is True for x in (
            "eye.new_or_increased_flashes_floaters", "eye.curtain_shadow_or_field_loss",
        )):
            active.append("eye.retinal_warning_features")
        if any(self.memory.value(x) is True for x in (
            "eye.proptosis_or_painful_restricted_movement",
            "eye.periorbital_swelling_with_fever_or_unwell",
        )):
            active.append("eye.orbital_warning_features")
        self.active_patterns = active

    def _update_ear_hearing_patterns(self) -> None:
        active = ["otologic.ear_hearing_symptoms"]
        branch = self.memory.value("ear.primary_symptom_group")
        if branch:
            active.append(f"ear.branch.{branch}")
        if any(self.memory.value(x) is True for x in (
            "ear.sudden_hearing_loss_within_72h",
            "ear.rapidly_worsening_hearing_4_to_90_days",
        )):
            active.append("ear.time_sensitive_hearing_loss")
        if any(self.memory.value(x) is True for x in (
            "ear.head_injury_or_penetrating_trauma",
            "ear.clear_or_bloody_discharge_after_head_injury",
            "ear.button_battery_or_sharp_foreign_body",
        )):
            active.append("ear.trauma_or_foreign_body_warning")
        if self.memory.value("ear.postauricular_redness_swelling_tenderness_or_protrusion") is True:
            active.append("ear.mastoid_warning_features")
        self.active_patterns = active

    def _update_diabetes_follow_up_patterns(self) -> None:
        active = ["endocrine.diabetes_follow_up"]
        diabetes_type = self.memory.value("diabetes.type_or_context")
        focus = self.memory.value("diabetes.primary_follow_up_focus")
        if diabetes_type:
            active.append(f"diabetes.type.{diabetes_type}")
        if focus:
            active.append(f"diabetes.focus.{focus}")
        if any(self.memory.value(x) is True for x in (
            "diabetes.dka_symptom_cluster", "diabetes.moderate_large_ketones_or_high_ketone",
            "diabetes.marked_hyperglycemia_with_confusion_or_dehydration",
            "diabetes.sglt2_use_with_dka_symptoms",
        )):
            active.append("diabetes.hyperglycemic_crisis_warning")
        if any(self.memory.value(x) is True for x in (
            "diabetes.current_severe_hypoglycemia", "diabetes.current_glucose_below_54_or_persistent_below_70",
            "diabetes.severe_hypoglycemia_needing_assistance_history",
        )):
            active.append("diabetes.hypoglycemia_risk")
        if any(self.memory.value(x) is True for x in (
            "diabetes.foot_ulcer_with_sepsis_ischaemia_deep_infection_or_gangrene",
            "diabetes.active_foot_ulcer_infection_or_unexplained_hot_swollen_foot",
        )):
            active.append("diabetes.active_foot_warning")
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
        for conditional in policy.get("conditional_required_facts", []):
            selector = conditional.get("selector_fact")
            value = self.memory.value(selector) if selector else None
            cases = conditional.get("cases", {})
            if isinstance(value, list):
                matched = [item for item in value if item in cases]
                for item in matched:
                    required.update(cases[item])
                if not matched:
                    required.update(conditional.get("default", []))
            elif value in cases:
                required.update(cases[value])
            elif value is not None:
                required.update(conditional.get("default", []))
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
            "revision_status": {
                "pending_fact_id": self.pending_edit_fact,
                "amended_after_completion": self.amended_after_completion,
                "command_hint_ko": "답변을 바꾸려면 '수정'이라고 입력하세요.",
            },
            "events": memory["events"],
            "trace": list(self.trace),
            "package": memory["package"],
            "knowledge_warnings": list(self.package.get("_runtime_warnings", [])),
        }
