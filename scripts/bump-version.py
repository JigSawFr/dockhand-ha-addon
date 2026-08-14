#!/usr/bin/env python3
"""Bump add-on and bundled Dockhand versions consistently."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ADDON_VERSION_RE = re.compile(r"^(?P<base>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))(?:\.(?P<revision>[1-9]\d*))?(?:-beta\.(?P<beta>[1-9]\d*))?$")
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


def addon_base(version: str) -> str:
    match = ADDON_VERSION_RE.fullmatch(version)
    return match.group("base") if match else ""


def is_beta(version: str) -> bool:
    match = ADDON_VERSION_RE.fullmatch(version)
    return bool(match and match.group("beta"))


def ensure_changelog(version: str, dockhand_version: str, wrapper_only: bool) -> None:
    p = path("dockhand/CHANGELOG.md")
    text = p.read_text(encoding="utf-8")
    if re.search(rf"^##\s+{re.escape(version)}\s*$", text, re.M):
        return
    header = f"## {version}\n\n"
    if is_beta(version):
        body = f"- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v{dockhand_version}`.\n- Published from the `dev` channel for testing before a stable release.\n- Does not change the bundled Dockhand application version.\n\n"
    elif wrapper_only:
        body = f"- Home Assistant add-on wrapper revision for Dockhand `fnsys/dockhand:v{dockhand_version}`.\n- Does not change the bundled Dockhand application version.\n\n"
    else:
        body = f"- Bundle Dockhand `fnsys/dockhand:v{dockhand_version}`.\n- Update Home Assistant add-on metadata and release artifacts.\n\n"
    p.write_text(header + body + text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("addon_version", help="Dockhand version, wrapper revision, or beta revision, e.g. 1.0.41, 1.0.41.1, or 1.0.41.2-beta.1")
    parser.add_argument("--dockhand-version", required=True, help="Bundled upstream Dockhand version, e.g. 1.0.41")
    parser.add_argument("--wrapper-only", action="store_true", help="Require addon_version to be X.Y.Z.N for a wrapper-only revision")
    args = parser.parse_args()

    if not ADDON_VERSION_RE.fullmatch(args.addon_version):
        raise SystemExit(f"add-on version must be X.Y.Z, X.Y.Z.N, or X.Y.Z.N-beta.M: {args.addon_version}")
    if not BASE_VERSION_RE.fullmatch(args.dockhand_version):
        raise SystemExit(f"Dockhand version must be X.Y.Z: {args.dockhand_version}")
    if addon_base(args.addon_version) != args.dockhand_version:
        raise SystemExit(
            f"add-on base version {addon_base(args.addon_version)} must match Dockhand version {args.dockhand_version}"
        )
    version_match = ADDON_VERSION_RE.fullmatch(args.addon_version)
    has_revision = bool(version_match and version_match.group("revision"))
    if args.wrapper_only and not has_revision:
        raise SystemExit("wrapper-only releases must use X.Y.Z.N or X.Y.Z.N-beta.M")
    if is_beta(args.addon_version) and not has_revision:
        raise SystemExit("beta releases must use X.Y.Z.N-beta.M")
    if not args.wrapper_only and has_revision:
        raise SystemExit("use --wrapper-only for X.Y.Z.N or X.Y.Z.N-beta.M releases")

    replace(path("dockhand/config.yaml"), CONFIG_VERSION_RE, f'version: "{args.addon_version}"')
    replace(path("dockhand/Dockerfile"), DOCKHAND_FROM_RE, f"FROM fnsys/dockhand:v{args.dockhand_version} AS dockhand")
    ensure_changelog(args.addon_version, args.dockhand_version, args.wrapper_only)

    print(f"addon_version={args.addon_version}")
    print(f"dockhand_version={args.dockhand_version}")
    print("updated=dockhand/config.yaml,dockhand/Dockerfile,dockhand/CHANGELOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
