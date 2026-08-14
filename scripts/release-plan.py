#!/usr/bin/env python3
"""Compute safe Dockhand add-on release versions for beta/stable automation."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

VERSION_RE = re.compile(
    r"^(?P<base>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))"
    r"(?:\.(?P<revision>[1-9]\d*))?"
    r"(?:-beta\.(?P<beta>[1-9]\d*))?$"
)
CONFIG_VERSION_RE = re.compile(r'^version:\s+"(?P<version>[^"]+)"\s*$', re.M)
DOCKHAND_FROM_RE = re.compile(r"^FROM\s+fnsys/dockhand:v(?P<version>[^\s]+)\s+AS\s+dockhand\s*$", re.M)


@dataclass(frozen=True)
class AddonVersion:
    raw: str
    base: str
    revision: int | None
    beta: int | None

    @property
    def stable(self) -> str:
        return f"{self.base}.{self.revision}" if self.revision is not None else self.base

    @property
    def is_beta(self) -> bool:
        return self.beta is not None


def parse_version(value: str) -> AddonVersion:
    match = VERSION_RE.fullmatch(value)
    if not match:
        raise SystemExit(f"Invalid add-on version: {value}")
    revision = int(match.group("revision")) if match.group("revision") else None
    beta = int(match.group("beta")) if match.group("beta") else None
    if beta is not None and revision is None:
        raise SystemExit("Beta versions must use X.Y.Z.N-beta.M")
    return AddonVersion(value, match.group("base"), revision, beta)


def read_config_version(root: Path) -> str:
    text = (root / "dockhand/config.yaml").read_text(encoding="utf-8")
    match = CONFIG_VERSION_RE.search(text)
    if not match:
        raise SystemExit("Could not parse dockhand/config.yaml version")
    return match.group("version")


def read_dockhand_version(root: Path) -> str:
    text = (root / "dockhand/Dockerfile").read_text(encoding="utf-8")
    match = DOCKHAND_FROM_RE.search(text)
    if not match:
        raise SystemExit("Could not parse Dockhand image version from dockhand/Dockerfile")
    return match.group("version")


def next_beta(current: AddonVersion, dockhand_version: str) -> tuple[str, str, str]:
    if dockhand_version != current.base:
        stable_version = f"{dockhand_version}.1"
        return f"{stable_version}-beta.1", stable_version, "upstream-dockhand-bump"

    if current.is_beta:
        stable_version = current.stable
        beta_iteration = (current.beta or 0) + 1
        return f"{stable_version}-beta.{beta_iteration}", stable_version, "beta-iteration"

    next_revision = (current.revision or 0) + 1
    stable_version = f"{current.base}.{next_revision}"
    return f"{stable_version}-beta.1", stable_version, "wrapper-beta"


def stable_from(current: AddonVersion) -> tuple[str, str]:
    if current.is_beta:
        return current.stable, "promote-beta"
    return current.raw, "stable-current"


def plan(root: Path, channel: str, current_version: str | None, dockhand_version: str | None) -> dict[str, object]:
    current = parse_version(current_version or read_config_version(root))
    bundled_dockhand = dockhand_version or read_dockhand_version(root)

    if channel == "beta":
        version, stable_version, reason = next_beta(current, bundled_dockhand)
        prerelease = True
        required_branch = "dev"
    elif channel == "stable":
        version, reason = stable_from(current)
        stable_version = version
        prerelease = False
        required_branch = "main"
    else:
        raise SystemExit(f"Unsupported channel: {channel}")

    return {
        "version": version,
        "stable_version": stable_version,
        "dockhand_version": bundled_dockhand,
        "tag": f"v{version}",
        "channel": channel,
        "required_branch": required_branch,
        "prerelease": prerelease,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--channel", choices=["beta", "stable"], required=True)
    parser.add_argument("--current-version")
    parser.add_argument("--dockhand-version")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--github-output")
    args = parser.parse_args()

    values = plan(args.root, args.channel, args.current_version, args.dockhand_version)

    if args.github_output:
        out = Path(args.github_output)
        with out.open("a", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write(f"{key}={str(value).lower() if isinstance(value, bool) else value}\n")

    if args.json or not args.github_output:
        print(json.dumps(values, indent=2, sort_keys=True))
    else:
        print(f"release_plan=ok version={values['version']} channel={values['channel']} reason={values['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
