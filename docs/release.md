# Release process

This repository keeps the add-on version anchored to the bundled Dockhand version.

## Version policy

- Dockhand bump: use the exact upstream Dockhand SemVer, e.g. `1.0.41`.
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
docker build -t dockhand-ha-addon:smoke ./dockhand
```

Or use the combined helper:

```bash
bash scripts/preflight.sh
```

## Stable release

After CI is green on `main`:

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
6. creates a GitHub Release from the changelog section

## Beta release

After CI is green on `dev`:

```bash
git tag vX.Y.Z.N-beta.M
git push origin dev vX.Y.Z.N-beta.M
```

The beta release workflow:

1. validates version sync
2. validates privacy guard
3. confirms the release commit is contained in `origin/dev`
4. builds multi-arch images
5. publishes GHCR tags `<version>` and `beta`
6. creates a GitHub prerelease from the changelog section

Beta releases never publish `latest`.

## Post-release verification

Verify:

- GitHub Release exists
- GHCR package is public
- stable tags `X.Y.Z[.N]` and `latest` resolve
- beta tags `X.Y.Z.N-beta.M` and `beta` resolve when testing the beta channel
- Home Assistant sees the update in the matching repository channel
- install/update works on a test system
