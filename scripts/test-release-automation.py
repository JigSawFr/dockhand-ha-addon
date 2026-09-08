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
            # backmerge-resolve.py drives the tree's own release scripts, the way
            # it does on a runner checkout.
            "scripts/release-plan.py",
            "scripts/prepare-release-channel.py",
        ]:
            dest = tmp / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        return tmp

    def init_channel_fixture(self, root: Path) -> None:
        """A `main` carrying stable identity and a `dev` carrying beta identity,
        diverged the way the two channels always diverge."""
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
        # backmerge-resolve.py commits on its own, so the identity must be on disk.
        subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
        self.commit(root, "base")
        subprocess.run(["git", "checkout", "-q", "-b", "dev"], cwd=root, check=True)
        self.run_script(
            root, "prepare-release-channel.py", "--channel", "beta",
            "--version", "1.0.45.1-beta.1", "--dockhand-version", "1.0.45",
        )
        self.commit(root, "beta")
        subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True)
        # A hotfix released straight to stable: exactly what leaves dev behind.
        self.run_script(
            root, "prepare-release-channel.py", "--channel", "stable",
            "--version", "1.0.45.2", "--dockhand-version", "1.0.45",
        )
        self.commit(root, "stable hotfix")
        subprocess.run(["git", "checkout", "-q", "dev"], cwd=root, check=True)

    def commit(self, root: Path, message: str) -> None:
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message],
            cwd=root,
            check=True,
        )

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

    def test_backmerge_resolves_the_channel_divergence_it_is_supposed_to(self) -> None:
        """main and dev always disagree about channel identity, so a plain merge
        conflicts on every promotion. Those conflicts have a known answer and must
        not block the back-merge."""
        root = self.copy_repo_fixture()
        try:
            self.init_channel_fixture(root)
            result = self.run_script(root, "backmerge-resolve.py", "--stable-ref", "main")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("resolution=resolved", result.stdout)

            config = (root / "dockhand/config.yaml").read_text()
            repo = (root / "repository.yaml").read_text()
            # Beta identity survives the stable side.
            self.assertIn("name: Dockhand Beta by JigSawFr", config)
            self.assertIn("stage: experimental", config)
            self.assertIn("dockhand-ha-addon#dev", repo)
            # And the planner lifted the beta above the stable hotfix it just took.
            self.assertIn('version: "1.0.45.3-beta.1"', config)
            # The stable release entry came across; check-channel-sync.py looks for it.
            changelog = (root / "dockhand/CHANGELOG.md").read_text()
            self.assertIn("## 1.0.45.2\n", changelog)
            self.assertIn("## 1.0.45.3-beta.1\n", changelog)
            # Ancestry is the whole point: a squash would not restore it.
            ancestry = subprocess.run(
                ["git", "merge-base", "--is-ancestor", "main", "HEAD"], cwd=root, check=False
            )
            self.assertEqual(ancestry.returncode, 0, "main must be an ancestor of dev after a back-merge")
        finally:
            shutil.rmtree(root)

    def test_backmerge_refuses_a_conflict_it_has_no_answer_for(self) -> None:
        """Resolving the known divergence must not turn into resolving everything."""
        root = self.copy_repo_fixture()
        try:
            self.init_channel_fixture(root)
            dockerfile = root / "dockhand/Dockerfile"
            dockerfile.write_text(dockerfile.read_text() + "\n# beta side\n")
            self.commit(root, "beta edit")
            subprocess.run(["git", "checkout", "-q", "main"], cwd=root, check=True)
            dockerfile.write_text(dockerfile.read_text() + "\n# stable side\n")
            self.commit(root, "stable edit")
            subprocess.run(["git", "checkout", "-q", "dev"], cwd=root, check=True)

            result = self.run_script(root, "backmerge-resolve.py", "--stable-ref", "main")
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            self.assertIn("conflict=dockhand/Dockerfile", result.stdout)
            # The merge is aborted, not left half-resolved for someone to trip over.
            self.assertFalse((root / ".git/MERGE_HEAD").exists())
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
