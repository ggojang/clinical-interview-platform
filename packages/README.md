# Knowledge Packages

`generated/` contains immutable Compiler outputs consumed by Runtime.

Each package includes the Knowledge Graph, Rule Graph, indexes, Source Manifest,
Simulation metadata, Coverage, compatibility metadata, provenance, and a semantic
integrity digest. No patient or session data belongs in a package.

The active research artifacts are `generated/primary-care-cough-0.3.0.json`,
`generated/primary-care-fever-0.1.0.json`, and
`generated/primary-care-dyspnea-0.1.0.json`.
Generated package filenames are immutable version identifiers; a behavior change
must create a new package version.
