# Release process

This repository keeps the add-on version anchored to the bundled Dockhand version.

## Version policy

- Dockhand bump validated through beta: use the first wrapper revision on the new base, e.g. `1.0.43.1`, previewed as `1.0.43.1-beta.1`. A beta must carry a revision (`X.Y.Z.N-beta.M`), so a bare `X.Y.Z` cannot be reached through the beta channel; `release-plan.py` produces `X.Y.Z.1` for this reason.
- Dockhand bump published straight to stable: the bare upstream SemVer, e.g. `1.0.41`, is still valid.
- Wrapper-only stable fix: use a numeric wrapper revision on the same Dockhand base, e.g. `1.0.41.1`, then `1.0.41.2`.
- Wrapper-only beta: use the next wrapper revision plus beta iteration, e.g. `1.0.41.2-beta.1`, then `1.0.41.2-beta.2`.
- Use the same version string for Home Assistant metadata, Git tags, GitHub Releases, and GHCR tags.
- Stable release tags are `vX.Y.Z` or `vX.Y.Z.N` and must be published from `main`.
- Beta release tags are `vX.Y.Z.N-beta.M` and must be published from `dev`.
- Do not bump to the next upstream-looking patch version for wrapper-only fixes.
- Use numeric wrapper revisions such as `X.Y.Z.1` for wrapper-only fixes.
- Do not use SemVer build metadata with `+` because Docker image tags do not allow `+`.

See [Release channels](channels.md) for Home Assistant stable/beta repository URLs.

## Bump version

Dockhand bump:

```bash
python3 scripts/bump-version.py 1.0.99 --dockhand-version 1.0.99
```

Wrapper-only revision:

```bash
python3 scripts/bump-version.py 1.0.41.1 --dockhand-version 1.0.41 --wrapper-only
```

Beta wrapper revision on `dev`:

```bash
python3 scripts/bump-version.py 1.0.41.2-beta.1 --dockhand-version 1.0.41 --wrapper-only
```

## Preflight

Run locally:

```bash
python3 scripts/check-version-sync.py
python3 scripts/check-public-privacy.py
python3 scripts/check-addon-metadata.py
scripts/test-backup-db.sh
scripts/test-diagnostics-redaction.sh
node scripts/test-ingress-shim.js
scripts/release-dry-run.py --json
docker build -t dockhand-ha-addon:smoke ./dockhand
IMAGE=dockhand-ha-addon:smoke scripts/test-ingress-e2e.sh
```

Or use the combined helper:

```bash
bash scripts/preflight.sh
```

## Stable release

Stable releases are normally created by merging a stable promotion PR.

1. Let the beta channel validate on `dev`.
2. Run the **Promote stable** workflow from GitHub Actions.
3. Review and merge the generated PR into `main`.
4. The **Auto release** workflow dispatches `release.yaml` for the stable version.

Manual fallback after CI is green on `main`:

```bash
git tag vX.Y.Z.N
git push origin vX.Y.Z.N
```

For a pure Dockhand bump, use `vX.Y.Z` instead.

The stable release workflow:

1. validates version sync
2. validates privacy guard
3. confirms the release commit is contained in `origin/main`
4. builds multi-arch images
5. publishes GHCR tags `<version>` and `latest`
6. attaches SBOM/provenance metadata and signs published image refs with cosign
7. creates a GitHub Release from the changelog section

## Beta release

When Renovate detects a new upstream `fnsys/dockhand` image, it opens a PR against `dev`.

The **Normalize Dockhand update** workflow updates the add-on metadata around that PR:

1. computes the next beta wrapper version, e.g. `1.0.42.1-beta.1`
2. keeps the repository URL on the `#dev` channel
3. keeps `Dockhand Beta by JigSawFr` branding and `stage: experimental`
4. updates the changelog and channel matrix
5. reruns the version, privacy, metadata, and release dry-run checks

After the PR is merged to `dev`, **Auto release** validates the branch and dispatches `release.yaml` for the beta version. The release workflow then:

1. validates version sync
2. validates privacy guard
3. confirms the release commit is contained in `origin/dev`
4. builds multi-arch images
5. publishes GHCR tags `<version>` and `beta`
6. attaches SBOM/provenance metadata and signs published image refs with cosign
7. creates a GitHub prerelease from the changelog section

Beta releases never publish `latest`.

Manual fallback after CI is green on `dev`:

```bash
git tag vX.Y.Z.N-beta.M
git push origin dev vX.Y.Z.N-beta.M
```

## Post-release verification

Verify:

- GitHub Release exists
- GHCR package is public
- stable tags `X.Y.Z[.N]` and `latest` resolve
- beta tags `X.Y.Z.N-beta.M` and `beta` resolve when testing the beta channel
- Home Assistant sees the update in the matching repository channel
- install/update works on a test system
