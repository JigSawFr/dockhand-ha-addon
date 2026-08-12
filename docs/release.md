# Release process

This repository uses strict SemVer and release tags in the form `vX.Y.Z`.

## Version policy

- Add-on version: strict `MAJOR.MINOR.PATCH`.
- Dockhand upstream image version: tracked separately.
- When possible, the add-on version matches the bundled Dockhand version.
- Wrapper-only fixes use the next SemVer patch version.
- Do not use four-part versions.

## Bump version

Dockhand bump:

```bash
python3 scripts/bump-version.py 1.0.30 --dockhand-version 1.0.30
```

Wrapper-only bump:

```bash
python3 scripts/bump-version.py 1.0.30 --dockhand-version 1.0.29 --wrapper-only
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
git tag vX.Y.Z
git push origin vX.Y.Z
```

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
- tags `X.Y.Z` and `latest` resolve
- Home Assistant sees the update
- install/update works on a test system
