# Health-screening package test catalog

This directory is an isolated, removable test catalog for the Custom GPT
read-only Action. It is not part of the Clinical Knowledge/Fact build and does
not contain patient responses.

## Runtime loading

1. Read `registry.json` and use only `current_version`.
2. Read that version's `metadata.json`.
3. Read one public region's `index.json`, then its declared pages.
4. Read package details only by an opaque `package_id` returned by a page.

The Action parameters are limited to catalog version, public browsing-region
identifier, page number, and package identifier. Patient answers, clinical
profiles, budgets, free text, and identifiers must never be sent to this
Action. Candidate matching occurs locally in conversation state.

## Replace or add a version

Install the isolated import dependency, then build a new immutable version:

```bash
python3 -m pip install -r tools/test_catalogs/requirements.txt
python3 tools/test_catalogs/build_health_screening_package_catalog.py build \
  --input /path/to/korea_health_checkup_packages.xlsx \
  --version YYYY-MM-DD.N \
  --activate
```

The source workbook is not committed. Generated package entries retain its
SHA-256 digest, worksheet name, source row, listing status, and source URL.
Rebuilding an existing version is rejected to prevent an unnoticed mutable
canonical. Create a new version, verify it, and activate it.

## Switch or remove

```bash
python3 tools/test_catalogs/build_health_screening_package_catalog.py activate \
  --version YYYY-MM-DD.N

python3 tools/test_catalogs/build_health_screening_package_catalog.py remove \
  --version YYYY-MM-DD.N
```

Removing the active version requires `--force-current` and leaves
`current_version` empty, which blocks package recommendation. To remove this
temporary feature completely, delete this directory, the generator and its
requirements file, and the five contiguous test-catalog paths/parameters in
`docs/gpt/openapi.yaml`. The clinical Knowledge build remains unaffected.

## Interpretation boundary

Package wording, listed prices, and URLs are unreviewed test inputs. Parsed
price bounds and lexical tags are navigation aids only. Before a user acts,
the institution must confirm current composition, price, eligibility, and
availability.
