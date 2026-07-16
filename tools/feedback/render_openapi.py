#!/usr/bin/env python3
"""Render the separate feedback Action schema for one deployed HTTPS origin."""
from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    origin = args.base_url.rstrip("/")
    parsed = urlparse(origin)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path not in {"", "/"}:
        parser.error("--base-url must be an HTTPS origin without a path")
    template = (
        ROOT / "services/feedback-worker/openapi.template.yaml"
    ).read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        template.replace("https://FEEDBACK_API_HOST", origin), encoding="utf-8"
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
