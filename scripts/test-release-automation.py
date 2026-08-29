#!/usr/bin/env python3
"""Regression tests for release automation helper scripts."""
from __future__ import annotations

import json
import re
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

    def assert_unreleased(self, root: Path, version: str) -> None:
        """prepare-release-channel.py is idempotent, so a released version writes no entry."""
        changelog = (root / "dockhand/CHANGELOG.md").read_text()
        self.assertNotIn(
            f"## {version}\n",
            changelog,
            f"fixture already ships {version}; point this test at an unreleased version",
        )

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

    def test_beta_plan_catches_up_when_stable_moved_ahead(self) -> None:
        """A hotfix released straight to stable must not leave the beta planning a
        promotion that moves stable backwards."""
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
                "1.0.41",
                "--released-stable",
                "1.0.41.4",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["version"], "1.0.41.5-beta.1")
            self.assertEqual(plan["stable_version"], "1.0.41.5")
            self.assertEqual(plan["reason"], "stable-catch-up")
        finally:
            shutil.rmtree(root)

    def test_beta_plan_leaves_upstream_bump_alone(self) -> None:
        """A new upstream base already sorts above stable, so it needs no catch-up."""
        root = self.copy_repo_fixture()
        try:
            result = self.run_script(
                root,
                "release-plan.py",
                "--channel",
                "beta",
                "--current-version",
                "1.0.41.5-beta.1",
                "--dockhand-version",
                "1.0.43",
                "--released-stable",
                "1.0.41.4",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["version"], "1.0.43.1-beta.1")
            self.assertEqual(plan["reason"], "upstream-dockhand-bump")
        finally:
            shutil.rmtree(root)

    def test_beta_plan_still_iterates_above_stable(self) -> None:
        root = self.copy_repo_fixture()
        try:
            result = self.run_script(
                root,
                "release-plan.py",
                "--channel",
                "beta",
                "--current-version",
                "1.0.41.5-beta.1",
                "--dockhand-version",
                "1.0.41",
                "--released-stable",
                "1.0.41.4",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["version"], "1.0.41.5-beta.2")
            self.assertEqual(plan["reason"], "beta-iteration")
        finally:
            shutil.rmtree(root)

    def test_beta_plan_reads_released_stable_from_a_git_ref(self) -> None:
        """--stable-ref is what the normalize workflow uses, so it must resolve a real
        ref rather than relying on shell plumbing to pass the value in."""
        root = self.copy_repo_fixture()
        try:
            # The ref stands in for main, so it must carry a stable version.
            config = root / "dockhand/config.yaml"
            config.write_text(
                re.sub(
                    r'^version: "[^"]+"$', 'version: "1.0.41.4"', config.read_text(), count=1, flags=re.M
                )
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "stable"],
                cwd=root,
                check=True,
            )
            subprocess.run(["git", "tag", "stable-ref"], cwd=root, check=True)

            result = self.run_script(
                root,
                "release-plan.py",
                "--channel",
                "beta",
                "--current-version",
                "1.0.41.2-beta.5",
                "--dockhand-version",
                "1.0.41",
                "--stable-ref",
                "stable-ref",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            plan = json.loads(result.stdout)
            # Same outcome as passing --released-stable 1.0.41.4 by hand.
            self.assertEqual(plan["version"], "1.0.41.5-beta.1")
            self.assertEqual(plan["reason"], "stable-catch-up")
        finally:
            shutil.rmtree(root)

    def test_beta_plan_reports_an_unreadable_stable_ref(self) -> None:
        root = self.copy_repo_fixture()
        try:
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            result = self.run_script(
                root,
                "release-plan.py",
                "--channel",
                "beta",
                "--stable-ref",
                "no-such-ref",
                "--json",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Could not read dockhand/config.yaml from no-such-ref", result.stderr)
        finally:
            shutil.rmtree(root)

    def test_prepare_stable_removes_beta_metadata_and_stage(self) -> None:
        root = self.copy_repo_fixture()
        self.assert_unreleased(root, "1.0.41.6")
        try:
            result = self.run_script(
                root,
                "prepare-release-channel.py",
                "--channel",
                "stable",
                "--version",
                "1.0.41.6",
                "--dockhand-version",
                "1.0.41",
                "--summary",
                "Promote tested release automation to stable.",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            config = (root / "dockhand/config.yaml").read_text()
            repo = (root / "repository.yaml").read_text()
            self.assertIn('name: Dockhand by JigSawFr', config)
            self.assertIn('version: "1.0.41.6"', config)
            self.assertNotIn('stage: experimental', config)
            self.assertNotIn('Beta by JigSawFr', config + repo)
            self.assertIn('name: Dockhand by JigSawFr', repo)
            self.assertIn("https://github.com/JigSawFr/dockhand-ha-addon'", repo)
            changelog = (root / "dockhand/CHANGELOG.md").read_text()
            readme = (root / "README.md").read_text()
            self.assertIn("## 1.0.41.6", changelog)
            self.assertIn("Promote tested release automation to stable.", changelog)
            self.assertIn("| Stable | `Dockhand by JigSawFr` | `main` | `1.0.41.6` | `X.Y.Z`, `X.Y.Z.N` | `<version>`, `latest` |", readme)
        finally:
            shutil.rmtree(root)

    def test_prepare_beta_sets_dev_url_stage_and_matrix(self) -> None:
        root = self.copy_repo_fixture()
        self.assert_unreleased(root, "1.0.42.1-beta.1")
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
