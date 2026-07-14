#!/usr/bin/env python3
"""Fail when repository content appears to contain secrets or patient response data."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SKIP_DIRS = {
    ".git", ".venv", "__pycache__", ".pytest_cache", "local-data",
    "private-data", "raw", "private", "sessions",
}
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".pdf"}
FORBIDDEN_PATH_PARTS = {
    "patient-responses", "patient_responses", "questionnaire-responses",
    "questionnaire_responses",
}
PATTERNS = {
    "Korean resident registration number": re.compile(r"(?<!\d)\d{6}[- ]?[1-8]\d{6}(?!\d)"),
    "PEM private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI API key": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in SKIP_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        yield path, relative


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path, relative in iter_files(root):
        lowered = {part.lower() for part in relative.parts}
        if lowered & FORBIDDEN_PATH_PARTS:
            findings.append(f"forbidden response path: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {relative}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    findings = scan(root)
    if findings:
        print("Privacy/secret scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Privacy/secret scan passed: no prohibited patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
