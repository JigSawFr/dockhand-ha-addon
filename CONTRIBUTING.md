# Contributing

Thanks for improving Dockerhand by JigSawFr — the Dockhand Home Assistant add-on wrapper.

## Ground rules

- Keep this repository independent from upstream wrapper sync automation.
- Preserve the fork history.
- Use SemVer-compatible versions anchored to the bundled Dockhand version.
- Do not commit personal data, secrets, tokens, `.env` files, private keys, or real diagnostics containing credentials.
- Keep public identity metadata generic and GitHub-safe.

## Development setup

Requirements:

- Docker
- Python 3
- Git

Useful checks:

```bash
python3 scripts/check-version-sync.py
python3 scripts/check-public-privacy.py
python3 scripts/check-addon-metadata.py
docker build -t dockhand-ha-addon:smoke ./dockhand
```

Or run the combined preflight helper:

```bash
bash scripts/preflight.sh
```

## Version changes

Use the bump helper:

```bash
python3 scripts/bump-version.py 1.0.99 --dockhand-version 1.0.99
```

Wrapper-only patch:

```bash
python3 scripts/bump-version.py 1.0.41.1 --dockhand-version 1.0.41 --wrapper-only
```

Beta wrapper preview:

```bash
python3 scripts/bump-version.py 1.0.41.2-beta.1 --dockhand-version 1.0.41 --wrapper-only
```

Rules:

- Dockhand bumps use the exact upstream `MAJOR.MINOR.PATCH` version.
- Stable wrapper-only fixes use `MAJOR.MINOR.PATCH.N` on the same Dockhand base.
- Beta wrapper previews use `MAJOR.MINOR.PATCH.N-beta.M` on the `dev` branch.
- Use the same string for config version, Git tag, GitHub Release, and GHCR tag.
- Use numeric wrapper revisions `X.Y.Z.N`; do not use `+` build metadata.
- Add or update the matching `dockhand/CHANGELOG.md` section.

## Pull request checklist

Before opening a PR:

- [ ] `scripts/check-version-sync.py` passes.
- [ ] `scripts/check-public-privacy.py` passes.
- [ ] `scripts/check-addon-metadata.py` passes.
- [ ] Docker image builds locally.
- [ ] Documentation reflects behavior changes.
- [ ] Security implications are documented.

## Release checklist

Before tagging `vX.Y.Z`, `vX.Y.Z.N`, or `vX.Y.Z.N-beta.M`:

- [ ] Version guard is green.
- [ ] Privacy guard is green.
- [ ] Lint is green.
- [ ] Smoke test is green.
- [ ] Builder is green.
- [ ] GHCR publish permissions are confirmed.
- [ ] Matching changelog section exists, e.g. `## X.Y.Z.N` or `## X.Y.Z.N-beta.M`.
