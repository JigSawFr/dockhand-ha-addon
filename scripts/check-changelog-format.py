#!/usr/bin/env python3
"""Guard the changelog against the ways a merge can quietly damage it.

`backmerge-resolve.py` merges `dockhand/CHANGELOG.md` with `git merge-file
--union`, which keeps both sides of a conflict by concatenating them. That is
the right answer for a file both channels prepend to, but it has two failure
modes at the seam:

- the blank line between entries is lost, so an entry renders as part of the one
  above it. `restore_entry_spacing()` handles this, but only on the automated
  path: a human resolving the same conflict by hand is still exposed;
- an entry present on both sides is kept twice.

Home Assistant shows this file to users on the add-on page, so neither is
cosmetic. This runs in CI and in preflight, on whatever produced the file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def check(text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    seen: dict[str, int] = {}

    for index, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()

        if index > 0 and lines[index - 1].strip():
            errors.append(
                f"line {index + 1}: '{line}' has no blank line before it, so it renders "
                f"as part of the entry above; a union merge drops the separator at its seam"
            )

        if heading in seen:
            errors.append(
                f"line {index + 1}: '{line}' repeats the entry from line {seen[heading]}; "
                f"a union merge keeps an entry present on both sides twice"
            )
        else:
            seen[heading] = index + 1

    if not seen:
        errors.append("no '## <version>' entries found; is this the right file?")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", type=Path)
    parser.add_argument("--path", default="dockhand/CHANGELOG.md")
    args = parser.parse_args()

    changelog = args.root / args.path
    if not changelog.is_file():
        print(f"changelog_format=fail\n- {changelog} does not exist", file=sys.stderr)
        return 1

    errors = check(changelog.read_text(encoding="utf-8"))
    if errors:
        print("changelog_format=fail", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("changelog_format=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
