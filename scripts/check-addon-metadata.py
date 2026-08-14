#!/usr/bin/env python3
"""Validate key Home Assistant add-on metadata invariants without external deps."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "dockhand/config.yaml"
REPOSITORY = ROOT / "repository.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(?:\"([^\"]*)\"|'([^']*)'|([^#\n]+))\s*$", text, re.M)
    if not match:
        return None
    for index in (1, 2, 3):
        if match.group(index) is not None:
            return match.group(index).strip()
    return None


def bool_scalar(text: str, key: str) -> bool | None:
    value = scalar(text, key)
    if value == "true":
        return True
    if value == "false":
        return False
    return None


def block_items(text: str, key: str) -> list[str]:
    match = re.search(rf"^{re.escape(key)}:\s*$\n(?P<body>(?:^[ \t]+-.+$\n?)+)", text, re.M)
    if not match:
        return []
    return [line.strip()[2:].strip() for line in match.group("body").splitlines() if line.strip().startswith("- ")]


def has_data_map(text: str) -> bool:
    return bool(re.search(r"^map:\s*$\n(?:^[ \t]+.*\n)*?^[ \t]+-\s+type:\s+data\s*$\n^[ \t]+read_only:\s+false\s*$", text, re.M))


def has_mapping_key(text: str, block: str, key: str) -> bool:
    match = re.search(rf"^{re.escape(block)}:\s*$\n(?P<body>(?:^[ \t]+[^\n]+\n?)+)", text, re.M)
    return bool(match and re.search(rf"^[ \t]+{re.escape(key)}:\s+", match.group("body"), re.M))


def has_null_mapping(text: str, block: str, key: str) -> bool:
    match = re.search(rf"^{re.escape(block)}:\s*$\n(?P<body>(?:^[ \t]+[^\n]+\n?)+)", text, re.M)
    return bool(match and re.search(rf"^[ \t]+{re.escape(key)}:\s+null\s*$", match.group("body"), re.M))


def main() -> int:
    errors: list[str] = []
    cfg = read(CONFIG)
    repo = read(REPOSITORY)

    expected_scalars = {
        "name": "Dockhand by JigSawFr",
        "slug": "dockhand",
        "image": "ghcr.io/jigsawfr/dockhand-ha-addon",
    }
    for key, expected in expected_scalars.items():
        actual = scalar(cfg, key)
        if actual != expected:
            errors.append(f"config {key!r} must be {expected!r}, got {actual!r}")

    expected_bools = {
        "ingress": True,
        "docker_api": True,
        "apparmor": False,
        "init": False,
    }
    for key, expected in expected_bools.items():
        actual = bool_scalar(cfg, key)
        if actual is not expected:
            errors.append(f"config {key!r} must be {expected!r}, got {actual!r}")

    if scalar(cfg, "stage") is not None:
        errors.append("stable config must not define stage; it must not be marked experimental")

    arch = block_items(cfg, "arch")
    if arch != ["aarch64", "amd64"]:
        errors.append(f"arch must be ['aarch64', 'amd64'], got {arch!r}")

    if not has_data_map(cfg):
        errors.append("config map must include writable data mapping")

    if not has_null_mapping(cfg, "ports", "3000/tcp"):
        errors.append("ports must include disabled optional 3000/tcp mapping")
    if not has_mapping_key(cfg, "ports_description", "3000/tcp"):
        errors.append("ports_description must describe optional 3000/tcp risk")

    for key in ["log_level", "auto_backup_on_start", "backup_retention"]:
        if not has_mapping_key(cfg, "options", key):
            errors.append(f"options must include {key}")
        if not has_mapping_key(cfg, "schema", key):
            errors.append(f"schema must include {key}")

    devices = block_items(cfg, "devices")
    if "/var/run/docker.sock" not in devices:
        errors.append("config devices must include /var/run/docker.sock")

    repo_name = scalar(repo, "name")
    if repo_name != "Dockhand by JigSawFr":
        errors.append("repository.yaml name must be 'Dockhand by JigSawFr' on stable")

    repo_url = scalar(repo, "url")
    if repo_url != "https://github.com/JigSawFr/dockhand-ha-addon":
        errors.append("repository.yaml url must point to JigSawFr/dockhand-ha-addon")

    if errors:
        print("addon_metadata=fail")
        for error in errors:
            print(f"- {error}")
        return 1

    print("addon_metadata=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
