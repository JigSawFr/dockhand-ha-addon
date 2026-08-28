#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
generator="$repo_root/dockhand/rootfs/etc/cont-init.d/04-direct-proxy-auth.sh"
tmp=$(mktemp -d)
cleanup() {
    rm -rf "$tmp"
}
trap cleanup EXIT

fixture='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
auth_key='DOCKHAND_TEST_DIRECT_PROXY_'"TOKEN"

# No token: direct proxy stays denied for every non-loopback request.
map_disabled="$tmp/disabled-map.conf"
DOCKHAND_DIRECT_AUTH_MAP="$map_disabled" \
env "${auth_key}=" bash "$generator" >/dev/null
grep -F 'default 0;' "$map_disabled" >/dev/null
grep -F '~^1:' "$map_disabled" >/dev/null
if grep -F '"0:' "$map_disabled" >/dev/null; then
    echo 'disabled direct proxy unexpectedly authorizes a token'
    exit 1
fi
[ "$(stat -c '%a' "$map_disabled")" = '600' ] || { echo 'direct proxy auth map must be mode 600'; exit 1; }

# A valid token produces one exact match without leaking it to stdout.
map_enabled="$tmp/enabled-map.conf"
output=$(DOCKHAND_DIRECT_AUTH_MAP="$map_enabled" \
    env "${auth_key}=${fixture}" bash "$generator")
[ -z "$output" ] || { echo 'direct proxy auth setup must not print token-bearing output'; exit 1; }
grep -F 'default 0;' "$map_enabled" >/dev/null
grep -F "~^0:$fixture\$ 1;" "$map_enabled" >/dev/null
if grep -F "\"0:$fixture\"" "$map_enabled" >/dev/null; then
    echo 'direct proxy auth map uses a case-insensitive literal key'
    exit 1
fi
[ "$(stat -c '%a' "$map_enabled")" = '600' ] || { echo 'direct proxy auth map must be mode 600'; exit 1; }

# Reject whitespace or nginx-syntax characters instead of interpolating them.
map_invalid="$tmp/invalid-map.conf"
invalid_fixture='bad value; include /tmp/evil;'
if DOCKHAND_DIRECT_AUTH_MAP="$map_invalid" \
    env "${auth_key}=${invalid_fixture}" bash "$generator" >/dev/null 2>&1; then
    echo 'invalid direct proxy token was accepted'
    exit 1
fi
if [ -f "$map_invalid" ] && grep -F 'include /tmp/evil' "$map_invalid" >/dev/null; then
    echo 'invalid token reached generated nginx configuration'
    exit 1
fi

echo 'direct_proxy_auth_tests=ok'
