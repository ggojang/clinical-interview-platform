# Restricted questionnaire test store

Source-defined questionnaires whose item text is not cleared for repository
distribution must not be committed here or under `docs/gpt`.

For an internal test:

1. Obtain the exact official artifact through its required access process.
2. Confirm that internal electronic testing is permitted, or record written permission.
3. Convert or obtain it as a FHIR R4 `Questionnaire` without rewriting its wording,
   options, order, recall period, enablement, or scoring semantics.
4. Put the JSON file under `private-data/questionnaires/content/`.
5. Copy `questionnaire-test-registry.example.json` to
   `private-data/questionnaires/registry.json` and record the source, exact version,
   SHA-256 digest, rights status, and `enabled: true`.
6. Load it with `runtime.restricted_questionnaires.RestrictedQuestionnaireStore`.

The loader accepts only three rights states:

- `user_supplied_for_internal_test`
- `written_permission_for_internal_test`
- `artifact_license_allows_internal_test`

It verifies the local path, digest, FHIR resource type, status, and version. It does
not implement scoring, modify fixed items, export source content to the public GPT
bundle, or persist patient responses.

CHS, KHP, and KLoSA are registered as acquisition candidates, but their original
items are not included in this public repository. Embedded third-party instruments
require a separate owner review even when the surrounding survey is available.
