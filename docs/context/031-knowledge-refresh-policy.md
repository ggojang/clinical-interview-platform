# Knowledge Refresh Policy

Version: 0.1 (Draft)

---

# Purpose

This document defines how update intervals are calculated and enforced for repository knowledge.

The exact interval values from an earlier session were not present in the repository when this policy was created.

This policy therefore records a new calculation baseline and preserves that fact in provenance.

---

# Core Principle

Every knowledge object has an update policy.

Time-based review and event-triggered review are separate.

A passed date does not silently delete knowledge.

It changes whether the knowledge may be used in production or only in research testing.

---

# Source Monitoring Cadence

Source monitoring detects upstream changes.

It does not perform a complete clinical review on every check.

## Terminology Server and STOM

Check the terminology baseline, version, and digest every 30 days.

## NICE Guidance

Check guidance metadata, revision date, and digest every 7 days.

## Clinical Guidelines

Check ERS, GINA, BTS, and comparable guideline metadata or digest every 1 day.

Daily checking is automated.

A complete clinical review begins only when a change is detected or the full-review date is reached.

## Public Health Guidance

Check CDC and comparable public-health guidance every 7 days.

## Interoperability Standards and Domain Datasets

Check USCDI, USCDI+, FHIR implementation guidance and comparable versioned interoperability metadata every 7 days.

A detected change triggers mapping and Coverage review.

It does not directly change clinical questions, completion or Safety Rules.

---

# Knowledge Review Classes

## Safety Critical

Review status every 30 days.

Complete review every 90 days.

Overdue knowledge is excluded from production.

It may remain available in research tests with an explicit warning.

## Guideline Behavior

Review status every 90 days.

Complete review every 180 days.

Overdue knowledge is excluded from production compilation.

It may remain available for Simulation and regression.

## Terminology Mapping

Check mapping review status every 90 days.

Complete review every 180 days or whenever the terminology baseline changes.

An overdue mapping does not change internal Fact semantics.

## Stable Semantic

Check semantic review status every 180 days.

Complete review every 365 days.

These intervals apply to relatively stable atomic concepts, not safety behavior.

## Local Jurisdiction

Check local policy review status every 30 days.

Complete review every 90 days.

A jurisdiction or policy change triggers immediate review.

---

# Immediate Review Triggers

- upstream source version changed
- source withdrawn or corrected
- new safety signal
- conflicting reviewed source
- terminology baseline changed
- production incident
- jurisdiction policy changed

---

# Research-Test Use

Knowledge marked `unreviewed` or `research_only` may be compiled into a draft package only when the package declares `research_test` or `simulation` usage.

Runtime must reject that package in production mode.

Expired research knowledge remains traceable and testable but produces an explicit refresh warning.

---

# Required Metadata

Every generated knowledge object records

- refresh class
- source monitor profile
- source monitor interval
- calculated interval
- last reviewed or created date
- next monitor date
- next full review date
- immediate review triggers
- overdue behavior
- provenance

---

# Final Principle

Update intervals are part of knowledge governance.

They are explicit, computed, versioned, testable and never hidden in an agent memory.
