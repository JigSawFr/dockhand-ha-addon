#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
script="$repo_root/dockhand/rootfs/usr/bin/dockhand-diagnostics"

input='Authorization: Bearer abc12345
Authorization: Basic Zm9vOmJhcg==
token=abc12345
password: hunter2
api_key sample-key
https://example.invalid/callback?token=abc12345&keep=yes&password=hunter2
'

output=$(printf '%s' "$input" | DOCKHAND_REDACT_STDIN=true bash "$script")

printf '%s\n' "$output" | grep -F 'Authorization: Bearer [REDACTED]' >/dev/null
printf '%s\n' "$output" | grep -F 'Authorization: Basic [REDACTED]' >/dev/null
printf '%s\n' "$output" | grep -F 'token=[REDACTED]' >/dev/null
printf '%s\n' "$output" | grep -F 'password: [REDACTED]' >/dev/null
printf '%s\n' "$output" | grep -F 'api_key [REDACTED]' >/dev/null
printf '%s\n' "$output" | grep -F '?token=[REDACTED]&keep=yes&password=[REDACTED]' >/dev/null

if printf '%s\n' "$output" | grep -E 'abc12345|hunter2|sample-key|Zm9vOmJhcg' >/dev/null; then
    echo 'redaction leaked a fixture secret'
    printf '%s\n' "$output"
    exit 1
fi

echo 'diagnostics_redaction_tests=ok'
