## Summary

-

## Test plan

- [ ] `python3 scripts/check-version-sync.py`
- [ ] `python3 scripts/check-public-privacy.py`
- [ ] `uv run --with pyyaml python scripts/check-addon-metadata.py`
- [ ] `docker build -t dockhand-ha-addon:smoke ./dockhand`

## Release impact

- [ ] No release impact
- [ ] Wrapper-only patch
- [ ] Bundled Dockhand version bump
- [ ] Home Assistant base image change
- [ ] Security-relevant change

## Checklist

- [ ] Strict SemVer preserved
- [ ] Changelog updated when behavior changes
- [ ] Documentation updated
- [ ] No secrets or personal data committed
- [ ] Security model reviewed for Docker socket impact
