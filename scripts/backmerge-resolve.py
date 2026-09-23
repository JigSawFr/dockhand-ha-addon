#!/usr/bin/env python3
"""Merge the stable branch into the current beta checkout, resolving the files
that the two channels are *supposed* to disagree about.

`main` and `dev` carry deliberately different channel identity: the add-on name,
the version, `stage: experimental`, the `#dev` repository URL, and the channel
matrix rows in the README and channel docs. Every stable promotion rewrites
exactly those lines on `main`, so a plain `git merge main` into `dev` conflicts
on them every single time — which is why the back-merge never proposed itself.

Divergence that is expected is not a conflict to escalate; it is a conflict with
a known answer:

- channel-owned files take the stable side for anything genuinely new, then
  `prepare-release-channel.py` re-stamps the beta identity on top;
- the changelog takes both sides, so the beta keeps its entries and gains the
  stable release entry that `check-channel-sync.py` looks for;
- anything else is a real conflict, and the merge is aborted for a human.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CONFIG_VERSION_RE = re.compile(r'^version:\s+"(?P<version>[^"]+)"\s*$', re.M)
DOCKHAND_FROM_RE = re.compile(r"^FROM\s+fnsys/dockhand:v(?P<version>[^\s]+)\s+AS\s+dockhand\s*$", re.M)

# Rewritten by prepare-release-channel.py on every channel switch, so both
# branches always touch the same lines. Resolved in favour of stable, then
# re-stamped back to beta identity.
CHANNEL_OWNED = (
    "dockhand/config.yaml",
    "repository.yaml",
    "README.md",
    "docs/channels.md",
)

# Both channels prepend their own release entry at the top of the file. Neither
# side is wrong: the beta keeps its entries and inherits the stable ones.
UNION_MERGED = ("dockhand/CHANGELOG.md",)


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=check
    )


def merge_in_progress(root: Path) -> bool:
    return git(root, "rev-parse", "--verify", "-q", "MERGE_HEAD", check=False).returncode == 0


def conflicted_paths(root: Path) -> list[str]:
    out = git(root, "diff", "--name-only", "--diff-filter=U").stdout
    return [line for line in out.splitlines() if line]


def resolve_stage(root: Path, path: str, strategy: str) -> None:
    """Three-way merge one conflicted file, favouring `strategy` in the hunks
    that actually conflict. Non-conflicting changes from both sides survive —
    unlike `git checkout --ours/--theirs`, which discards a whole side."""
    with tempfile.TemporaryDirectory() as tmp:
        stages = {}
        for stage, name in ((1, "base"), (2, "ours"), (3, "theirs")):
            blob = Path(tmp) / name
            result = git(root, "show", f":{stage}:{path}", check=False)
            if result.returncode != 0:
                raise SystemExit(
                    f"{path} is conflicted but has no stage {stage}; resolve this merge by hand"
                )
            blob.write_text(result.stdout, encoding="utf-8")
            stages[name] = blob
        # merge-file writes the result into the first file it is given.
        git(
            root,
            "merge-file",
            f"--{strategy}",
            str(stages["ours"]),
            str(stages["base"]),
            str(stages["theirs"]),
            check=False,
        )
        merged = stages["ours"].read_text(encoding="utf-8")
    if strategy == "union":
        merged = restore_entry_spacing(merged)
    (root / path).write_text(merged, encoding="utf-8")
    git(root, "add", "--", path)


def restore_entry_spacing(text: str) -> str:
    """A union merge butts the two sides together at the seam, so the changelog
    loses the blank line it keeps between entries. Only the seam can be affected;
    every other heading already has its separator."""
    return re.sub(r"(?<!\n\n)(?<=\n)(?=## )", "\n", text)


def plan_beta(root: Path, current_version: str, dockhand_version: str, stable_ref: str) -> str:
    """The back-merge changes what the beta channel ships, and it lands after a
    stable release the beta has not caught up with. `release-plan.py` owns both
    rules, including the stable-catch-up that keeps the promotion target above
    the released stable version."""
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "release-plan.py"),
            "--root",
            str(root),
            "--channel",
            "beta",
            "--current-version",
            current_version,
            "--dockhand-version",
            dockhand_version,
            "--stable-ref",
            stable_ref,
            "--json",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    return str(json.loads(result.stdout)["version"])


def restamp_beta(root: Path, version: str, dockhand_version: str, summary: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "prepare-release-channel.py"),
            "--root",
            str(root),
            "--channel",
            "beta",
            "--version",
            version,
            "--dockhand-version",
            dockhand_version,
            "--summary",
            summary,
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--stable-ref", default="origin/main")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Finish a merge that is already in progress instead of starting one. "
        "Lets a human stage the answer to a conflict this script has no rule for "
        "and still get the channel identity and version handled the same way.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()

    config = (root / "dockhand/config.yaml").read_text(encoding="utf-8")
    version_match = CONFIG_VERSION_RE.search(config)
    if not version_match:
        raise SystemExit("Could not parse dockhand/config.yaml version")
    beta_version = version_match.group("version")
    if "-beta." not in beta_version:
        raise SystemExit(
            f"Refusing to back-merge into a non-beta checkout (version {beta_version})"
        )

    dockerfile = (root / "dockhand/Dockerfile").read_text(encoding="utf-8")
    dockhand_match = DOCKHAND_FROM_RE.search(dockerfile)
    if not dockhand_match:
        raise SystemExit("Could not parse Dockhand image version from dockhand/Dockerfile")
    dockhand_version = dockhand_match.group("version")

    conflicts: list[str] = []
    if args.resume:
        if not merge_in_progress(root):
            raise SystemExit("--resume needs a merge in progress")
        merge_failed = True
        merge_output = ""
    else:
        merge = git(root, "merge", "--no-ff", "--no-edit", args.stable_ref, check=False)
        merge_failed = merge.returncode != 0
        merge_output = merge.stdout + merge.stderr

    if merge_failed:
        conflicts = conflicted_paths(root)
        if not conflicts and not args.resume:
            print(merge_output, file=sys.stderr)
            raise SystemExit(f"git merge {args.stable_ref} failed without reporting conflicts")

        unexpected = [p for p in conflicts if p not in CHANNEL_OWNED and p not in UNION_MERGED]
        if unexpected:
            # Leave a resumed merge alone: the caller staged work in it.
            if not args.resume:
                git(root, "merge", "--abort", check=False)
            print("resolution=conflicted")
            for path in unexpected:
                print(f"conflict={path}")
            return 1

        for path in conflicts:
            resolve_stage(root, path, "union" if path in UNION_MERGED else "theirs")

    # Whether or not it conflicted, the merge changed what the beta channel
    # ships, and the stable side may have overwritten the channel identity. Put
    # the beta identity back, on the version the planner says it should carry.
    merged_dockhand = DOCKHAND_FROM_RE.search(
        (root / "dockhand/Dockerfile").read_text(encoding="utf-8")
    )
    if merged_dockhand:
        dockhand_version = merged_dockhand.group("version")
    planned = plan_beta(root, beta_version, dockhand_version, args.stable_ref)
    restamp_beta(
        root,
        planned,
        dockhand_version,
        "Back-merge the stable channel into beta so the next promotion cannot move stable backwards.",
    )
    git(root, "add", "--all")
    if merge_in_progress(root):
        git(root, "commit", "--no-edit")
    else:
        # A clean merge already committed; fold the re-stamp into it. `--amend`
        # keeps both parents, so the ancestry the back-merge exists for survives.
        git(root, "commit", "--amend", "--no-edit")
    print("resolution=" + ("resolved" if merge_failed else "clean"))
    print(f"version={planned}")
    for path in conflicts:
        print(f"resolved={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
