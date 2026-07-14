# Provenance Specification

Every knowledge item, generated simulation, derived fact, and runtime assertion must be traceable.

## Minimum provenance fields

- creator type: human, AI, importer, runtime;
- creator identifier;
- creation timestamp;
- source references;
- review status;
- version.

## Review statuses

- `unreviewed`
- `in_review`
- `reviewed`
- `rejected`
- `deprecated`

AI-generated content defaults to `unreviewed`.

## Runtime provenance

A runtime fact must identify the patient evidence that supports it. A derived assertion must identify the rule and source facts used.
