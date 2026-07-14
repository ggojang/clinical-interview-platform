# Korean Claim-Code Binding

Version: 0.1.0 (Research Draft)

Clinical meaning and reimbursement classification are separate layers. SNOMED CT and the original Clinical Memory Fact retain the clinical meaning. A KCD or HIRA EDI code is an additional, versioned mapping with independent provenance.

Claim-code lookup is reactive, not a routine enrichment step. It is activated only when the user supplies an exact code, a claim-catalog name, a medication product name, asks for claim-code verification, or provides a document or scan containing an explicit code or name. Symptoms, ordinary clinical Facts, AI-generated differentials, and suggested tests or treatments do not activate claim lookup. The questionnaire must not proactively ask the patient for a claim code.

For an uploaded document, extraction occurs in the conversation context. Only the minimal extracted code or short catalog name may be sent to STOM; the file, image, surrounding narrative, and direct identifiers must not be transmitted. The document location and OCR uncertainty remain attached to the local evidence. An uncertain OCR result is confirmed or left unresolved before code selection.

The binding domain must be selected before lookup:

- diagnosis: KCD-8 or KCD-9;
- procedure: HIRA EDI procedure;
- medication: HIRA EDI medication;
- therapeutic material: HIRA EDI material.

KCD-8 free-text search is currently exposed by STOM. KCD-9 codes can be verified through the FHIR CodeSystem `$lookup` operation. The KCD-9 morphology search is specific to tumor morphology and must not be used as a general diagnosis search. A KCD-8 code must never be assumed to remain identical in KCD-9 without an explicit versioned mapping or KCD-9 verification.

HIRA procedure, medication, and material catalogs have separate search and detail operations. Search results are candidates. Product or item selection requires sufficient context, and a therapeutic-material group result is not a final billable item code.

Claim codes never establish a diagnosis and never control interview priority, safety, differential diagnosis, or escalation. If terminology lookup or exact selection fails, the clinical interview continues and the claim mapping remains unresolved.

A possible differential generated at questionnaire completion must not be emitted as a final claim diagnosis. Diagnosis-code binding requires an explicit diagnosis context and remains a candidate until the appropriate clinical or billing workflow confirms it.

When an allowed claim-information trigger is present and both a SNOMED CT concept and a KCD/HIRA code can be verified for the same information, both codings are retained. Neither coding replaces the other. The binding records whether their meanings are exact, equivalent, broader, narrower, related, or unresolved, together with versions, sources and verification provenance. Name similarity alone cannot establish exact or equivalent meaning.

FHIR may place both codings in one `CodeableConcept` only for a verified exact or equivalent meaning. Broader, narrower, or merely related codings remain linked in the internal binding but are not collapsed into a single equivalent-coding assertion.
