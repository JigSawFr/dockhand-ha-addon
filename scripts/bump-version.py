#!/usr/bin/env python3
"""Bump add-on and bundled Dockhand versions consistently."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
CONFIG_VERSION_RE = re.compile(r'^version:\s+"[^"]+"\s*$', re.M)
DOCKHAND_FROM_RE = re.compile(r"^FROM\s+fnsys/dockhand:v[^\s]+\s+AS\s+dockhand\s*$", re.M)
CHANGELOG_HEADER_RE = re.compile(r"^##\s+")


def path(name: str) -> Path:
    return ROOT / name


def replace(path_: Path, pattern: re.Pattern[str], repl: str) -> None:
    text = path_.read_text(encoding="utf-8")
    new, count = pattern.subn(repl, text, count=1)
    if count != 1:
        raise SystemExit(f"Could not update {path_.relative_to(ROOT)}")
    path_.write_text(new, encoding="utf-8")


def ensure_changelog(version: str, dockhand_version: str, wrapper_only: bool) -> None:
    p = path("dockhand/CHANGELOG.md")
    text = p.read_text(encoding="utf-8")
    if re.search(rf"^##\s+{re.escape(version)}\s*$", text, re.M):
        return
    header = f"## {version}\n\n"
    if wrapper_only:
        body = f"- Wrapper-only maintenance release.\n- Bundles Dockhand `fnsys/dockhand:v{dockhand_version}`.\n\n"
    else:
        body = f"- Bundle Dockhand `fnsys/dockhand:v{dockhand_version}`.\n- Update Home Assistant add-on metadata and release artifacts.\n\n"
    p.write_text(header + body + text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("addon_version")
    parser.add_argument("--dockhand-version", required=True)
    parser.add_argument("--wrapper-only", action="store_true")
    args = parser.parse_args()

    for label, value in {"addon version": args.addon_version, "Dockhand version": args.dockhand_version}.items():
        if not SEMVER_RE.fullmatch(value):
            raise SystemExit(f"{label} must be strict SemVer: {value}")

    replace(path("dockhand/config.yaml"), CONFIG_VERSION_RE, f'version: "{args.addon_version}"')
    replace(path("dockhand/Dockerfile"), DOCKHAND_FROM_RE, f"FROM fnsys/dockhand:v{args.dockhand_version} AS dockhand")
    ensure_changelog(args.addon_version, args.dockhand_version, args.wrapper_only)

    print(f"addon_version={args.addon_version}")
    print(f"dockhand_version={args.dockhand_version}")
    print("updated=dockhand/config.yaml,dockhand/Dockerfile,dockhand/CHANGELOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
