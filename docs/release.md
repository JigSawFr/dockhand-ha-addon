# Release process

This repository keeps the add-on version anchored to the bundled Dockhand version.

## Version policy

- Dockhand bump: use the exact upstream Dockhand SemVer, e.g. `1.0.41`.
- Wrapper-only fix: use a SemVer pre-release revision on the same Dockhand base, e.g. `1.0.41-ha.1`, then `1.0.41-ha.2`.
- Use the same version string for Home Assistant metadata, Git tags, GitHub Releases, and GHCR tags.
- Release tags are `vX.Y.Z` or `vX.Y.Z-ha.N`.
- Do not bump to the next upstream-looking patch version for wrapper-only fixes.
- Do not use four-part versions such as `X.Y.Z.1`.
- Do not use SemVer build metadata with `+` because Docker image tags do not allow `+`.

## Bump version

Dockhand bump:

```bash
python3 scripts/bump-version.py 1.0.99 --dockhand-version 1.0.99
```

Wrapper-only revision:

```bash
python3 scripts/bump-version.py 1.0.41-ha.1 --dockhand-version 1.0.41 --wrapper-only
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

## Release

After CI is green on `main`:

```bash
git tag vX.Y.Z-ha.N
git push origin vX.Y.Z-ha.N
```

For a pure Dockhand bump, use `vX.Y.Z` instead.

The release workflow:

1. validates version sync
2. validates privacy guard
3. builds multi-arch images
4. publishes GHCR tags
5. creates a GitHub Release from the changelog section

## Post-release verification

Verify:

- GitHub Release exists
- GHCR package is public
- tags `X.Y.Z[-ha.N]` and `latest` resolve
- Home Assistant sees the update
- install/update works on a test system
