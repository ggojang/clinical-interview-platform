# Source Material Archive

`docs/source/` stores official source documents that are useful for reproducible
Build-Time Knowledge acquisition.

Source files may be added only when all of the following are true:

- the publisher and official download location are identifiable;
- the file is a stable source artifact rather than a patient-specific record;
- download, local retention, and repository redistribution are permitted;
- provenance, source version or publication date, acquisition date, canonical
  URL, license status, and checksum can be recorded;
- the file contains no real patient response, direct identifier, or original
  interview transcript.

Restricted, subscription-only, or redistribution-uncertain material must not be
committed. Its metadata and canonical URL belong in `sources/manifests/`, with
the source marked incomplete and the applicable license limitation recorded.

Downloaded files are immutable evidence. A newer edition is added as a new
versioned artifact rather than overwriting the prior file. Derived Knowledge,
Fact, Rule, and Question candidates remain `unreviewed` and `research_only`
until the normal review process changes their status.

Runtime never reads this directory, browses source websites, or derives clinical
behavior directly from archived files. The Knowledge Builder uses normalized,
versioned repository artifacts produced from these sources.
