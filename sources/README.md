# Sources

Build-Time Source Manifests live in `manifests/`.

A manifest records identity, version, path, digest, completeness, licensing status,
limitations, and provenance. Runtime never reads external sources or this directory
during an interview.

The cough, fever, and dyspnea manifests are research-only. External guideline artifacts
are not yet cached or license-verified.

Report monitoring work due under the refresh policy:

```bash
python3 sources/check_refresh.py --as-of 2026-07-20
python3 sources/check_refresh.py --manifest sources/manifests/primary-care-fever-research.json
python3 sources/check_refresh.py --manifest sources/manifests/primary-care-dyspnea-research.json
```

With no `--manifest`, the command checks every `*-research.json` manifest. Use
`--manifest` only when intentionally narrowing the report to one profile. The
command schedules checks only. It does not access the network or claim that an
upstream source was reviewed.
