# Knowledge Acquisition

Version: 0.1 (Draft)

---

# Purpose

This document defines Knowledge Acquisition.

Knowledge Acquisition is the process by which external medical sources are collected, identified, versioned, normalized, and prepared for the Knowledge Builder.

Knowledge Acquisition does not create Runtime knowledge.

Knowledge Acquisition does not generate Questions.

Knowledge Acquisition does not modify the Knowledge Graph directly.

Its responsibility is to produce trustworthy, reproducible, and traceable source material for later transformation.

---

# Core Principle

External medical knowledge is acquired at Build Time.

Runtime never performs Knowledge Acquisition.

The Interview Runtime must never search, browse, download, or interpret external medical sources during a patient interview.

The acquisition boundary is strict.

```text
External Sources
        ↓
Knowledge Acquisition
        ↓
Source Cache
        ↓
Normalization
        ↓
Knowledge Builder
```

---

# Acquisition Objectives

Knowledge Acquisition must answer the following questions:

What source was acquired?
Who published it?
Which version was acquired?
When was it acquired?
How was it acquired?
Was the content complete?
Was the content modified?
Is the source permitted for this use?
What repository objects were later derived from it?

If any of these questions cannot be answered, the source is incomplete.

Source Categories

Knowledge Acquisition treats source categories differently.

Terminology Sources

Examples:

SNOMED CT
SNOMED CT reference sets
SNOMED CT MRCM
LOINC
ICPC-2
ICD
local terminology systems

Purpose:

semantic alignment;
hierarchy;
terminology scope;
concept relationships;
permissible attributes;
classification and indexing.

Terminology sources do not directly determine Question priority.

Interoperability Sources

Examples:

FHIR R4 specification;
FHIR Resource definitions;
FHIR profiles;
ValueSet bindings;
ConceptMap resources;
StructureDefinition resources.

Purpose:

export structure;
mapping targets;
data-type constraints;
element bindings;
interoperability validation.

FHIR does not define clinical interview behavior.

Guideline Sources

Examples:

NICE;
CHEST;
ERS;
GINA;
GOLD;
CDC;
USPSTF;
national and local clinical guidelines.

Purpose:

safety priorities;
interview scope;
red flags;
clinically important discriminators;
follow-up requirements;
eligibility and contraindication rules.

Guidelines must be interpreted before becoming executable rules.

Evidence Sources

Examples:

systematic reviews;
meta-analyses;
evidence reports;
high-quality consensus documents;
selected primary research.

Purpose:

candidate Fact discovery;
evidence clarification;
conflict resolution;
knowledge-gap investigation.

Evidence sources do not automatically override reviewed guidelines.

Primary Care Scope Sources

Examples:

GP/FP reference sets;
ICPC-2 Reason for Encounter and Problem classifications;
primary-care encounter datasets;
national primary-care service definitions;
approved local scope documents.

Purpose:

bootstrap scope;
coverage planning;
Reason for Encounter indexing;
Problem indexing;
domain prioritization.

These sources support scope and navigation.

They do not define the internal semantics of the Interview Engine.

Local Sources

Examples:

hospital protocols;
clinic policies;
jurisdiction-specific forms;
vaccination schedules;
referral pathways;
administrative requirements.

Local sources must include jurisdiction and validity period.

Local sources must never silently override international or national guidance.

STOM Integration

STOM is a Build-Time terminology provider.

Current endpoint:

https://stom.infoclinic.co/fhir

Current FHIR baseline:

FHIR R4

STOM may be used to acquire:

CodeSystem resources;
ValueSet resources;
ConceptMap resources;
NamingSystem resources;
StructureDefinition resources where supported;
CodeSystem $lookup results;
CodeSystem $validate-code results;
CodeSystem $subsumes results;
ValueSet $expand results;
ValueSet $validate-code results;
ConceptMap $translate results.

STOM is not a Runtime dependency.

STOM Acquisition Rules

All STOM requests used in Knowledge Build must record:

base URL;
FHIR version;
operation;
request parameters;
terminology system URI;
terminology version URI;
language;
response timestamp;
HTTP status;
response content type;
response digest;
acquisition tool version;
build identifier.

Responses must be stored in the Source Cache before transformation.

SNOMED CT Versioning

SNOMED CT version must always be explicit during reproducible builds.

Example:

http://snomed.info/sct/11000267109/version/20260615

A build must not depend on an unspecified “latest” version.

The terminology version used by a released Knowledge Package must remain immutable.

When a new SNOMED CT edition is loaded into STOM:

Terminology Load
        ↓
Terminology Event
        ↓
Candidate Rebuild
        ↓
Validation
        ↓
New Baseline
        ↓
Explicit Runtime Release

Existing Runtime Packages remain unchanged.

Release Frequency

Terminology systems and evidence sources have different acquisition schedules.

Terminology

Terminology acquisition is event-driven.

Examples:

new SNOMED CT edition loaded;
new LOINC release installed;
new ConceptMap published;
GP/FP reference set updated.

There is no need for frequent polling when the source is manually loaded and version-controlled.

Guidelines

Guideline monitoring may be scheduled more frequently than terminology monitoring.

The exact schedule is configurable.

Detected changes enter a Candidate Queue.

They do not immediately alter Runtime behavior.

Evidence Literature

Evidence discovery may run on a shorter schedule.

New literature is treated as candidate evidence.

It must not automatically create active Facts or Rules.

Runtime and Simulation Feedback

The following events must create immediate Knowledge Review candidates:

repeated missing Fact;
unsafe Question ordering;
failed red-flag detection;
excessive Question burden;
duplicated Questions;
unresolved common-cause branch;
hallucinated assertion;
incomplete provenance;
mapping failure;
simulation regression.

Runtime feedback is evidence of a Knowledge gap.

It is not itself medical truth.

Acquisition Modes
Bootstrap Acquisition

Used when creating the first Knowledge Baseline.

Bootstrap Acquisition gathers enough source material to support the declared Primary Care scope.

It must not attempt to import all available medical knowledge.

Bootstrap follows Coverage priority.

Incremental Acquisition

Used for new or changed sources.

Only affected source material should be reacquired.

Incremental Acquisition must preserve existing source identifiers.

Triggered Acquisition

Executed in response to a specific event.

Examples:

terminology release;
guideline revision;
critical safety notice;
simulation failure;
new Reason for Encounter;
new jurisdiction;
new language.
Manual Acquisition

Used when an authorized person explicitly provides a source.

Manual acquisition still requires full provenance.

Manual upload does not imply approval.

Source Manifest

Every source must have a Source Manifest.

Minimum fields:

source_id: source.nice.example
source_type: guideline
publisher: NICE
title: Example guideline
canonical_url: null
version: null
publication_date: null
effective_date: null
retrieved_at: null
language:
  - en
jurisdiction:
  - GB
license:
  status: unknown
acquisition:
  method: manual
  tool: null
  tool_version: null
content:
  media_type: application/pdf
  sha256: null
review:
  status: unreviewed

A source without a manifest cannot enter the Builder.

Source Identity

Every source requires a stable identifier.

The identifier must not depend only on a filename.

Good:

source.nice.ng120.2025

Bad:

guideline-final-v2.pdf

Source identity should remain stable across storage locations.

Source Cache

Acquired material is stored in a read-only Source Cache.

Recommended structure:

knowledge/
└── source-cache/
    ├── terminology/
    │   ├── stom/
    │   ├── snomed/
    │   ├── loinc/
    │   └── icpc/
    ├── fhir/
    ├── guidelines/
    ├── evidence/
    ├── local/
    └── manifests/

The Source Cache contains acquired material.

It does not contain reviewed Knowledge Graph objects.

Immutability

A cached source response is immutable.

If a source changes, a new cached object must be created.

Do not overwrite source evidence.

Example:

lookup-64572001-ko-20260615.json
lookup-64572001-ko-20260731.json

Both may coexist.

Raw and Normalized Sources

Raw acquisition and normalized source records must be separated.

Raw Source
        ↓
Normalized Source

Raw Source preserves the original response.

Normalized Source provides a consistent internal representation.

Normalization must never destroy the original.

Content Digests

Every cached object must include a cryptographic digest.

Recommended:

SHA-256

Digests are used for:

change detection;
reproducibility;
provenance;
cache validation;
build verification.
Language

Language must always be explicit.

Terminology acquisition may request:

Korean preferred terms;
English preferred terms;
FSN;
synonyms;
designations.

A multilingual response must preserve the language and designation type of every term.

Jurisdiction

Jurisdiction must be explicit where clinically relevant.

Examples:

vaccination;
screening;
prescribing;
referral;
occupational requirements;
administrative forms.

A rule derived from one jurisdiction must not be silently applied to another.

Licensing

Knowledge Acquisition must record source licensing.

Licensed terminology content must not be redistributed in ways that violate its license.

Repository outputs must distinguish:

source identifiers;
derived internal identifiers;
licensed text;
non-licensed metadata;
redistributable mappings.

License status is part of provenance.

Acquisition Validation

Every acquisition must pass basic validation.

Validation includes:

successful retrieval;
expected media type;
non-empty content;
parsable structure where applicable;
stable source identity;
explicit version;
content digest;
provenance completeness.

FHIR responses must additionally validate:

resourceType;
expected operation response;
expected FHIR version;
valid Parameters structure;
valid ValueSet expansion;
valid OperationOutcome handling.
FHIR Operation Acquisition
CodeSystem $lookup

The acquisition record must preserve:

system;
version;
code;
display language;
requested properties;
returned display;
returned designations;
returned properties;
inactive status;
response digest.
ValueSet $expand

The acquisition record must preserve:

canonical URL or inline ValueSet;
terminology version;
ECL or Refset expression;
filter;
offset;
count;
active-only behavior;
language;
designations;
total;
expansion identifier;
timestamp;
paging state.

Paged expansions must detect duplicates and omissions.

CodeSystem $subsumes

The acquisition record must preserve:

code A;
code B;
system;
version;
outcome;
request and response digest.
ConceptMap $translate

The acquisition record must preserve:

source coding;
target system;
ConceptMap version;
match equivalence;
dependency information;
translation result.
Refset Acquisition

Reference Set acquisition must distinguish:

the Refset definition;
Refset members;
referenced components;
member-specific fields;
terminology version;
active status.

A ValueSet expansion may be sufficient for concept membership.

It may be insufficient for MRCM or map member fields.

When additional fields are required, the acquisition process must preserve them through a supported API or imported release content.

MRCM Acquisition

MRCM acquisition may include:

domain reference set;
attribute domain reference set;
attribute range reference set;
module scope reference set;
domain constraint;
proximal primitive constraint;
attribute rule;
range constraint;
grouped flag;
cardinality;
in-group cardinality;
rule strength;
content type.

MRCM is used during Build Time.

Runtime never queries or executes raw MRCM content.

Guideline Acquisition

Guideline acquisition must identify:

publisher;
guideline identifier;
title;
version;
publication date;
revision date;
section;
recommendation identifier;
recommendation strength where available;
evidence quality where available;
jurisdiction;
superseded status.

A citation containing only the publisher name is insufficient.

Recommendation-Level Traceability

Derived Rule or Interview Target provenance should point to the smallest practical source unit.

Preferred:

Guideline
→ Section
→ Recommendation

Less preferred:

Guideline title only

Recommendation-level traceability is required for safety-critical Rules.

Candidate Queue

Newly acquired material enters a Candidate Queue.

Candidate states:

discovered
acquired
normalized
screened
accepted_for_build
rejected
superseded

Acquisition does not imply acceptance.

Review

Sources may be reviewed for:

authenticity;
relevance;
currency;
jurisdiction;
quality;
licensing;
completeness.

Review status must be recorded.

Provenance

Every acquisition creates provenance.

Minimum provenance:

source identifier;
acquisition activity;
acquisition agent;
acquisition tool;
tool version;
timestamp;
request;
response digest;
repository build identifier;
review status.

The full lineage must support:

External Source
        ↓
Cached Source
        ↓
Normalized Source
        ↓
Knowledge Node or Rule
        ↓
Compiled Package
        ↓
Runtime Decision
Failure Handling

Acquisition failures must be explicit.

Examples:

DNS failure;
timeout;
authentication failure;
invalid certificate;
unsupported operation;
malformed FHIR response;
missing terminology version;
pagination inconsistency;
license restriction;
unavailable source.

Failures must not produce placeholder medical knowledge.

Offline Acquisition

The Knowledge Builder may operate without external network access.

In this mode:

External Collection Environment
        ↓
Source Cache
        ↓
Offline Builder

The Builder consumes cached, validated source artifacts.

This is the preferred mode for reproducible builds.

Security

Acquisition credentials must never be stored in source files.

Secrets must be supplied through:

environment variables;
secret managers;
protected local configuration.

Logs must not expose secrets.

Personal Data

Knowledge Acquisition must not collect patient-identifiable data.

Runtime feedback entering Knowledge Acquisition must be de-identified or synthetic.

Medical-source acquisition and patient-data ingestion are separate processes.

Determinism

Given the same:

source manifests;
cached source content;
configuration;
Builder version;

Knowledge Acquisition output must be identical.

Network state must not affect an already cached build.

Repository Rules

Knowledge Acquisition:

must preserve raw source material;
must create a Source Manifest;
must record version and language;
must create a digest;
must preserve licensing metadata;
must not create active Runtime knowledge;
must not bypass review;
must not overwrite prior source evidence;
must not depend on unspecified latest versions.
Final Principle

Knowledge Acquisition establishes the evidence boundary of the repository.

It determines what external information entered the Knowledge Factory, in which version, through which process, and with which provenance.

Nothing may become repository knowledge unless its source can be reconstructed.
