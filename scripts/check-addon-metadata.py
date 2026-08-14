#!/usr/bin/env python3
"""Validate key Home Assistant add-on metadata invariants without external deps."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "dockhand/config.yaml"
REPOSITORY = ROOT / "repository.yaml"
DOCKERFILE = ROOT / "dockhand/Dockerfile"
APPARMOR = ROOT / "dockhand/apparmor.txt"


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


def is_beta_version(version: str | None) -> bool:
    return bool(version and "-beta." in version)


def main() -> int:
    errors: list[str] = []
    cfg = read(CONFIG)
    repo = read(REPOSITORY)

    expected_scalars = {
        "name": "Dockhand",
        "slug": "dockhand",
        "image": "ghcr.io/jigsawfr/dockhand-ha-addon",
    }
    for key, expected in expected_scalars.items():
        actual = scalar(cfg, key)
        if actual != expected:
            errors.append(f"config {key!r} must be {expected!r}, got {actual!r}")

    expected_bools = {
        "ingress": True,
        "ingress_stream": True,
        "docker_api": True,
        "init": False,
    }
    for key, expected in expected_bools.items():
        actual = bool_scalar(cfg, key)
        if actual is not expected:
            errors.append(f"config {key!r} must be {expected!r}, got {actual!r}")

    for key in ["panel_admin", "apparmor", "watchdog"]:
        if scalar(cfg, key) is not None:
            errors.append(f"config {key!r} should be omitted to stay linter-compatible")

    arch = block_items(cfg, "arch")
    if arch != ["aarch64", "amd64"]:
        errors.append(f"arch must be ['aarch64', 'amd64'], got {arch!r}")

    if not has_data_map(cfg):
        errors.append("config map must include writable data mapping")

    if not has_null_mapping(cfg, "ports", "3000/tcp"):
        errors.append("ports must include disabled optional 3000/tcp mapping")
    if not has_mapping_key(cfg, "ports_description", "3000/tcp"):
        errors.append("ports_description must describe optional 3000/tcp risk")

    dockerfile = read(DOCKERFILE)
    apparmor = read(APPARMOR)
    if "HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3" not in dockerfile:
        errors.append("Dockerfile must define the native Docker HEALTHCHECK")
    if "CMD /usr/bin/dockhand-healthcheck || exit 1" not in dockerfile:
        errors.append("Dockerfile HEALTHCHECK must call dockhand-healthcheck")
    for entry in ["profile dockhand", "network inet stream,", "network unix stream,", "/var/run/docker.sock rw,", "/data/** rw,"]:
        if entry not in apparmor:
            errors.append(f"AppArmor profile must contain {entry!r}")

    if scalar(cfg, "backup_pre") is None or "wal_checkpoint(TRUNCATE)" not in cfg:
        errors.append("backup_pre must checkpoint the Dockhand SQLite WAL before HA backups")
    backup_exclude = block_items(cfg, "backup_exclude")
    if "\"backups/*.sqlite\"" not in backup_exclude and "backups/*.sqlite" not in backup_exclude:
        errors.append("backup_exclude must exclude lightweight startup SQLite backups")

    for key in ["log_level", "auto_backup_on_start", "backup_retention"]:
        if not has_mapping_key(cfg, "options", key):
            errors.append(f"options must include {key}")
        if not has_mapping_key(cfg, "schema", key):
            errors.append(f"schema must include {key}")

    devices = block_items(cfg, "devices")
    if "/var/run/docker.sock" not in devices:
        errors.append("config devices must include /var/run/docker.sock")

    repo_name = scalar(repo, "name")
    repo_url = scalar(repo, "url")
    config_version = scalar(cfg, "version")
    beta = is_beta_version(config_version)
    expected_repo_name = "Dockerhand Beta by JigSawFr" if beta else "Dockerhand by JigSawFr"
    expected_repo_url = "https://github.com/JigSawFr/dockhand-ha-addon#dev" if beta else "https://github.com/JigSawFr/dockhand-ha-addon"
    if repo_name != expected_repo_name:
        errors.append(f"repository.yaml name must be {expected_repo_name!r} for this release channel")
    if repo_url != expected_repo_url:
        errors.append(f"repository.yaml url must be {expected_repo_url!r} for this release channel")

    if errors:
        print("addon_metadata=fail")
        for error in errors:
            print(f"- {error}")
        return 1

    print("addon_metadata=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
