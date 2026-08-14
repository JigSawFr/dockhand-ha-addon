#!/usr/bin/env python3
"""Dry-run release metadata without publishing images or GitHub releases."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "dockhand/config.yaml"
CHANGELOG = ROOT / "dockhand/CHANGELOG.md"

VERSION_RE = re.compile(r'^version:\s+"(?P<version>[^"]+)"$', re.MULTILINE)
HEADER_RE = re.compile(r"^##\s+(?P<version>\S+)\s*$", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def config_version() -> str:
    match = VERSION_RE.search(read(CONFIG))
    if not match:
        raise SystemExit("Could not parse dockhand/config.yaml version")
    return match.group("version")


def release_notes(version: str) -> str:
    text = read(CHANGELOG)
    matches = list(HEADER_RE.finditer(text))
    for idx, match in enumerate(matches):
        if match.group("version") != version:
            continue
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        notes = text[start:end].strip()
        if not notes:
            raise SystemExit(f"Empty changelog section for {version}")
        return notes
    raise SystemExit(f"Missing changelog section for {version}")


def run_check_version(tag: str, quiet: bool = False) -> None:
    if not quiet:
        subprocess.run([sys.executable, "scripts/check-version-sync.py", "--tag", tag], cwd=ROOT, check=True)
        return

    result = subprocess.run(
        [sys.executable, "scripts/check-version-sync.py", "--tag", tag],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)


def output_for(version: str) -> dict[str, object]:
    beta = "-beta." in version
    return {
        "version": version,
        "tag": f"v{version}",
        "channel": "beta" if beta else "stable",
        "required_branch": "dev" if beta else "main",
        "prerelease": beta,
        "image_tags": [
            f"ghcr.io/jigsawfr/dockhand-ha-addon:{version}",
            f"ghcr.io/jigsawfr/dockhand-ha-addon:{'beta' if beta else 'latest'}",
        ],
        "release_notes": release_notes(version),
    }


def write_github_output(values: dict[str, object], path: str) -> None:
    out = Path(path)
    with out.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if isinstance(value, list):
                value = "\n".join(str(item) for item in value)
            elif isinstance(value, bool):
                value = "true" if value else "false"
            else:
                value = str(value)
            if "\n" in value:
                delim = f"DOCKHAND_{key.upper()}_{uuid.uuid4().hex}"
                handle.write(f"{key}<<{delim}\n{value}\n{delim}\n")
            else:
                handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Release tag to dry-run, e.g. v1.0.41.2-beta.4")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument("--github-output", help="Write outputs using GitHub Actions format")
    args = parser.parse_args()

    version = (args.tag[1:] if args.tag and args.tag.startswith("v") else args.tag) or config_version()
    tag = f"v{version}"
    run_check_version(tag, quiet=args.json)
    values = output_for(version)

    if args.github_output:
        write_github_output(values, args.github_output)
    if args.json or not args.github_output:
        print(json.dumps(values, indent=2, sort_keys=True))
    else:
        print(f"release_dry_run=ok version={version} channel={values['channel']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
