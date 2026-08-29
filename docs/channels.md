# Release channels

Dockhand uses two Home Assistant repository channels: **stable** for normal use and **beta** for validating wrapper changes before promotion.

## Channel matrix

| Channel | Repository name in Home Assistant | URL | Branch | Current version | Versions | GHCR tags | GitHub release |
|---|---|---|---:|---:|---|---|---|
| Stable | `Dockhand by JigSawFr` | `https://github.com/JigSawFr/dockhand-ha-addon` | `main` | `1.0.44.1` | `X.Y.Z`, `X.Y.Z.N` | `<version>`, `latest` | regular |
| Beta | `Dockhand Beta by JigSawFr` | `https://github.com/JigSawFr/dockhand-ha-addon#dev` | `dev` | `1.0.44.1-beta.1` | `X.Y.Z.N-beta.M` | `<version>`, `beta` | prerelease |

Home Assistant supports installing a repository branch by appending `#branch` to the repository URL. Stable users stay on `main`; beta users explicitly opt into `#dev`.

## Stable channel

Use this for normal installations:

```text
https://github.com/JigSawFr/dockhand-ha-addon
```

Stable releases are published from `main` only. They update the GHCR `latest` tag.

## Beta channel

Use this for prerelease testing:

```text
https://github.com/JigSawFr/dockhand-ha-addon#dev
```

Beta releases are published from `dev` only. They update the GHCR `beta` tag, but never `latest`.

Current beta additions over stable include the default Home Assistant Docker environment seed, hardened Home Assistant Ingress flow, runtime regression tests, backup/diagnostics tests, release dry-run checks, dependency-update automation, and supply-chain attestations/signing for future releases.

## Version example

```text
1.0.41.2-beta.1
```

Means:

- bundled Dockhand app: `fnsys/dockhand:v1.0.41`
- target stable wrapper revision: `1.0.41.2`
- beta iteration: `beta.1`

## Publishing a beta

From the `dev` branch:

```bash
python3 scripts/bump-version.py 1.0.41.2-beta.1 --dockhand-version 1.0.41 --wrapper-only
python3 scripts/check-version-sync.py --tag v1.0.41.2-beta.1
python3 scripts/check-public-privacy.py
python3 scripts/check-addon-metadata.py
git tag v1.0.41.2-beta.1
git push origin dev v1.0.41.2-beta.1
```

The release workflow verifies that beta tags are contained in `origin/dev` before publishing images.

## Promoting beta to stable

When a beta has been validated:

1. Merge or port the tested changes to `main`.
2. Bump to the stable target version, for example `1.0.41.2`.
3. Publish `v1.0.41.2` from `main`.

The release workflow refuses prerelease versions on the stable path and refuses non-beta versions on the beta path.

## Keeping beta ahead of stable

A fix released straight to `main` — a hotfix that never went through beta — leaves `dev` behind. That gap is not cosmetic: `dev` is what gets promoted back to stable, so the next beta ships a wrapper *behind* stable, and promoting it republishes the regression.

Three things keep the gap from going unnoticed:

- **`scripts/check-channel-sync.py`** fails while `dev` is behind `main`. It asserts that every `main` commit is reachable from `dev`, that the current stable release appears in the beta changelog, and that the beta's promotion target sorts above the released stable version. The `Version guard` workflow runs it on every pull request to `dev`, and `scripts/preflight.sh` runs it locally.
- **`.github/workflows/backmerge-stable.yaml`** opens a `main` → `dev` pull request as soon as `main` moves, so the back-merge is proposed rather than remembered.
- **`release-plan.py --released-stable`** makes the beta planner aware of what stable already ships. Without it, a beta iterating on an older base plans a promotion that moves stable backwards; with it, the planner jumps to the next free revision above stable (`stable-catch-up`).

Back-merges must land as merge commits, not squashes: a squash does not make `main` an ancestor of `dev`, so the merge base never advances and every later back-merge replays the same conflicts. Ordinary pull requests branched from `dev` can be squashed as usual — only a pull request that carries `main` as a parent needs this care.

### The `AUTOMATION_PAT` secret

A push or pull request made with the default `GITHUB_TOKEN` does not start workflow runs. That affects two automations here: the commit `normalize-dockhand-update.yaml` writes onto a Renovate branch — the one carrying the version bump — and the pull request `backmerge-stable.yaml` opens. Without a token, both land with no CI and sit at `action_required` until someone approves the runs by hand.

Set a repository secret named `AUTOMATION_PAT` (a fine-grained token with **Contents: read and write** and **Pull requests: read and write** on this repository) and both automations start CI on their own. Both workflows fall back to `GITHUB_TOKEN` when the secret is absent, and the normalize workflow emits a warning annotation so the gap is visible rather than silent.

## Why keep the same add-on slug?

The add-on slug remains `dockhand` to avoid unnecessary migration friction. Home Assistant differentiates the channels by repository source/name, not by changing the app identity.
