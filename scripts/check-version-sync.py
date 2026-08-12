#!/usr/bin/env python3
"""Validate version consistency for the Dockhand add-on."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
FOUR_PART_VERSION_RE = re.compile(r"\bv?\d+\.\d+\.\d+\.\d+\b")
IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
DOCKHAND_FROM_RE = re.compile(r"^FROM\s+fnsys/dockhand:v(?P<version>[^\s]+)\s+AS\s+dockhand\s*$", re.M)
BASE_FROM_RE = re.compile(r"^FROM\s+(?P<image>ghcr\.io/home-assistant/base-debian:[^\s]+)\s*$", re.M)
CONFIG_VERSION_RE = re.compile(r'^version:\s+"(?P<version>[^"]+)"\s*$', re.M)
CONFIG_IMAGE_RE = re.compile(r'^image:\s+"(?P<image>[^"]+)"\s*$', re.M)
CHANGELOG_HEADER_RE = re.compile(r"^##\s+(?P<version>\S+)\s*$", re.M)
EXPECTED_IMAGE = "ghcr.io/jigsawfr/dockhand-ha-addon"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def parse_version_from_config(errors: list[str]) -> str:
    cfg = read("dockhand/config.yaml")
    match = CONFIG_VERSION_RE.search(cfg)
    require(match is not None, "dockhand/config.yaml must contain version: \"X.Y.Z\"", errors)
    return match.group("version") if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Optional release tag to validate, e.g. v1.0.29")
    args = parser.parse_args()

    errors: list[str] = []
    config = read("dockhand/config.yaml")
    dockerfile = read("dockhand/Dockerfile")
    changelog = read("dockhand/CHANGELOG.md")
    readme = read("README.md")

    addon_version = parse_version_from_config(errors)
    require(bool(SEMVER_RE.fullmatch(addon_version)), f"add-on version must be strict SemVer: {addon_version!r}", errors)

    image_match = CONFIG_IMAGE_RE.search(config)
    require(image_match is not None, "dockhand/config.yaml must contain image", errors)
    if image_match:
        require(image_match.group("image") == EXPECTED_IMAGE, f"config image must be {EXPECTED_IMAGE}", errors)

    dockhand_match = DOCKHAND_FROM_RE.search(dockerfile)
    require(dockhand_match is not None, "Dockerfile must use FROM fnsys/dockhand:vX.Y.Z AS dockhand", errors)
    dockhand_version = dockhand_match.group("version") if dockhand_match else ""
    require(bool(SEMVER_RE.fullmatch(dockhand_version)), f"Dockhand image version must be strict SemVer: {dockhand_version!r}", errors)

    base_match = BASE_FROM_RE.search(dockerfile)
    require(base_match is not None, "Dockerfile must use Home Assistant base Debian image", errors)

    headers = [m.group("version") for m in CHANGELOG_HEADER_RE.finditer(changelog)]
    require(addon_version in headers, f"dockhand/CHANGELOG.md must contain ## {addon_version}", errors)

    require(f"version: \"{addon_version}\"" in config, "config version literal missing", errors)
    require(f"fnsys/dockhand:v{dockhand_version}" in dockerfile, "Dockerfile Dockhand image literal missing", errors)
    require(
        f"fnsys/dockhand:v{dockhand_version}" in changelog,
        f"dockhand/CHANGELOG.md must mention bundled Dockhand v{dockhand_version}",
        errors,
    )
    tracked_text = "\n".join(
        read(file)
        for file in [
            "dockhand/config.yaml",
            "dockhand/Dockerfile",
            "dockhand/CHANGELOG.md",
            "README.md",
            "RELEASE.md",
            "docs/release.md",
            "CONTRIBUTING.md",
        ]
    )
    four_part_versions = sorted(
        {
            value
            for value in FOUR_PART_VERSION_RE.findall(tracked_text)
            if not IPV4_RE.fullmatch(value) or any(int(part) > 255 for part in value.split("."))
        }
    )
    require(not four_part_versions, f"four-part version literals are not allowed: {four_part_versions}", errors)

    if args.tag:
        tag = args.tag[1:] if args.tag.startswith("v") else args.tag
        require(tag == addon_version, f"tag {args.tag!r} must match add-on version {addon_version!r}", errors)

    if errors:
        print("version_sync=fail")
        for error in errors:
            print(f"- {error}")
        return 1

    print("version_sync=ok")
    print(f"addon_version={addon_version}")
    print(f"dockhand_version={dockhand_version}")
    print(f"image={EXPECTED_IMAGE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
