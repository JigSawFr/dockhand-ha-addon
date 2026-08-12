#!/usr/bin/env python3
"""Scan public files for accidental PII/secrets."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOW = {
    "${{ secrets.GITHUB_TOKEN }}",
    "id-token: write",
}
PII_PATTERNS = [
    re.compile(r"S[ée]bastien", re.I),
    re.compile("Rob" + "ert", re.I),
    re.compile("stien" + "-" + "ro" + "bert", re.I),
    re.compile("se" + "b@", re.I),
]
PRIVATE_KEY_PATTERN = "-" * 5 + "BEGIN (?:RSA |OPENSSH |EC |DSA |)" + "PRIVATE" + " KEY" + "-" * 5
SECRET_PATTERNS = [
    re.compile(PRIVATE_KEY_PATTERN),
    re.compile(r"(?i)(api[_-]?key|secret|password|token|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github" + r"_pat_[A-Za-z0-9_]{20,}"),
]
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def git_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / line for line in out.splitlines() if line]


def main() -> int:
    findings: list[str] = []
    for path in git_files():
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(allowed in line for allowed in ALLOW):
                continue
            for pattern in PII_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{lineno}: pii pattern {pattern.pattern!r}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{lineno}: secret-like pattern {pattern.pattern!r}")
    if findings:
        print("privacy_guard=fail")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("privacy_guard=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
