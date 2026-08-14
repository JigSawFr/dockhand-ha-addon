## Summary

-

## Test plan

- [ ] `python3 scripts/check-version-sync.py`
- [ ] `python3 scripts/check-public-privacy.py`
- [ ] `python3 scripts/check-addon-metadata.py`
- [ ] `scripts/test-backup-db.sh`
- [ ] `scripts/test-seed-ha-environment.sh`
- [ ] `scripts/test-diagnostics-redaction.sh`
- [ ] `node scripts/test-ingress-shim.js`
- [ ] `scripts/release-dry-run.py --json`
- [ ] `docker build -t dockhand-ha-addon:smoke ./dockhand`
- [ ] `IMAGE=dockhand-ha-addon:smoke scripts/test-ingress-e2e.sh`

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
