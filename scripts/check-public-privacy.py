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
    ("private first name marker", re.compile("S[ée]" + "bastien", re.I)),
    ("private last name marker", re.compile("Rob" + "ert", re.I)),
    ("private handle marker", re.compile("stien" + "-" + "ro" + "bert", re.I)),
    ("private email marker", re.compile("se" + "b@", re.I)),
]
PRIVATE_KEY_PATTERN = "-" * 5 + "BEGIN (?:RSA |OPENSSH |EC |DSA |)" + "PRIVATE" + " KEY" + "-" * 5
SECRET_PATTERNS = [
    ("private key marker", re.compile(PRIVATE_KEY_PATTERN)),
    ("secret-like assignment", re.compile(r"(?i)(api[_-]?key|secret|password|token|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
    ("GitHub token marker", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("GitHub PAT marker", re.compile(r"github" + r"_pat_[A-Za-z0-9_]{20,}")),
]
LOCAL_ENV_PATTERNS = [
    ("private assistant marker", re.compile("Sky" + "net", re.I)),
    ("private agent marker", re.compile("Her" + "mes", re.I)),
    ("private storage marker", re.compile(r"\b" + "N" + "AS" + r"\b", re.I)),
    ("private storage vendor marker", re.compile("Asus" + "tor", re.I)),
    ("private local path marker", re.compile(r"/(?:opt|home)/" + "data" + r"\b")),
    ("private host domain marker", re.compile("sky" + "-" + "net", re.I)),
    ("private network address marker", re.compile(r"\b(?:10|192\.168)\.\d{1,3}\.\d{1,3}\b")),
    ("local build diagnostic marker", re.compile("local" + " Docker" + " build", re.I)),
    ("local daemon diagnostic marker", re.compile("daemon" + "-side empty", re.I)),
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
            for label, pattern in PII_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{lineno}: {label}")
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{lineno}: {label}")
            for label, pattern in LOCAL_ENV_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{lineno}: {label}")
    if findings:
        print("privacy_guard=fail")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("privacy_guard=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
