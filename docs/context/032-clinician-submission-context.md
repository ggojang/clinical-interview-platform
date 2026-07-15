# Clinician Submission Context

Version: 0.1 (Draft)

---

# Purpose

Clinician Submission Context defines the reusable background information and completion evidence needed when an adaptive interview result will be submitted to a healthcare professional.

It supplements, but does not replace, Reason-for-Encounter-specific Knowledge, Facts, safety Rules or Questions.

It is not a fixed questionnaire.

It is not a FHIR representation.

---

# Activation

The context is activated explicitly for clinician-submission use.

Package-specific safety assessment and clinically required Facts are collected first. The shared context is then completed without changing the package's clinical routing.

Legacy research simulations may run without this context. Clinician-submission simulations must enable it explicitly.

---

# Required Context

Every activated clinician-submission interview resolves:

- longitudinal context review state;
- information source;
- age in completed years;
- sex or anatomy context needed for clinical care;
- final additional comment.

On a first encounter, when all background groups are due, or when recency is unknown, it also resolves:

- current and past diagnoses, including timing and current status;
- surgery and major procedures, including timing, indication and important complications;
- prescription, nonprescription and supplement use, including name, dose, route, frequency and purpose;
- allergy agent, reaction and severity;
- family relationship, condition and age at onset when known;
- occupation, duration and clinically relevant exposure;
- smoking status, amount, duration, cessation timing and pack-years when calculable;
- alcohol frequency, type and amount.

Medication alone is rechecked when only its shorter review interval is due.

Height, weight, blood group, immunization history and measurements are collected when relevant rather than treated as universal requirements.

---

# Reason-for-Encounter Minimum Dataset

Common background history alone is insufficient for clinician submission.

Every adaptive Reason-for-Encounter package is audited for a clinician minimum dataset covering:

- presentation and the person's own description;
- onset, duration and course;
- site, laterality and radiation when applicable;
- character and severity;
- timing, frequency and triggers when applicable;
- functional impact;
- associated positive and pertinent negative findings;
- safety red flags;
- prior episodes, diagnoses, tests and clinical evaluation;
- treatment already attempted, response and adverse effects;
- relevant conditions, medicines, procedures, exposures and risk context;
- the person's main concern and expected help.

Package-specific Facts remain the authority for symptom detail and safety. The shared module adds only cross-cutting clinician-summary Facts and identifies existing package Facts that must become required in clinician-submission mode.

Conditional anatomy, pregnancy, exposure and other branch Facts retain their applicability rules. A non-applicable branch is resolved explicitly rather than inferred as negative.

The compiler rejects a package when its clinician minimum dataset references a missing Fact, lacks a Question for a required Fact, or has not audited that Reason for Encounter.

---

# Missing Information

Known absence is a clinical answer.

Unknown, declined, not applicable, conflicted and never asked are distinct states. They must not be converted to a negative answer.

`dataAbsentReason` is preserved whenever information is unavailable.

---

# Clinician Handoff

The internal handoff groups Facts into:

- Reason-for-Encounter clinical summary, including prior evaluation, attempted treatment, functional impact and the person's concern;
- encounter and information source;
- demographics and relevant clinical context;
- medical, surgical and immunization history;
- medication and allergy information;
- family, occupation, smoking and alcohol history;
- available measurements;
- final and off-path additional comments.

Each entry retains its Fact identifier, state, value, `dataAbsentReason` and confidence when available.

The handoff is `research_only` and `unreviewed` until clinical review is completed.

---

# Deferred Projections

Fixed questionnaires remain source-preserving workflows with their own items and answer options.

FHIR R4 resources are later projections of Clinical Memory and the clinician handoff. FHIR structure must not control current Fact collection or completion semantics.
