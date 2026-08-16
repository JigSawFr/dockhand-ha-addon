#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile scripts/*.py
scripts/test-backup-db.sh
scripts/test-seed-ha-environment.sh
scripts/test-diagnostics-redaction.sh
scripts/test-direct-proxy-auth.sh
python3 scripts/test-direct-proxy-config.py
scripts/release-dry-run.py --json >/dev/null
if command -v node >/dev/null 2>&1; then
    node scripts/test-ingress-shim.js
else
    echo 'node unavailable; skipping ingress shim behavior test'
fi
python3 scripts/check-version-sync.py
python3 scripts/check-public-privacy.py
python3 scripts/check-addon-metadata.py

python3 - <<'PY'
import json
import re
import sys
from pathlib import Path

json.loads(Path('.github/renovate.json').read_text())

root = Path('.')
errors = []
for path in root.rglob('*.md'):
    if '.git' in path.parts:
        continue
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if target.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        target = target.split('#', 1)[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f'{path}: link escapes repo: {target}')
            continue
        if not resolved.exists():
            errors.append(f'{path}: missing link target: {target}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('preflight=ok')
PY

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    if docker build -t dockhand-ha-addon:smoke ./dockhand; then
        IMAGE=dockhand-ha-addon:smoke scripts/test-ingress-e2e.sh
    else
        echo 'docker build unavailable in this environment; skipping image build and ingress E2E'
    fi
elif command -v docker >/dev/null 2>&1; then
    echo 'docker daemon unavailable; skipping image build'
else
    echo 'docker unavailable; skipping image build'
fi
