# Knowledge Storage: Git-Canonical, Database-Served Hybrid

Status: Proposed for backend implementation
Date: 2026-08-20

## Decision

Do not replace the repository Knowledge files with a mutable database as the
clinical source of truth. Keep reviewed and research Knowledge, Facts,
Questions, Rules, terminology bindings, provenance, source digests,
Simulations, and compiled package manifests in Git-controlled files. Publish
each validated compiled release into an operational database as an immutable,
content-addressed read model for backend lookup.

This preserves reproducible build, diff, review, rollback, provenance, and
offline Simulation while allowing indexed runtime retrieval, tenant release
selection, observability, and horizontal API scaling.

## Boundaries

```text
authoring files + source cache
        -> validation / simulation / compilation
        -> signed immutable package release
        -> database read model / object storage
        -> stateless Runtime API
        -> ephemeral or separately governed encounter store
```

- Git files are canonical Build-Time knowledge.
- The database is a deployment projection, never a live authoring surface.
- Runtime selects one exact package release and may not mutate it.
- Patient answers, attachments, and transcripts never enter Knowledge tables.
- Production encounter data requires a separate encrypted store, access
  policy, retention schedule, audit log, and legal basis. The current anonymous
  demo remains memory-only.

## Minimum operational schema

- `knowledge_release`: package id, semantic version, lifecycle/review/use
  status, manifest digest, source commit, compiled timestamp, signature.
- `knowledge_object`: release id, object type, stable object id, JSON payload,
  payload digest, provenance id.
- `knowledge_edge`: release id, from id, relation, to id.
- `terminology_binding`: release id, owner id, system, version, code,
  relation, ValueSet canonical, verification status and timestamp.
- `source_provenance`: source id/version/URL/license/digest/refresh metadata.
- `release_coverage`: release id, RFE, metric, numerator, denominator, gate.
- `tenant_release_assignment`: tenant/environment and pinned release id.

Use PostgreSQL JSONB initially. Add normalized indexed columns only for stable
query dimensions (`release_id`, `object_type`, `object_id`, `rfe_id`, status,
terminology system/code). Large licensed or source artifacts belong in
encrypted object storage referenced by digest, not duplicated into JSONB.

## Publication gate

1. Validate canonical files and provenance.
2. Run privacy scan, all unit tests, Simulations, Coverage and terminology
   audits.
3. Compile an immutable package.
4. Calculate manifest and object digests.
5. Insert a new release transactionally; never update an existing release.
6. Verify database rows against the manifest.
7. Promote a tenant/environment pointer atomically.
8. Retain the previous release for rollback.

## Not recommended

- Editing clinical Rules or codes directly in production tables.
- Storing only the latest version.
- Mixing patient session data with Knowledge objects.
- Letting an LLM write Knowledge rows at Runtime.
- Querying unversioned terminology results without provenance.

## Migration sequence

1. Add a read-only package repository interface while retaining filesystem
   loading as the reference implementation.
2. Add PostgreSQL publication and manifest verification tooling.
3. Deploy the database-backed repository in shadow mode and compare exact
   retrieved object digests with filesystem results.
4. Switch backend reads only after parity tests pass.
5. Keep filesystem compilation and disaster-recovery loading available.
