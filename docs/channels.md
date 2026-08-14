# Release channels

This repository uses two Home Assistant add-on channels.

## Stable channel

Repository URL:

```text
https://github.com/JigSawFr/dockhand-ha-addon
```

- Branch: `main`
- Intended for normal Home Assistant installations.
- Release versions: `X.Y.Z` or `X.Y.Z.N`
- GHCR tags: `<version>` and `latest`
- GitHub Releases: regular releases

## Beta channel

Repository URL:

```text
https://github.com/JigSawFr/dockhand-ha-addon#dev
```

Home Assistant supports installing a repository branch by appending the branch name after `#` in the repository URL.

- Branch: `dev`
- Intended for testing wrapper changes before stable promotion.
- Release versions: `X.Y.Z.N-beta.M`
- GHCR tags: `<version>` and `beta`
- GitHub Releases: prereleases
- The bundled Dockhand version stays anchored to `X.Y.Z`.

Example beta version:

```text
1.0.41.2-beta.1
```

This means:

- bundled Dockhand: `fnsys/dockhand:v1.0.41`
- target stable wrapper revision: `1.0.41.2`
- beta iteration: `beta.1`

## Why branch-based channels?

Home Assistant add-on repositories are branch-aware. A beta channel should live on its own branch and repository URL so stable users do not see prerelease versions as normal updates.

The add-on `slug` remains `dockhand`; Home Assistant prefixes installed add-ons by repository, so stable and beta repositories can be distinguished by their repository source.

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

The release workflow validates that beta versions are published from `dev`. It publishes the version tag plus `beta`, but never `latest`.

## Promoting beta to stable

When a beta is validated:

1. Port or merge the tested changes to `main`.
2. Bump to the stable target version, e.g. `1.0.41.2`.
3. Publish `v1.0.41.2` from `main`.

Stable release validation refuses prerelease versions on `main`, and beta release validation refuses non-beta versions on `dev`.
