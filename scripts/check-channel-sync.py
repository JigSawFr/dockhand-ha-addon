#!/usr/bin/env python3
"""Verify the beta channel has absorbed everything the stable channel shipped.

The beta channel is promoted to stable, so a beta that is missing a stable fix
does not just lag: promoting it republishes the regression to stable users. This
guard fails while `dev` is behind `main`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(
    r"^(?P<base>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))"
    r"(?:\.(?P<revision>[1-9]\d*))?"
    r"(?:-beta\.(?P<beta>[1-9]\d*))?$"
)
CONFIG_VERSION_RE = re.compile(r'^version:\s+"(?P<version>[^"]+)"\s*$', re.M)
CHANGELOG_HEADER_RE = re.compile(r"^##\s+(?P<version>\S+)\s*$", re.M)


def sort_key(version: str) -> tuple[int, int, int, int]:
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise SystemExit(f"Invalid add-on version: {version}")
    major, minor, patch = (int(part) for part in match.group("base").split("."))
    revision = int(match.group("revision")) if match.group("revision") else 0
    return major, minor, patch, revision


def promotion_target(version: str) -> str:
    """The stable version a beta resolves to when promoted."""
    match = VERSION_RE.fullmatch(version)
    if not match:
        raise SystemExit(f"Invalid add-on version: {version}")
    if match.group("revision"):
        return f"{match.group('base')}.{match.group('revision')}"
    return match.group("base")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def is_ancestor(ref: str, of: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ref, of],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stable-ref",
        default="origin/main",
        help="Git ref holding the stable channel (default: origin/main)",
    )
    parser.add_argument(
        "--beta-ref",
        default="HEAD",
        help="Git ref holding the beta channel (default: HEAD)",
    )
    args = parser.parse_args()

    errors: list[str] = []

    beta_config = (ROOT / "dockhand/config.yaml").read_text(encoding="utf-8")
    beta_match = CONFIG_VERSION_RE.search(beta_config)
    if not beta_match:
        raise SystemExit("Could not parse dockhand/config.yaml version")
    beta = beta_match.group("version")

    # Only the beta channel can be behind stable; on a stable checkout there is
    # nothing to compare and the promotion check would not apply.
    if "-beta." not in beta:
        print("channel_sync=skipped")
        print(f"reason=not a beta checkout ({beta})")
        return 0

    stable_config = git("show", f"{args.stable_ref}:dockhand/config.yaml")
    stable_match = CONFIG_VERSION_RE.search(stable_config)
    if not stable_match:
        raise SystemExit(f"Could not parse version from {args.stable_ref}:dockhand/config.yaml")
    stable_version = stable_match.group("version")

    # 1. Every stable commit must be reachable from the beta branch. This is the
    #    check that catches a stable-only hotfix that was never back-merged.
    if not is_ancestor(args.stable_ref, args.beta_ref):
        missing = git("log", "--oneline", f"{args.beta_ref}..{args.stable_ref}").strip()
        errors.append(
            f"{args.stable_ref} is not an ancestor of {args.beta_ref}; back-merge it before releasing beta:\n"
            + "\n".join(f"    {line}" for line in missing.splitlines())
        )

    # 2. The stable release must appear in the beta changelog, so the beta
    #    genuinely carries its content and not merely its commits.
    changelog = (ROOT / "dockhand/CHANGELOG.md").read_text(encoding="utf-8")
    headers = [m.group("version") for m in CHANGELOG_HEADER_RE.finditer(changelog)]
    if stable_version not in headers:
        errors.append(
            f"dockhand/CHANGELOG.md must contain ## {stable_version}; "
            f"the beta channel has not absorbed the current stable release"
        )

    # 3. Promoting the beta must move stable forward, never sideways or back.
    target = promotion_target(beta)
    if sort_key(target) <= sort_key(stable_version):
        errors.append(
            f"beta {beta!r} promotes to {target!r}, which is not above the released "
            f"stable {stable_version!r}; bump the wrapper revision"
        )

    if errors:
        print("channel_sync=fail")
        for error in errors:
            print(f"- {error}")
        return 1

    print("channel_sync=ok")
    print(f"stable_version={stable_version}")
    print(f"beta_version={beta}")
    print(f"promotion_target={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
