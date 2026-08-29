#!/usr/bin/env python3
"""Prepare repository files for a Dockhand beta or stable release channel."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

VERSION_RE = re.compile(
    r"^(?P<base>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))"
    r"(?:\.(?P<revision>[1-9]\d*))?"
    r"(?:-beta\.(?P<beta>[1-9]\d*))?$"
)
CONFIG_NAME_RE = re.compile(r"^name:\s+.*$", re.M)
CONFIG_VERSION_RE = re.compile(r'^version:\s+"[^"]+"\s*$', re.M)
DOCKHAND_FROM_RE = re.compile(r"^FROM\s+fnsys/dockhand:v[^\s]+\s+AS\s+dockhand\s*$", re.M)
CHANGELOG_HEADER_RE = re.compile(r"^##\s+(?P<version>\S+)\s*$", re.M)

STABLE_NAME = "Dockhand by JigSawFr"
BETA_NAME = "Dockhand Beta by JigSawFr"
STABLE_URL = "https://github.com/JigSawFr/dockhand-ha-addon"
BETA_URL = "https://github.com/JigSawFr/dockhand-ha-addon#dev"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def parse_version(version: str) -> re.Match[str]:
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise SystemExit(f"Invalid add-on version: {version}")
    if match.group("beta") and not match.group("revision"):
        raise SystemExit("Beta versions must use X.Y.Z.N-beta.M")
    return match


def addon_base(version: str) -> str:
    return parse_version(version).group("base")


def update_config(root: Path, channel: str, version: str) -> None:
    path = root / "dockhand/config.yaml"
    text = read(path)
    name = BETA_NAME if channel == "beta" else STABLE_NAME
    text, count_name = CONFIG_NAME_RE.subn(f"name: {name}", text, count=1)
    text, count_version = CONFIG_VERSION_RE.subn(f'version: "{version}"', text, count=1)
    if count_name != 1 or count_version != 1:
        raise SystemExit("Could not update dockhand/config.yaml name/version")

    text = re.sub(r"^stage:\s+experimental\s*\n", "", text, flags=re.M)
    if channel == "beta":
        if not text.endswith("\n"):
            text += "\n"
        text += "stage: experimental\n"
    write(path, text)


def update_repository(root: Path, channel: str) -> None:
    name = BETA_NAME if channel == "beta" else STABLE_NAME
    url = BETA_URL if channel == "beta" else STABLE_URL
    write(root / "repository.yaml", f"name: {name}\nurl: '{url}'\nmaintainer: JigSawFr\n")


def update_dockerfile(root: Path, dockhand_version: str) -> None:
    path = root / "dockhand/Dockerfile"
    text = read(path)
    text, count = DOCKHAND_FROM_RE.subn(f"FROM fnsys/dockhand:v{dockhand_version} AS dockhand", text, count=1)
    if count != 1:
        raise SystemExit("Could not update dockhand/Dockerfile Dockhand image")
    write(path, text)


def replace_table_version(text: str, row_label: str, version: str) -> str:
    lines = text.splitlines(keepends=True)
    current_idx: int | None = None

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if "Current version" in cells:
            current_idx = cells.index("Current version")
            continue

        if current_idx is None or not cells or cells[0] != row_label:
            continue
        if current_idx >= len(cells):
            raise SystemExit(f"Malformed {row_label} version table row")

        cells[current_idx] = f"`{version}`"
        newline = "\n" if line.endswith("\n") else ""
        lines[idx] = "| " + " | ".join(cells) + " |" + newline
        return "".join(lines)

    raise SystemExit(f"Could not update {row_label} version table row")


def update_docs(root: Path, channel: str, version: str) -> None:
    row = "Beta" if channel == "beta" else "Stable"
    for rel in ["README.md", "docs/channels.md"]:
        path = root / rel
        text = read(path)
        write(path, replace_table_version(text, row, version))


def changelog_body(channel: str, version: str, dockhand_version: str, summary: str | None) -> str:
    if summary:
        custom = f"- {summary.rstrip('.')}.\n"
    else:
        custom = ""

    if channel == "beta":
        return (
            custom
            + f"- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v{dockhand_version}`.\n"
            + "- Published from the `dev` channel for testing before a stable release.\n"
            + "- Prepared by the release automation workflow.\n\n"
        )
    return (
        custom
        + f"- Stable Home Assistant add-on wrapper revision for Dockhand `fnsys/dockhand:v{dockhand_version}`.\n"
        + "- Promoted from the tested beta channel.\n"
        + "- Prepared by the release automation workflow.\n\n"
    )


def ensure_changelog(root: Path, channel: str, version: str, dockhand_version: str, summary: str | None) -> None:
    path = root / "dockhand/CHANGELOG.md"
    text = read(path)
    if re.search(rf"^##\s+{re.escape(version)}\s*$", text, re.M):
        return
    body = changelog_body(channel, version, dockhand_version, summary)
    write(path, f"## {version}\n\n{body}" + text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--channel", choices=["beta", "stable"], required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--dockhand-version")
    parser.add_argument("--summary")
    args = parser.parse_args()

    match = parse_version(args.version)
    if args.channel == "beta" and not match.group("beta"):
        raise SystemExit("Beta channel requires a -beta.M version")
    if args.channel == "stable" and match.group("beta"):
        raise SystemExit("Stable channel cannot use a beta version")

    dockhand_version = args.dockhand_version or addon_base(args.version)
    if dockhand_version != addon_base(args.version):
        raise SystemExit("Dockhand version must match the add-on base version")

    update_config(args.root, args.channel, args.version)
    update_repository(args.root, args.channel)
    update_dockerfile(args.root, dockhand_version)
    update_docs(args.root, args.channel, args.version)
    ensure_changelog(args.root, args.channel, args.version, dockhand_version, args.summary)

    print("prepare_release_channel=ok")
    print(f"channel={args.channel}")
    print(f"version={args.version}")
    print(f"dockhand_version={dockhand_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
