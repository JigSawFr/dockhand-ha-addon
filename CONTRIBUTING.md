# Contributing

Thanks for improving Dockhand Home Assistant Add-on.

## Ground rules

- Keep this repository independent from upstream wrapper sync automation.
- Preserve the fork history.
- Use strict SemVer.
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
python3 scripts/bump-version.py 1.0.30 --dockhand-version 1.0.30
```

Wrapper-only patch:

```bash
python3 scripts/bump-version.py 1.0.30 --dockhand-version 1.0.29 --wrapper-only
```

Rules:

- Add-on versions are strict `MAJOR.MINOR.PATCH` SemVer.
- Dockhand image versions are tracked separately.
- Do not use four-part versions.
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

Before tagging `vX.Y.Z`:

- [ ] Version guard is green.
- [ ] Privacy guard is green.
- [ ] Lint is green.
- [ ] Smoke test is green.
- [ ] Builder is green.
- [ ] GHCR publish permissions are confirmed.
- [ ] Changelog section `## X.Y.Z` exists.
