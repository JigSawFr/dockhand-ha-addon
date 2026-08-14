#!/usr/bin/env python3
"""Regression tests for release automation helper scripts."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseAutomationTests(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(ROOT / "scripts" / args[0]), "--root", str(root), *args[1:]],
            text=True,
            capture_output=True,
            check=False,
        )

    def copy_repo_fixture(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="dockhand-release-automation-"))
        for rel in [
            "dockhand/config.yaml",
            "dockhand/Dockerfile",
            "dockhand/CHANGELOG.md",
            "README.md",
            "docs/channels.md",
            "repository.yaml",
        ]:
            dest = tmp / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        return tmp

    def test_beta_plan_for_new_upstream_dockhand_version(self) -> None:
        root = self.copy_repo_fixture()
        try:
            result = self.run_script(
                root,
                "release-plan.py",
                "--channel",
                "beta",
                "--current-version",
                "1.0.41.2-beta.5",
                "--dockhand-version",
                "1.0.42",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["version"], "1.0.42.1-beta.1")
            self.assertEqual(plan["stable_version"], "1.0.42.1")
            self.assertEqual(plan["reason"], "upstream-dockhand-bump")
        finally:
            shutil.rmtree(root)

    def test_stable_plan_strips_beta_suffix(self) -> None:
        root = self.copy_repo_fixture()
        try:
            result = self.run_script(
                root,
                "release-plan.py",
                "--channel",
                "stable",
                "--current-version",
                "1.0.42.1-beta.3",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["version"], "1.0.42.1")
            self.assertEqual(plan["required_branch"], "main")
            self.assertFalse(plan["prerelease"])
        finally:
            shutil.rmtree(root)

    def test_release_dry_run_json_is_machine_readable(self) -> None:
        config = (ROOT / "dockhand/config.yaml").read_text()
        version = config.split('version: "', 1)[1].split('"', 1)[0]
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "release-dry-run.py"), "--tag", f"v{version}", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], version)

    def test_prepare_stable_removes_beta_metadata_and_stage(self) -> None:
        root = self.copy_repo_fixture()
        try:
            result = self.run_script(
                root,
                "prepare-release-channel.py",
                "--channel",
                "stable",
                "--version",
                "1.0.41.3",
                "--dockhand-version",
                "1.0.41",
                "--summary",
                "Promote tested release automation to stable.",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            config = (root / "dockhand/config.yaml").read_text()
            repo = (root / "repository.yaml").read_text()
            self.assertIn('name: Dockhand by JigSawFr', config)
            self.assertIn('version: "1.0.41.3"', config)
            self.assertNotIn('stage: experimental', config)
            self.assertNotIn('Beta by JigSawFr', config + repo)
            self.assertIn('name: Dockhand by JigSawFr', repo)
            self.assertIn("https://github.com/JigSawFr/dockhand-ha-addon'", repo)
            changelog = (root / "dockhand/CHANGELOG.md").read_text()
            readme = (root / "README.md").read_text()
            self.assertIn("## 1.0.41.3", changelog)
            self.assertIn("Promote tested release automation to stable.", changelog)
            self.assertIn("| Stable | `Dockhand by JigSawFr` | `main` | `1.0.41.3` | `X.Y.Z`, `X.Y.Z.N` | `<version>`, `latest` |", readme)
        finally:
            shutil.rmtree(root)

    def test_prepare_beta_sets_dev_url_stage_and_matrix(self) -> None:
        root = self.copy_repo_fixture()
        try:
            result = self.run_script(
                root,
                "prepare-release-channel.py",
                "--channel",
                "beta",
                "--version",
                "1.0.42.1-beta.1",
                "--dockhand-version",
                "1.0.42",
                "--summary",
                "Beta validation for Dockhand upstream update.",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            config = (root / "dockhand/config.yaml").read_text()
            repo = (root / "repository.yaml").read_text()
            self.assertIn('name: Dockhand Beta by JigSawFr', config)
            self.assertIn('version: "1.0.42.1-beta.1"', config)
            self.assertIn('stage: experimental', config)
            self.assertIn('name: Dockhand Beta by JigSawFr', repo)
            self.assertIn("https://github.com/JigSawFr/dockhand-ha-addon#dev", repo)
            self.assertIn("| Beta | `Dockhand Beta by JigSawFr` | `dev` | `1.0.42.1-beta.1` | `X.Y.Z.N-beta.M` | `<version>`, `beta` |", (root / "README.md").read_text())
            self.assertIn("1.0.42.1-beta.1", (root / "docs/channels.md").read_text())
            self.assertIn("## 1.0.42.1-beta.1", (root / "dockhand/CHANGELOG.md").read_text())
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
