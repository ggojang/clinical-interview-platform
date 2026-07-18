"""Deterministic Knowledge Package compiler for the Primary Care cough slice.

The compiler uses only versioned repository inputs. It never accesses the network
and never invents missing medical knowledge.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from interoperability.uscdi import build_package_interoperability_coverage

DEFAULT_GRAPH = ROOT / "knowledge/graph/primary-care-cough.json"
DEFAULT_RULES = ROOT / "rules/primary-care-cough.json"
DEFAULT_SOURCES = ROOT / "sources/manifests/primary-care-cough.json"
DEFAULT_COMPLETION_POLICY = ROOT / "policies/primary-care-cough-completion.json"
CLINICIAN_SUBMISSION_CONTEXT = (
    ROOT / "knowledge/shared/clinician-submission-context.json"
)
HIRA_PAIN_ASSESSMENT = ROOT / "knowledge/shared/hira-pain-assessment.json"
DEFAULT_OUTPUT = ROOT / "packages/generated/primary-care-cough-0.3.0.json"
PACKAGE_PROFILES = {
    "cough": {
        "graph": DEFAULT_GRAPH,
        "rules": DEFAULT_RULES,
        "sources": DEFAULT_SOURCES,
        "completion_policy": DEFAULT_COMPLETION_POLICY,
        "output": DEFAULT_OUTPUT,
        "package_id": "package.primary-care-cough",
        "package_version": "0.3.0",
        "rfe": "rfe.cough",
        "simulation_root": ROOT / "simulation/patients/respiratory",
        "simulation_glob": "*.json",
        "research_manifests": [ROOT / "sources/manifests/respiratory-cough-research.json"],
    },
    "fever": {
        "graph": ROOT / "knowledge/graph/primary-care-fever.json",
        "rules": ROOT / "rules/primary-care-fever.json",
        "sources": ROOT / "sources/manifests/primary-care-fever.json",
        "completion_policy": ROOT / "policies/primary-care-fever-completion.json",
        "output": ROOT / "packages/generated/primary-care-fever-0.1.0.json",
        "package_id": "package.primary-care-fever",
        "package_version": "0.1.0",
        "rfe": "rfe.fever",
        "simulation_root": ROOT / "simulation/patients/systemic/fever",
        "research_manifests": [ROOT / "sources/manifests/primary-care-fever-research.json"],
    },
    "dyspnea": {
        "graph": ROOT / "knowledge/graph/primary-care-dyspnea.json",
        "rules": ROOT / "rules/primary-care-dyspnea.json",
        "sources": ROOT / "sources/manifests/primary-care-dyspnea.json",
        "completion_policy": ROOT / "policies/primary-care-dyspnea-completion.json",
        "output": ROOT / "packages/generated/primary-care-dyspnea-0.1.0.json",
        "package_id": "package.primary-care-dyspnea",
        "package_version": "0.1.0",
        "rfe": "rfe.dyspnea",
        "simulation_root": ROOT / "simulation/patients/respiratory/dyspnea",
        "research_manifests": [ROOT / "sources/manifests/primary-care-dyspnea-research.json"],
    },
    "abdominal_pain": {
        "graph": ROOT / "knowledge/graph/primary-care-abdominal-pain.json",
        "rules": ROOT / "rules/primary-care-abdominal-pain.json",
        "sources": ROOT / "sources/manifests/primary-care-abdominal-pain.json",
        "completion_policy": ROOT / "policies/primary-care-abdominal-pain-completion.json",
        "output": ROOT / "packages/generated/primary-care-abdominal-pain-0.1.0.json",
        "package_id": "package.primary-care-abdominal-pain",
        "package_version": "0.1.0",
        "rfe": "rfe.abdominal_pain",
        "simulation_root": ROOT / "simulation/patients/gastrointestinal/abdominal-pain",
        "research_manifests": [ROOT / "sources/manifests/primary-care-abdominal-pain-research.json"],
    },
    "chest_pain": {
        "graph": ROOT / "knowledge/graph/primary-care-chest-pain.json",
        "rules": ROOT / "rules/primary-care-chest-pain.json",
        "sources": ROOT / "sources/manifests/primary-care-chest-pain.json",
        "completion_policy": ROOT / "policies/primary-care-chest-pain-completion.json",
        "output": ROOT / "packages/generated/primary-care-chest-pain-0.1.0.json",
        "package_id": "package.primary-care-chest-pain",
        "package_version": "0.1.0",
        "rfe": "rfe.chest_pain",
        "simulation_root": ROOT / "simulation/patients/cardiovascular/chest-pain",
        "research_manifests": [ROOT / "sources/manifests/primary-care-chest-pain-research.json"],
    },
    "headache": {
        "graph": ROOT / "knowledge/graph/primary-care-headache.json",
        "rules": ROOT / "rules/primary-care-headache.json",
        "sources": ROOT / "sources/manifests/primary-care-headache.json",
        "completion_policy": ROOT / "policies/primary-care-headache-completion.json",
        "output": ROOT / "packages/generated/primary-care-headache-0.1.0.json",
        "package_id": "package.primary-care-headache",
        "package_version": "0.1.0",
        "rfe": "rfe.headache",
        "simulation_root": ROOT / "simulation/patients/neurological/headache",
        "research_manifests": [ROOT / "sources/manifests/primary-care-headache-research.json"],
    },
    "dizziness_syncope": {
        "graph": ROOT / "knowledge/graph/primary-care-dizziness-syncope.json",
        "rules": ROOT / "rules/primary-care-dizziness-syncope.json",
        "sources": ROOT / "sources/manifests/primary-care-dizziness-syncope.json",
        "completion_policy": ROOT / "policies/primary-care-dizziness-syncope-completion.json",
        "output": ROOT / "packages/generated/primary-care-dizziness-syncope-0.1.0.json",
        "package_id": "package.primary-care-dizziness-syncope",
        "package_version": "0.1.0",
        "rfe": "rfe.dizziness_syncope",
        "simulation_root": ROOT / "simulation/patients/neurological/dizziness-syncope",
        "research_manifests": [ROOT / "sources/manifests/primary-care-dizziness-syncope-research.json"],
    },
    "vomiting_diarrhea": {
        "graph": ROOT / "knowledge/graph/primary-care-vomiting-diarrhea.json",
        "rules": ROOT / "rules/primary-care-vomiting-diarrhea.json",
        "sources": ROOT / "sources/manifests/primary-care-vomiting-diarrhea.json",
        "completion_policy": ROOT / "policies/primary-care-vomiting-diarrhea-completion.json",
        "output": ROOT / "packages/generated/primary-care-vomiting-diarrhea-0.1.0.json",
        "package_id": "package.primary-care-vomiting-diarrhea",
        "package_version": "0.1.0",
        "rfe": "rfe.vomiting_diarrhea",
        "simulation_root": ROOT / "simulation/patients/gastrointestinal/vomiting-diarrhea",
        "research_manifests": [ROOT / "sources/manifests/primary-care-vomiting-diarrhea-research.json"],
    },
    "urinary_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-urinary-symptoms.json",
        "rules": ROOT / "rules/primary-care-urinary-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-urinary-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-urinary-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-urinary-symptoms-0.1.0.json",
        "package_id": "package.primary-care-urinary-symptoms",
        "package_version": "0.1.0",
        "rfe": "rfe.urinary_symptoms",
        "simulation_root": ROOT / "simulation/patients/genitourinary/urinary-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-urinary-symptoms-research.json"],
    },
    "fatigue": {
        "graph": ROOT / "knowledge/graph/primary-care-fatigue.json",
        "rules": ROOT / "rules/primary-care-fatigue.json",
        "sources": ROOT / "sources/manifests/primary-care-fatigue.json",
        "completion_policy": ROOT / "policies/primary-care-fatigue-completion.json",
        "output": ROOT / "packages/generated/primary-care-fatigue-0.1.0.json",
        "package_id": "package.primary-care-fatigue",
        "package_version": "0.1.0",
        "rfe": "rfe.fatigue",
        "simulation_root": ROOT / "simulation/patients/systemic/fatigue",
        "research_manifests": [ROOT / "sources/manifests/primary-care-fatigue-research.json"],
    },
    "back_pain": {
        "graph": ROOT / "knowledge/graph/primary-care-back-pain.json",
        "rules": ROOT / "rules/primary-care-back-pain.json",
        "sources": ROOT / "sources/manifests/primary-care-back-pain.json",
        "completion_policy": ROOT / "policies/primary-care-back-pain-completion.json",
        "output": ROOT / "packages/generated/primary-care-back-pain-0.1.0.json",
        "package_id": "package.primary-care-back-pain",
        "package_version": "0.1.0",
        "rfe": "rfe.back_pain",
        "simulation_root": ROOT / "simulation/patients/musculoskeletal/back-pain",
        "research_manifests": [ROOT / "sources/manifests/primary-care-back-pain-research.json"],
    },
    "skin_complaint": {
        "graph": ROOT / "knowledge/graph/primary-care-skin-complaint.json",
        "rules": ROOT / "rules/primary-care-skin-complaint.json",
        "sources": ROOT / "sources/manifests/primary-care-skin-complaint.json",
        "completion_policy": ROOT / "policies/primary-care-skin-complaint-completion.json",
        "output": ROOT / "packages/generated/primary-care-skin-complaint-0.1.0.json",
        "package_id": "package.primary-care-skin-complaint",
        "package_version": "0.1.0",
        "rfe": "rfe.skin_complaint",
        "simulation_root": ROOT / "simulation/patients/dermatological/skin-complaint",
        "research_manifests": [ROOT / "sources/manifests/primary-care-skin-complaint-research.json"],
    },
    "medication_review": {
        "graph": ROOT / "knowledge/graph/primary-care-medication-review.json",
        "rules": ROOT / "rules/primary-care-medication-review.json",
        "sources": ROOT / "sources/manifests/primary-care-medication-review.json",
        "completion_policy": ROOT / "policies/primary-care-medication-review-completion.json",
        "output": ROOT / "packages/generated/primary-care-medication-review-0.1.0.json",
        "package_id": "package.primary-care-medication-review",
        "package_version": "0.1.0",
        "rfe": "rfe.medication_review",
        "simulation_root": ROOT / "simulation/patients/medication/medication-review",
        "research_manifests": [ROOT / "sources/manifests/primary-care-medication-review-research.json"],
    },
    "upper_respiratory_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-upper-respiratory-symptoms.json",
        "rules": ROOT / "rules/primary-care-upper-respiratory-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-upper-respiratory-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-upper-respiratory-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-upper-respiratory-symptoms-0.1.0.json",
        "package_id": "package.primary-care-upper-respiratory-symptoms",
        "package_version": "0.1.0",
        "rfe": "rfe.upper_respiratory_symptoms",
        "simulation_root": ROOT / "simulation/patients/upper-respiratory",
        "research_manifests": [ROOT / "sources/manifests/primary-care-upper-respiratory-symptoms-research.json"],
    },
    "palpitations": {
        "graph": ROOT / "knowledge/graph/primary-care-palpitations.json",
        "rules": ROOT / "rules/primary-care-palpitations.json",
        "sources": ROOT / "sources/manifests/primary-care-palpitations.json",
        "completion_policy": ROOT / "policies/primary-care-palpitations-completion.json",
        "output": ROOT / "packages/generated/primary-care-palpitations-0.1.0.json",
        "package_id": "package.primary-care-palpitations",
        "package_version": "0.1.0",
        "rfe": "rfe.palpitations",
        "simulation_root": ROOT / "simulation/patients/cardiovascular/palpitations",
        "research_manifests": [ROOT / "sources/manifests/primary-care-palpitations-research.json"],
    },
    "bowel_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-bowel-symptoms.json",
        "rules": ROOT / "rules/primary-care-bowel-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-bowel-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-bowel-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-bowel-symptoms-0.1.0.json",
        "package_id": "package.primary-care-bowel-symptoms",
        "package_version": "0.1.0",
        "rfe": "rfe.bowel_symptoms",
        "simulation_root": ROOT / "simulation/patients/gastrointestinal/bowel-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-bowel-symptoms-research.json"],
    },
    "focal_weakness_numbness": {
        "graph": ROOT / "knowledge/graph/primary-care-focal-weakness-numbness.json",
        "rules": ROOT / "rules/primary-care-focal-weakness-numbness.json",
        "sources": ROOT / "sources/manifests/primary-care-focal-weakness-numbness.json",
        "completion_policy": ROOT / "policies/primary-care-focal-weakness-numbness-completion.json",
        "output": ROOT / "packages/generated/primary-care-focal-weakness-numbness-0.1.0.json",
        "package_id": "package.primary-care-focal-weakness-numbness", "package_version": "0.1.0",
        "rfe": "rfe.focal_weakness_numbness",
        "simulation_root": ROOT / "simulation/patients/neurological/focal-weakness-numbness",
        "research_manifests": [ROOT / "sources/manifests/primary-care-focal-weakness-numbness-research.json"],
    },
    "joint_limb_complaint": {
        "graph": ROOT / "knowledge/graph/primary-care-joint-limb.json",
        "rules": ROOT / "rules/primary-care-joint-limb.json",
        "sources": ROOT / "sources/manifests/primary-care-joint-limb.json",
        "completion_policy": ROOT / "policies/primary-care-joint-limb-completion.json",
        "output": ROOT / "packages/generated/primary-care-joint-limb-0.1.0.json",
        "package_id": "package.primary-care-joint-limb", "package_version": "0.1.0",
        "rfe": "rfe.joint_limb_complaint",
        "simulation_root": ROOT / "simulation/patients/musculoskeletal/joint-limb",
        "research_manifests": [ROOT / "sources/manifests/primary-care-joint-limb-research.json"],
    },
    "mental_health_sleep": {
        "graph": ROOT / "knowledge/graph/primary-care-mental-health-sleep.json",
        "rules": ROOT / "rules/primary-care-mental-health-sleep.json",
        "sources": ROOT / "sources/manifests/primary-care-mental-health-sleep.json",
        "completion_policy": ROOT / "policies/primary-care-mental-health-sleep-completion.json",
        "output": ROOT / "packages/generated/primary-care-mental-health-sleep-0.1.0.json",
        "package_id": "package.primary-care-mental-health-sleep", "package_version": "0.1.0",
        "rfe": "rfe.mental_health_sleep",
        "simulation_root": ROOT / "simulation/patients/mental-health/mental-health-sleep",
        "research_manifests": [ROOT / "sources/manifests/primary-care-mental-health-sleep-research.json"],
    },
    "edema": {
        "graph": ROOT / "knowledge/graph/primary-care-edema.json",
        "rules": ROOT / "rules/primary-care-edema.json",
        "sources": ROOT / "sources/manifests/primary-care-edema.json",
        "completion_policy": ROOT / "policies/primary-care-edema-completion.json",
        "output": ROOT / "packages/generated/primary-care-edema-0.1.0.json",
        "package_id": "package.primary-care-edema", "package_version": "0.1.0",
        "rfe": "rfe.edema", "simulation_root": ROOT / "simulation/patients/cardiovascular/edema",
        "research_manifests": [ROOT / "sources/manifests/primary-care-edema-research.json"],
    },
    "hypertension_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-hypertension-follow-up.json",
        "rules": ROOT / "rules/primary-care-hypertension-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-hypertension-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-hypertension-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-hypertension-follow-up-0.1.0.json",
        "package_id": "package.primary-care-hypertension-follow-up",
        "package_version": "0.1.0", "rfe": "rfe.hypertension_follow_up",
        "simulation_root": ROOT / "simulation/patients/cardiovascular/hypertension-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-hypertension-follow-up-research.json"],
    },
    "weight_constitutional_change": {
        "graph": ROOT / "knowledge/graph/primary-care-weight-constitutional-change.json",
        "rules": ROOT / "rules/primary-care-weight-constitutional-change.json",
        "sources": ROOT / "sources/manifests/primary-care-weight-constitutional-change.json",
        "completion_policy": ROOT / "policies/primary-care-weight-constitutional-change-completion.json",
        "output": ROOT / "packages/generated/primary-care-weight-constitutional-change-0.1.0.json",
        "package_id": "package.primary-care-weight-constitutional-change", "package_version": "0.1.0",
        "rfe": "rfe.weight_constitutional_change",
        "simulation_root": ROOT / "simulation/patients/general/weight-constitutional-change",
        "research_manifests": [ROOT / "sources/manifests/primary-care-weight-constitutional-change-research.json"],
    },
    "reproductive_genital_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-reproductive-genital-symptoms.json",
        "rules": ROOT / "rules/primary-care-reproductive-genital-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-reproductive-genital-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-reproductive-genital-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-reproductive-genital-symptoms-0.1.0.json",
        "package_id": "package.primary-care-reproductive-genital-symptoms", "package_version": "0.1.0",
        "rfe": "rfe.reproductive_genital_symptoms",
        "simulation_root": ROOT / "simulation/patients/genitourinary/reproductive-genital-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-reproductive-genital-symptoms-research.json"],
    },
    "eye_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-eye-symptoms.json",
        "rules": ROOT / "rules/primary-care-eye-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-eye-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-eye-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-eye-symptoms-0.1.0.json",
        "package_id": "package.primary-care-eye-symptoms", "package_version": "0.1.0",
        "rfe": "rfe.eye_symptoms",
        "simulation_root": ROOT / "simulation/patients/ophthalmic/eye-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-eye-symptoms-research.json"],
    },
    "ear_hearing_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-ear-hearing-symptoms.json",
        "rules": ROOT / "rules/primary-care-ear-hearing-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-ear-hearing-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-ear-hearing-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-ear-hearing-symptoms-0.1.0.json",
        "package_id": "package.primary-care-ear-hearing-symptoms", "package_version": "0.1.0",
        "rfe": "rfe.ear_hearing_symptoms",
        "simulation_root": ROOT / "simulation/patients/otologic/ear-hearing-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-ear-hearing-symptoms-research.json"],
    },
    "diabetes_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-diabetes-follow-up.json",
        "rules": ROOT / "rules/primary-care-diabetes-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-diabetes-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-diabetes-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-diabetes-follow-up-0.1.0.json",
        "package_id": "package.primary-care-diabetes-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.diabetes_follow_up",
        "simulation_root": ROOT / "simulation/patients/endocrine/diabetes-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-diabetes-follow-up-research.json"],
    },
    "oral_dental_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-oral-dental-symptoms.json",
        "rules": ROOT / "rules/primary-care-oral-dental-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-oral-dental-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-oral-dental-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-oral-dental-symptoms-0.1.0.json",
        "package_id": "package.primary-care-oral-dental-symptoms", "package_version": "0.1.0",
        "rfe": "rfe.oral_dental_symptoms",
        "simulation_root": ROOT / "simulation/patients/oral-dental/oral-dental-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-oral-dental-symptoms-research.json"],
    },
    "wound_minor_injury": {
        "graph": ROOT / "knowledge/graph/primary-care-wound-minor-injury.json",
        "rules": ROOT / "rules/primary-care-wound-minor-injury.json",
        "sources": ROOT / "sources/manifests/primary-care-wound-minor-injury.json",
        "completion_policy": ROOT / "policies/primary-care-wound-minor-injury-completion.json",
        "output": ROOT / "packages/generated/primary-care-wound-minor-injury-0.1.0.json",
        "package_id": "package.primary-care-wound-minor-injury", "package_version": "0.1.0",
        "rfe": "rfe.wound_minor_injury",
        "simulation_root": ROOT / "simulation/patients/injury/wound-minor-injury",
        "research_manifests": [ROOT / "sources/manifests/primary-care-wound-minor-injury-research.json"],
    },
    "memory_cognitive_concern": {
        "graph": ROOT / "knowledge/graph/primary-care-memory-cognitive-concern.json",
        "rules": ROOT / "rules/primary-care-memory-cognitive-concern.json",
        "sources": ROOT / "sources/manifests/primary-care-memory-cognitive-concern.json",
        "completion_policy": ROOT / "policies/primary-care-memory-cognitive-concern-completion.json",
        "output": ROOT / "packages/generated/primary-care-memory-cognitive-concern-0.1.0.json",
        "package_id": "package.primary-care-memory-cognitive-concern", "package_version": "0.1.0",
        "rfe": "rfe.memory_cognitive_concern",
        "simulation_root": ROOT / "simulation/patients/neurological/memory-cognitive-concern",
        "research_manifests": [ROOT / "sources/manifests/primary-care-memory-cognitive-concern-research.json"],
    },
    "pregnancy_postpartum_concern": {
        "graph": ROOT / "knowledge/graph/primary-care-pregnancy-postpartum-concern.json",
        "rules": ROOT / "rules/primary-care-pregnancy-postpartum-concern.json",
        "sources": ROOT / "sources/manifests/primary-care-pregnancy-postpartum-concern.json",
        "completion_policy": ROOT / "policies/primary-care-pregnancy-postpartum-concern-completion.json",
        "output": ROOT / "packages/generated/primary-care-pregnancy-postpartum-concern-0.1.0.json",
        "package_id": "package.primary-care-pregnancy-postpartum-concern", "package_version": "0.1.0",
        "rfe": "rfe.pregnancy_postpartum_concern",
        "simulation_root": ROOT / "simulation/patients/obstetric/pregnancy-postpartum-concern",
        "research_manifests": [ROOT / "sources/manifests/primary-care-pregnancy-postpartum-concern-research.json"],
    },
    "allergy_concern": {
        "graph": ROOT / "knowledge/graph/primary-care-allergy-concern.json",
        "rules": ROOT / "rules/primary-care-allergy-concern.json",
        "sources": ROOT / "sources/manifests/primary-care-allergy-concern.json",
        "completion_policy": ROOT / "policies/primary-care-allergy-concern-completion.json",
        "output": ROOT / "packages/generated/primary-care-allergy-concern-0.1.0.json",
        "package_id": "package.primary-care-allergy-concern", "package_version": "0.1.0",
        "rfe": "rfe.allergy_concern",
        "simulation_root": ROOT / "simulation/patients/allergy/allergy-concern",
        "research_manifests": [ROOT / "sources/manifests/primary-care-allergy-concern-research.json"],
    },
    "asthma_copd_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-asthma-copd-follow-up.json",
        "rules": ROOT / "rules/primary-care-asthma-copd-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-asthma-copd-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-asthma-copd-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-asthma-copd-follow-up-0.1.0.json",
        "package_id": "package.primary-care-asthma-copd-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.asthma_copd_follow_up",
        "simulation_root": ROOT / "simulation/patients/respiratory/asthma-copd-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-asthma-copd-follow-up-research.json"],
    },
    "lump_lymph_node": {
        "graph": ROOT / "knowledge/graph/primary-care-lump-lymph-node.json",
        "rules": ROOT / "rules/primary-care-lump-lymph-node.json",
        "sources": ROOT / "sources/manifests/primary-care-lump-lymph-node.json",
        "completion_policy": ROOT / "policies/primary-care-lump-lymph-node-completion.json",
        "output": ROOT / "packages/generated/primary-care-lump-lymph-node-0.1.0.json",
        "package_id": "package.primary-care-lump-lymph-node", "package_version": "0.1.0",
        "rfe": "rfe.lump_lymph_node",
        "simulation_root": ROOT / "simulation/patients/general/lump-lymph-node",
        "research_manifests": [ROOT / "sources/manifests/primary-care-lump-lymph-node-research.json"],
    },
    "dyspepsia_reflux": {
        "graph": ROOT / "knowledge/graph/primary-care-dyspepsia-reflux.json",
        "rules": ROOT / "rules/primary-care-dyspepsia-reflux.json",
        "sources": ROOT / "sources/manifests/primary-care-dyspepsia-reflux.json",
        "completion_policy": ROOT / "policies/primary-care-dyspepsia-reflux-completion.json",
        "output": ROOT / "packages/generated/primary-care-dyspepsia-reflux-0.1.0.json",
        "package_id": "package.primary-care-dyspepsia-reflux", "package_version": "0.1.0",
        "rfe": "rfe.dyspepsia_reflux",
        "simulation_root": ROOT / "simulation/patients/gastrointestinal/dyspepsia-reflux",
        "research_manifests": [ROOT / "sources/manifests/primary-care-dyspepsia-reflux-research.json"],
    },
    "thyroid_concern_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-thyroid-concern-follow-up.json",
        "rules": ROOT / "rules/primary-care-thyroid-concern-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-thyroid-concern-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-thyroid-concern-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-thyroid-concern-follow-up-0.1.0.json",
        "package_id": "package.primary-care-thyroid-concern-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.thyroid_concern_follow_up",
        "simulation_root": ROOT / "simulation/patients/endocrine/thyroid-concern-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-thyroid-concern-follow-up-research.json"],
    },
    "anemia_concern_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-anemia-concern-follow-up.json",
        "rules": ROOT / "rules/primary-care-anemia-concern-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-anemia-concern-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-anemia-concern-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-anemia-concern-follow-up-0.1.0.json",
        "package_id": "package.primary-care-anemia-concern-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.anemia_concern_follow_up",
        "simulation_root": ROOT / "simulation/patients/hematology/anemia-concern-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-anemia-concern-follow-up-research.json"],
    },
    "seizure_event_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-seizure-event-follow-up.json",
        "rules": ROOT / "rules/primary-care-seizure-event-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-seizure-event-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-seizure-event-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-seizure-event-follow-up-0.1.0.json",
        "package_id": "package.primary-care-seizure-event-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.seizure_event_follow_up",
        "simulation_root": ROOT / "simulation/patients/neurology/seizure-event-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-seizure-event-follow-up-research.json"],
    },
    "gait_falls_concern": {
        "graph": ROOT / "knowledge/graph/primary-care-gait-falls-concern.json",
        "rules": ROOT / "rules/primary-care-gait-falls-concern.json",
        "sources": ROOT / "sources/manifests/primary-care-gait-falls-concern.json",
        "completion_policy": ROOT / "policies/primary-care-gait-falls-concern-completion.json",
        "output": ROOT / "packages/generated/primary-care-gait-falls-concern-0.1.0.json",
        "package_id": "package.primary-care-gait-falls-concern", "package_version": "0.1.0",
        "rfe": "rfe.gait_falls_concern",
        "simulation_root": ROOT / "simulation/patients/neurology/gait-falls-concern",
        "research_manifests": [ROOT / "sources/manifests/primary-care-gait-falls-concern-research.json"],
    },
    "epistaxis": {
        "graph": ROOT / "knowledge/graph/primary-care-epistaxis.json",
        "rules": ROOT / "rules/primary-care-epistaxis.json",
        "sources": ROOT / "sources/manifests/primary-care-epistaxis.json",
        "completion_policy": ROOT / "policies/primary-care-epistaxis-completion.json",
        "output": ROOT / "packages/generated/primary-care-epistaxis-0.1.0.json",
        "package_id": "package.primary-care-epistaxis", "package_version": "0.1.0",
        "rfe": "rfe.epistaxis",
        "simulation_root": ROOT / "simulation/patients/ent/epistaxis",
        "research_manifests": [ROOT / "sources/manifests/primary-care-epistaxis-research.json"],
    },
    "pediatric_growth_development": {
        "graph": ROOT / "knowledge/graph/primary-care-pediatric-growth-development.json",
        "rules": ROOT / "rules/primary-care-pediatric-growth-development.json",
        "sources": ROOT / "sources/manifests/primary-care-pediatric-growth-development.json",
        "completion_policy": ROOT / "policies/primary-care-pediatric-growth-development-completion.json",
        "output": ROOT / "packages/generated/primary-care-pediatric-growth-development-0.1.0.json",
        "package_id": "package.primary-care-pediatric-growth-development", "package_version": "0.1.0",
        "rfe": "rfe.pediatric_growth_development",
        "simulation_root": ROOT / "simulation/patients/pediatrics/growth-development",
        "research_manifests": [ROOT / "sources/manifests/primary-care-pediatric-growth-development-research.json"],
    },
    "tremor_movement_concern": {
        "graph": ROOT / "knowledge/graph/primary-care-tremor-movement-concern.json",
        "rules": ROOT / "rules/primary-care-tremor-movement-concern.json",
        "sources": ROOT / "sources/manifests/primary-care-tremor-movement-concern.json",
        "completion_policy": ROOT / "policies/primary-care-tremor-movement-concern-completion.json",
        "output": ROOT / "packages/generated/primary-care-tremor-movement-concern-0.1.0.json",
        "package_id": "package.primary-care-tremor-movement-concern", "package_version": "0.1.0",
        "rfe": "rfe.tremor_movement_concern",
        "simulation_root": ROOT / "simulation/patients/neurology/tremor-movement-concern",
        "research_manifests": [ROOT / "sources/manifests/primary-care-tremor-movement-concern-research.json"],
    },
    "neck_pain": {
        "graph": ROOT / "knowledge/graph/primary-care-neck-pain.json",
        "rules": ROOT / "rules/primary-care-neck-pain.json",
        "sources": ROOT / "sources/manifests/primary-care-neck-pain.json",
        "completion_policy": ROOT / "policies/primary-care-neck-pain-completion.json",
        "output": ROOT / "packages/generated/primary-care-neck-pain-0.1.0.json",
        "package_id": "package.primary-care-neck-pain", "package_version": "0.1.0",
        "rfe": "rfe.neck_pain",
        "simulation_root": ROOT / "simulation/patients/musculoskeletal/neck-pain",
        "research_manifests": [ROOT / "sources/manifests/primary-care-neck-pain-research.json"],
    },
    "menstrual_uterine_bleeding": {
        "graph": ROOT / "knowledge/graph/primary-care-menstrual-uterine-bleeding.json",
        "rules": ROOT / "rules/primary-care-menstrual-uterine-bleeding.json",
        "sources": ROOT / "sources/manifests/primary-care-menstrual-uterine-bleeding.json",
        "completion_policy": ROOT / "policies/primary-care-menstrual-uterine-bleeding-completion.json",
        "output": ROOT / "packages/generated/primary-care-menstrual-uterine-bleeding-0.1.0.json",
        "package_id": "package.primary-care-menstrual-uterine-bleeding", "package_version": "0.1.0",
        "rfe": "rfe.menstrual_uterine_bleeding",
        "simulation_root": ROOT / "simulation/patients/womens-health/menstrual-uterine-bleeding",
        "research_manifests": [ROOT / "sources/manifests/primary-care-menstrual-uterine-bleeding-research.json"],
    },
    "breast_symptoms": {
        "graph": ROOT / "knowledge/graph/primary-care-breast-symptoms.json",
        "rules": ROOT / "rules/primary-care-breast-symptoms.json",
        "sources": ROOT / "sources/manifests/primary-care-breast-symptoms.json",
        "completion_policy": ROOT / "policies/primary-care-breast-symptoms-completion.json",
        "output": ROOT / "packages/generated/primary-care-breast-symptoms-0.1.0.json",
        "package_id": "package.primary-care-breast-symptoms", "package_version": "0.1.0",
        "rfe": "rfe.breast_symptoms",
        "simulation_root": ROOT / "simulation/patients/breast/breast-symptoms",
        "research_manifests": [ROOT / "sources/manifests/primary-care-breast-symptoms-research.json"],
    },
    "kidney_function_ckd_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-kidney-function-ckd-follow-up.json",
        "rules": ROOT / "rules/primary-care-kidney-function-ckd-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-kidney-function-ckd-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-kidney-function-ckd-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-kidney-function-ckd-follow-up-0.1.0.json",
        "package_id": "package.primary-care-kidney-function-ckd-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.kidney_function_ckd_follow_up",
        "simulation_root": ROOT / "simulation/patients/renal/kidney-function-ckd-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-kidney-function-ckd-follow-up-research.json"],
    },
    "liver_function_chronic_follow_up": {
        "graph": ROOT / "knowledge/graph/primary-care-liver-function-chronic-follow-up.json",
        "rules": ROOT / "rules/primary-care-liver-function-chronic-follow-up.json",
        "sources": ROOT / "sources/manifests/primary-care-liver-function-chronic-follow-up.json",
        "completion_policy": ROOT / "policies/primary-care-liver-function-chronic-follow-up-completion.json",
        "output": ROOT / "packages/generated/primary-care-liver-function-chronic-follow-up-0.1.0.json",
        "package_id": "package.primary-care-liver-function-chronic-follow-up", "package_version": "0.1.0",
        "rfe": "rfe.liver_function_chronic_follow_up",
        "simulation_root": ROOT / "simulation/patients/hepatology/liver-function-chronic-follow-up",
        "research_manifests": [ROOT / "sources/manifests/primary-care-liver-function-chronic-follow-up-research.json"],
    },
}

ALLOWED_NODE_TYPES = {
    "EncounterContext", "ReasonForEncounter", "ClinicalIntent",
    "InterviewTarget", "Fact", "QuestionTemplate", "ClinicalGroup",
    "Hypothesis", "Simulation", "Coverage", "Mapping", "Guideline",
}
ALLOWED_RULE_TYPES = {
    "activation", "applicability", "requirement", "completion", "priority",
    "suppression", "conflict", "safety", "transition", "stop", "mapping",
}


class CompilationError(ValueError):
    """Raised when a package cannot be compiled without guessing."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompilationError(f"{path.relative_to(ROOT)}: cannot load JSON: {exc}") from exc


def require_provenance(obj: dict[str, Any], label: str) -> None:
    provenance = obj.get("provenance")
    if not isinstance(provenance, dict):
        raise CompilationError(f"{label}: missing provenance")
    for key in ("created_by", "created_at", "review_status", "version"):
        if key not in provenance:
            raise CompilationError(f"{label}: provenance missing {key}")


def validate_graph(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    require_provenance(graph, graph.get("id", "knowledge graph"))
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise CompilationError("knowledge graph: nodes and edges must be arrays")

    node_index: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if not node_id or node_id in node_index:
            raise CompilationError(f"knowledge graph: duplicate or missing node id {node_id!r}")
        if node.get("type") not in ALLOWED_NODE_TYPES:
            raise CompilationError(f"{node_id}: unsupported node type {node.get('type')!r}")
        require_provenance(node, node_id)
        node_index[node_id] = node

    edge_ids: set[str] = set()
    for edge in edges:
        edge_id = edge.get("id")
        if not edge_id or edge_id in edge_ids:
            raise CompilationError(f"knowledge graph: duplicate or missing edge id {edge_id!r}")
        edge_ids.add(edge_id)
        if edge.get("from") not in node_index or edge.get("to") not in node_index:
            raise CompilationError(f"{edge_id}: unresolved edge reference")
        require_provenance(edge, edge_id)
        source = node_index[edge["from"]]
        target = node_index[edge["to"]]
        if source["type"] == "Hypothesis" and target["type"] == "QuestionTemplate":
            raise CompilationError(f"{edge_id}: Hypothesis must not generate QuestionTemplate")
    return node_index


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)


def validate_rules(
    rule_graph: dict[str, Any],
    node_index: dict[str, dict[str, Any]],
    production: bool,
) -> list[dict[str, Any]]:
    require_provenance(rule_graph, rule_graph.get("id", "rule graph"))
    rules = rule_graph.get("rules")
    if not isinstance(rules, list):
        raise CompilationError("rule graph: rules must be an array")

    rule_ids: set[str] = set()
    for rule in rules:
        rule_id = rule.get("id")
        if not rule_id or rule_id in rule_ids:
            raise CompilationError(f"rule graph: duplicate or missing rule id {rule_id!r}")
        rule_ids.add(rule_id)
        if rule.get("type") not in ALLOWED_RULE_TYPES:
            raise CompilationError(f"{rule_id}: unsupported rule type")
        require_provenance(rule, rule_id)
        for key, value in walk_values({"when": rule.get("when"), "then": rule.get("then")}):
            if key in {"fact", "target", "rfe"} and isinstance(value, str):
                if value not in node_index:
                    raise CompilationError(f"{rule_id}: unresolved {key} reference {value}")
            if key == "activate_intents" and isinstance(value, list):
                missing = [item for item in value if item not in node_index]
                if missing:
                    raise CompilationError(f"{rule_id}: unresolved intent references {missing}")
        if production and rule.get("type") == "safety":
            review = rule["provenance"].get("review_status")
            if review != "reviewed" or rule.get("status") != "enabled":
                raise CompilationError(
                    f"{rule_id}: production safety rule must be reviewed and enabled"
                )
    return sorted(rules, key=lambda item: (-item["priority"], item["id"]))


def validate_sources(manifest: dict[str, Any], production: bool) -> None:
    require_provenance(manifest, manifest.get("id", "source manifest"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise CompilationError("source manifest: artifacts must not be empty")
    for artifact in artifacts:
        for key in ("id", "kind", "version", "digest", "license_status"):
            if key not in artifact:
                raise CompilationError(f"source artifact missing {key}")
        if production and artifact["license_status"] not in {"allowed", "restricted"}:
            raise CompilationError(
                f"{artifact['id']}: production source license status is not acceptable"
            )
        if production and not artifact.get("complete", False):
            raise CompilationError(f"{artifact['id']}: production source is incomplete")


def path_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
    elif path.is_dir():
        for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
            if "__pycache__" in item.parts:
                continue
            digest.update(str(item.relative_to(path)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(item.read_bytes())
            digest.update(b"\0")
    else:
        raise CompilationError(f"source artifact path does not exist: {path}")
    return "sha256:" + digest.hexdigest()


def materialize_source_digests(manifest: dict[str, Any]) -> dict[str, Any]:
    resolved = deepcopy(manifest)
    for artifact in resolved["artifacts"]:
        source_path = ROOT / artifact["path"]
        artifact["digest"] = path_digest(source_path)
    return resolved


def simulation_metadata(
    simulation_root: Path, simulation_glob: str = "**/*.json"
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(simulation_root.glob(simulation_glob)):
        data = load_json(path)
        require_provenance(data, data.get("id", str(path.relative_to(ROOT))))
        result.append({
            "id": data["id"],
            "path": str(path.relative_to(ROOT)),
            "expected": data.get("expected", {}),
            "provenance": data["provenance"],
        })
    if not result:
        raise CompilationError("no JSON simulations available")
    return result


def build_indexes(
    node_index: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    questions: dict[str, dict[str, Any]] = {}
    target_facts: dict[str, list[str]] = {}
    intent_targets: dict[str, list[str]] = {}
    for edge in edges:
        if edge["type"] == "COLLECTS":
            q = node_index[edge["from"]]
            questions[edge["to"]] = {
                "template_id": q["id"],
                "wording": q["wording"],
                "language": q.get("language", "en"),
                "mode": q.get("mode", []),
                **(
                    {"answer_code_map": q["answer_code_map"]}
                    if "answer_code_map" in q else {}
                ),
                **(
                    {"data_absent_code_map": q["data_absent_code_map"]}
                    if "data_absent_code_map" in q else {}
                ),
            }
        elif edge["type"] == "REQUIRES":
            target_facts.setdefault(edge["from"], []).append(edge["to"])
        elif edge["type"] == "GENERATES":
            intent_targets.setdefault(edge["from"], []).append(edge["to"])
    return {
        "questions_by_fact": {key: questions[key] for key in sorted(questions)},
        "target_facts": {key: sorted(value) for key, value in sorted(target_facts.items())},
        "intent_targets": {key: sorted(value) for key, value in sorted(intent_targets.items())},
    }


def coverage(
    node_index: dict[str, dict[str, Any]],
    indexes: dict[str, Any],
    simulations: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    for node in node_index.values():
        by_type[node["type"]] = by_type.get(node["type"], 0) + 1
    fact_ids = {node["id"] for node in node_index.values() if node["type"] == "Fact"}
    question_facts = set(indexes["questions_by_fact"])
    target_ids = {node["id"] for node in node_index.values() if node["type"] == "InterviewTarget"}
    linked_targets = set(indexes["target_facts"])
    safety_rules = {rule["id"] for rule in rules if rule["type"] == "safety"}
    simulated_safety_rules = {
        rule_id
        for simulation in simulations
        for rule_id in simulation.get("expected", {}).get(
            "expected_triggered_rules_contains", []
        )
    }
    data_absent_simulations = sum(
        bool(simulation.get("expected", {}).get("expected_data_absent_reasons"))
        for simulation in simulations
    )
    return {
        "node_counts": dict(sorted(by_type.items())),
        "facts_with_questions": len(fact_ids & question_facts),
        "total_facts": len(fact_ids),
        "required_targets_linked_to_facts": len(target_ids & linked_targets),
        "total_targets": len(target_ids),
        "simulation_count": len(simulations),
        "total_safety_rules": len(safety_rules),
        "safety_rules_with_simulations": len(safety_rules & simulated_safety_rules),
        "uncovered_safety_rules": sorted(safety_rules - simulated_safety_rules),
        "data_absent_reason_simulations": data_absent_simulations,
        "reviewed_for_production": False,
        "known_gaps": [
            "External guideline artifacts are not cached or license-verified.",
            "Clinical and safety review is incomplete.",
            "Simulation set is below release coverage requirements.",
        ],
    }


def semantic_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def apply_hira_pain_assessment(
    profile: str,
    graph: dict[str, Any],
    rule_graph: dict[str, Any],
    completion_policy: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    """Compose the reusable HIRA-aligned pain module at Build Time.

    The profile binding is explicit so the compiler never guesses that an
    unrelated symptom means pain. A known NRS value is mandatory whenever the
    binding activates; dataAbsentReason remains recordable but cannot make the
    assessment complete.
    """
    module = load_json(HIRA_PAIN_ASSESSMENT)
    binding = module.get("profile_bindings", {}).get(profile)
    if not binding:
        return graph, rule_graph, completion_policy, None

    graph = deepcopy(graph)
    rule_graph = deepcopy(rule_graph)
    completion_policy = deepcopy(completion_policy)
    existing_ids = {node["id"] for node in graph["nodes"]}
    provenance = deepcopy(module["provenance"])

    existing_nrs_fact = binding.get("existing_nrs_fact")
    nrs_fact_id = existing_nrs_fact or "pain.nrs_score"
    nodes_to_add = [module["facts"][0]]
    questions_to_add = [module["questions"][0]]
    targets_to_add = [module["targets"][0]]
    if not existing_nrs_fact:
        nodes_to_add.append(module["facts"][1])
        questions_to_add.append(module["questions"][1])
        targets_to_add.append(module["targets"][1])
    else:
        if existing_nrs_fact not in existing_ids:
            raise CompilationError(
                f"pain assessment binding references missing NRS Fact: {existing_nrs_fact}"
            )
        nrs_node = next(node for node in graph["nodes"] if node["id"] == existing_nrs_fact)
        nrs_node.update({
            "value_type": "integer", "minimum": 0, "maximum": 10,
            "scale": deepcopy(module["facts"][1]["scale"]),
            "derived_category": deepcopy(module["facts"][1]["derived_category"]),
            "must_preserve_raw_score": True,
            "required_when_pain_applies": True,
        })

    graph["nodes"].extend(deepcopy(nodes_to_add + targets_to_add + questions_to_add))
    for target, question, fact_node in zip(targets_to_add, questions_to_add, nodes_to_add):
        fact_id = fact_node["id"]
        graph["edges"].extend([
            {
                "id": f"edge.hira-pain.{target['id']}.requires",
                "type": "REQUIRES", "from": target["id"], "to": fact_id,
                "version": module["version"], "status": "research_only",
                "provenance": deepcopy(provenance),
            },
            {
                "id": f"edge.hira-pain.{question['id']}.collects",
                "type": "COLLECTS", "from": question["id"], "to": fact_id,
                "version": module["version"], "status": "research_only",
                "provenance": deepcopy(provenance),
            },
        ])
        rule_graph["rules"].append({
            "id": f"rule.hira-pain.priority.{fact_id}",
            "type": "priority", "priority": 96,
            "when": {},
            "then": {"target": target["id"], "reason": "mandatory_standardized_pain_assessment"},
            "version": module["version"], "status": "research_only",
            "provenance": deepcopy(provenance),
        })

    # Existing profile-specific NRS questions remain canonical, but are
    # annotated and range-validated through the shared module.
    if existing_nrs_fact:
        question_id = next(
            edge["from"] for edge in graph["edges"]
            if edge["type"] == "COLLECTS" and edge["to"] == existing_nrs_fact
        )
        question_node = next(node for node in graph["nodes"] if node["id"] == question_id)
        question_node["scale_type"] = "NRS"
        question_node["required_numeric_range"] = [0, 10]

    required_pair = ["pain.frequency", nrs_fact_id]
    completion_policy.setdefault("question_budget", {})["routine"] = int(
        completion_policy.get("question_budget", {}).get("routine", 40)
    ) + len(nodes_to_add)
    completion_policy.setdefault("must_be_known_facts", [])
    for fact_id in required_pair:
        if fact_id not in completion_policy["must_be_known_facts"]:
            completion_policy["must_be_known_facts"].append(fact_id)
    if binding["activation"] == "always":
        always = completion_policy.setdefault("required_facts", {}).setdefault("always", [])
        for fact_id in required_pair:
            if fact_id not in always:
                always.append(fact_id)
    else:
        completion_policy.setdefault("conditional_required_facts", []).append({
            "when": deepcopy(binding["when"]),
            "required_facts": required_pair,
            "reason": "pain_item_activated",
        })
    return graph, rule_graph, completion_policy, module


def compile_package(
    graph_path: Path | None = None,
    rules_path: Path | None = None,
    sources_path: Path | None = None,
    production: bool = False,
    profile: str = "cough",
) -> dict[str, Any]:
    if profile not in PACKAGE_PROFILES:
        raise CompilationError(f"unknown package profile: {profile}")
    config = PACKAGE_PROFILES[profile]
    graph_path = graph_path or config["graph"]
    rules_path = rules_path or config["rules"]
    sources_path = sources_path or config["sources"]
    graph = load_json(graph_path)
    rule_graph = load_json(rules_path)
    sources = materialize_source_digests(load_json(sources_path))
    completion_policy = load_json(config["completion_policy"])
    graph, rule_graph, completion_policy, pain_assessment = apply_hira_pain_assessment(
        profile, graph, rule_graph, completion_policy
    )
    clinician_submission_context = load_json(CLINICIAN_SUBMISSION_CONTEXT)
    node_index = validate_graph(graph)
    sorted_rules = validate_rules(rule_graph, node_index, production)
    validate_sources(sources, production)
    simulations = simulation_metadata(
        config["simulation_root"], config.get("simulation_glob", "**/*.json")
    )
    indexes = build_indexes(node_index, graph["edges"])
    all_fact_ids = {
        node_id for node_id, node in node_index.items() if node["type"] == "Fact"
    }
    for fact_ids in completion_policy.get("required_facts", {}).values():
        missing = set(fact_ids) - all_fact_ids
        if missing:
            raise CompilationError(f"completion policy has unresolved Facts: {sorted(missing)}")
    for conditional in completion_policy.get("conditional_required_facts", []):
        if "when" in conditional:
            condition_refs = {
                value for key, value in walk_values(conditional["when"])
                if key == "fact" and isinstance(value, str)
            }
            missing = condition_refs - all_fact_ids
            if missing:
                raise CompilationError(
                    f"conditional completion policy has unresolved condition Facts: {sorted(missing)}"
                )
            missing = set(conditional.get("required_facts", [])) - all_fact_ids
            if missing:
                raise CompilationError(
                    f"conditional completion policy has unresolved Facts: {sorted(missing)}"
                )
            continue
        selector_id = conditional.get("selector_fact")
        if selector_id not in all_fact_ids:
            raise CompilationError(
                f"conditional completion policy has unresolved selector Fact: {selector_id}"
            )
        selector = node_index[selector_id]
        allowed = set(selector.get("allowed_values", []))
        cases = conditional.get("cases")
        if not isinstance(cases, dict) or not cases:
            raise CompilationError("conditional completion policy requires non-empty cases")
        if allowed and set(cases) - allowed:
            raise CompilationError(
                "conditional completion policy has selector cases outside allowed values: "
                f"{sorted(set(cases) - allowed)}"
            )
        for fact_ids in [*cases.values(), conditional.get("default", [])]:
            missing = set(fact_ids) - all_fact_ids
            if missing:
                raise CompilationError(
                    f"conditional completion policy has unresolved Facts: {sorted(missing)}"
                )
    for rule_id, fact_ids in completion_policy.get("clarification_facts_by_rule", {}).items():
        if rule_id not in {rule["id"] for rule in sorted_rules}:
            raise CompilationError(f"completion policy has unresolved Rule: {rule_id}")
        missing = set(fact_ids) - all_fact_ids
        if missing:
            raise CompilationError(f"completion policy has unresolved Facts: {sorted(missing)}")

    context_facts = {
        item.get("id"): item
        for item in clinician_submission_context.get("facts", [])
        if isinstance(item, dict) and item.get("id")
    }
    context_questions = clinician_submission_context.get("questions", [])
    question_fact_ids = {
        item.get("fact_id") for item in context_questions if isinstance(item, dict)
    }
    completion = clinician_submission_context.get("completion", {})
    referenced_context_facts = set(completion.get("always_required", []))
    clinician_rfe_minimum = completion.get("clinician_rfe_minimum", {})
    referenced_context_facts.update(
        clinician_rfe_minimum.get("always_required_facts", [])
    )
    for conditional in completion.get("conditional_required_facts", []):
        referenced_context_facts.add(conditional.get("selector_fact"))
        for fact_ids in conditional.get("cases", {}).values():
            referenced_context_facts.update(fact_ids)
        referenced_context_facts.update(
            conditional.get("default_when_selector_data_absent", [])
        )
    referenced_context_facts.discard(None)
    missing_context_facts = referenced_context_facts - set(context_facts)
    if missing_context_facts:
        raise CompilationError(
            "clinician submission context has unresolved Facts: "
            f"{sorted(missing_context_facts)}"
        )
    missing_context_questions = referenced_context_facts - question_fact_ids
    if missing_context_questions:
        raise CompilationError(
            "clinician submission context has required Facts without questions: "
            f"{sorted(missing_context_questions)}"
        )
    if config["rfe"] not in clinician_rfe_minimum.get(
        "audited_reason_for_encounters", []
    ):
        raise CompilationError(
            f"clinician minimum dataset has not audited {config['rfe']}"
        )
    rfe_additional_facts = set(
        clinician_rfe_minimum.get("additional_required_facts_by_rfe", {})
        .get(config["rfe"], [])
    )
    missing_rfe_facts = rfe_additional_facts - all_fact_ids
    if missing_rfe_facts:
        raise CompilationError(
            "clinician minimum dataset references package-missing Facts: "
            f"{sorted(missing_rfe_facts)}"
        )
    package_question_fact_ids = set(indexes["questions_by_fact"])
    missing_rfe_questions = rfe_additional_facts - package_question_fact_ids
    if missing_rfe_questions:
        raise CompilationError(
            "clinician minimum dataset has package Facts without questions: "
            f"{sorted(missing_rfe_questions)}"
        )

    interoperability_coverage = build_package_interoperability_coverage(
        profile=profile,
        rfe=config["rfe"],
        package_fact_ids=all_fact_ids,
        clinician_context_fact_ids=context_facts,
    )
    package_coverage = coverage(node_index, indexes, simulations, sorted_rules)
    package_coverage["interoperability"] = {
        "framework": "USCDI",
        "framework_version": interoperability_coverage["core"]["framework_version"],
        "mapped_element_count": interoperability_coverage["core"]["mapped_element_count"],
        "eligible_element_count": interoperability_coverage["core"]["eligible_element_count"],
        "coverage_percent": interoperability_coverage["core"]["coverage_percent"],
        "applicable_uscdi_plus_domains": [
            item["domain_id"] for item in interoperability_coverage["uscdi_plus_domains"]
        ],
        "clinical_authority": False,
    }

    package: dict[str, Any] = {
        "package_id": config["package_id"],
        "package_version": config["package_version"],
        "release_state": "draft",
        "usage_policy": {
            "allowed_modes": ["research_test", "simulation"],
            "production_allowed": False,
            "unreviewed_knowledge_allowed": True,
            "overdue_research_behavior": "allow_with_warning",
        },
        "scope": {
            "care_domain": "primary_care",
            "encounter_contexts": ["context.primary_care"],
            "reasons_for_encounter": [config["rfe"]],
            "production_enabled": production,
        },
        "knowledge_graph": graph,
        "rule_graph": {**rule_graph, "rules": sorted_rules},
        "indexes": indexes,
        "source_manifest": sources,
        "research_source_manifests": [
            load_json(path) for path in config["research_manifests"]
        ],
        "refresh_policy": load_json(ROOT / "policies/knowledge-refresh.json"),
        "interview_completion_policy": completion_policy,
        "pain_assessment_context": ({
            "id": pain_assessment["id"],
            "version": pain_assessment["version"],
            "status": pain_assessment["status"],
            "review_status": pain_assessment["review_status"],
            "resource_ref": str(HIRA_PAIN_ASSESSMENT.relative_to(ROOT)),
            "semantic_digest": semantic_digest(pain_assessment),
            "recording_requirements": pain_assessment["recording_requirements"],
        } if pain_assessment else None),
        "clinician_submission_context": {
            "id": clinician_submission_context["id"],
            "version": clinician_submission_context["version"],
            "status": clinician_submission_context["status"],
            "review_status": clinician_submission_context["review_status"],
            "resource_ref": str(CLINICIAN_SUBMISSION_CONTEXT.relative_to(ROOT)),
            "semantic_digest": semantic_digest(clinician_submission_context),
            "session_facts": [context_facts["interview.additional_comment"]],
        },
        "interoperability_coverage": interoperability_coverage,
        "simulations": simulations,
        "coverage": package_coverage,
        "compatibility": {
            "runtime_min": "0.1.0",
            "runtime_max_tested": "0.1.0",
            "rule_language": "0.1.0",
            "clinical_memory_schema": "0.2.0",
        },
        "provenance": {
            "created_by": {"type": "compiler", "id": "compiler.build_package"},
            "created_at": os.environ.get("SOURCE_DATE_EPOCH_ISO", "2026-07-13T00:00:00Z"),
            "source_refs": [
                str(graph_path.relative_to(ROOT)),
                str(rules_path.relative_to(ROOT)),
                str(sources_path.relative_to(ROOT)),
                "mappings/interoperability/uscdi-v6-core.json",
                "mappings/interoperability/uscdi-plus-domain-overlays.json",
                "policies/uscdi-interoperability-overlay.json",
            ],
            "review_status": "unreviewed",
            "version": "0.1.0",
        },
    }
    package["semantic_digest"] = semantic_digest(package)
    return package


def write_package(package: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(output)


def validate_package(package: dict[str, Any]) -> None:
    digest = package.get("semantic_digest")
    unsigned = {key: value for key, value in package.items() if key != "semantic_digest"}
    expected = semantic_digest(unsigned)
    if digest != expected:
        raise CompilationError("package semantic digest mismatch")
    graph = package.get("knowledge_graph")
    rules = package.get("rule_graph")
    if not isinstance(graph, dict) or not isinstance(rules, dict):
        raise CompilationError("package missing graph")
    node_index = validate_graph(graph)
    validate_rules(rules, node_index, bool(package.get("scope", {}).get("production_enabled")))
    interoperability = package.get("interoperability_coverage")
    if not isinstance(interoperability, dict):
        raise CompilationError("package missing USCDI interoperability Coverage")
    if interoperability.get("clinical_authority") is not False:
        raise CompilationError("USCDI interoperability Coverage cannot control clinical behavior")
    if interoperability.get("completion_authority") is not False:
        raise CompilationError("USCDI interoperability Coverage cannot control completion")
    if interoperability.get("core", {}).get("framework_version") != "v6":
        raise CompilationError("unsupported USCDI core baseline")
    allowed_mapping_statuses = {
        "exact", "partial", "broader", "narrower", "contextual", "unmapped",
        "not_patient_collectable",
    }
    for element in interoperability.get("core", {}).get("elements", []):
        if element.get("mapping_status") not in allowed_mapping_statuses:
            raise CompilationError("USCDI element has unsupported mapping status")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PACKAGE_PROFILES), default="cough")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()

    if args.validate:
        validate_package(load_json(args.validate.resolve()))
        print(f"PACKAGE VALID: {args.validate}")
        return

    package = compile_package(production=args.production, profile=args.profile)
    output = (args.output or PACKAGE_PROFILES[args.profile]["output"]).resolve()
    write_package(package, output)
    print(
        f"PACKAGE BUILT: {output} "
        f"({package['semantic_digest']}, "
        f"{package['coverage']['simulation_count']} simulations)"
    )


if __name__ == "__main__":
    main()
