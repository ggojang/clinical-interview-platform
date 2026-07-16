#!/usr/bin/env python3
"""Fetch aggregate anonymous test statistics without exposing an admin key."""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "https://clinical-interview-feedback.seungjong-yu.workers.dev"
DEFAULT_ADMIN_KEY_FILE = Path.home() / ".config/clinical-interview-platform/feedback-admin-key"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("FEEDBACK_API_BASE_URL", DEFAULT_BASE_URL),
    )
    parser.add_argument(
        "--admin-key-file",
        type=Path,
        default=Path(
            os.environ.get("FEEDBACK_ADMIN_KEY_FILE", DEFAULT_ADMIN_KEY_FILE)
        ),
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    key = os.environ.get("FEEDBACK_ADMIN_KEY", "")
    if not key and args.admin_key_file.is_file():
        key = args.admin_key_file.read_text(encoding="utf-8").strip()
    if not base.startswith("https://") or len(key) < 24:
        parser.error(
            "use an HTTPS base URL and provide a 24+ character administrator "
            "key through FEEDBACK_ADMIN_KEY or --admin-key-file"
        )
    query = urllib.parse.urlencode({"days": max(1, min(365, args.days))})
    request = urllib.request.Request(
        f"{base}/v1/admin/stats?{query}",
        headers={
            "X-Admin-Key": key,
            "accept": "application/json",
            "User-Agent": (
                "ClinicalInterviewResearchStats/1.0 "
                "(+https://github.com/ggojang/clinical-interview-platform)"
            ),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        report = json.load(response)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
