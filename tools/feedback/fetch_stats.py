#!/usr/bin/env python3
"""Fetch aggregate anonymous test statistics without exposing an admin key."""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    base = os.environ.get("FEEDBACK_API_BASE_URL", "").rstrip("/")
    key = os.environ.get("FEEDBACK_ADMIN_KEY", "")
    if not base.startswith("https://") or len(key) < 24:
        parser.error(
            "set HTTPS FEEDBACK_API_BASE_URL and FEEDBACK_ADMIN_KEY (24+ chars)"
        )
    query = urllib.parse.urlencode({"days": max(1, min(365, args.days))})
    request = urllib.request.Request(
        f"{base}/v1/admin/stats?{query}",
        headers={"X-Admin-Key": key, "accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        report = json.load(response)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
