# SNOMED CT Finding-Site Laterality

Version: 0.1.0 (Research Draft)

An anatomical site may receive laterality only when the versioned site concept is a member of `723264001 |Lateralizable body structure reference set|` and the focus concept satisfies the applicable MRCM and normal-form constraints.

Laterality is not modeled as a parallel attribute on the focus clinical finding in the classifiable expression. It is nested on the value of `363698007 |Finding site|`:

```text
=== {focus} :
{ 363698007 |Finding site| =
  ( {site} : 272741003 |Laterality| = {side} ) }
```

The supported side qualifiers are `7771000 |Left|` and `24028007 |Right|`. User input meaning bilateral may be represented in a close-to-user expression with `51440002 |Right and left|`, but its classifiable form is expanded into two role groups: one left and one right.

The Builder must reject post-coordination when the site is not a verified refset member, the site already states laterality, the focus has no Finding site, or multiple Finding site values differ. Failure to validate never blocks the interview: Clinical Memory retains the finding-site and laterality Facts separately without emitting a post-coordinated candidate.

Reference-set membership and MRCM validation are terminology operations. They never create a clinical Rule or determine question priority, diagnosis, safety, or escalation.
