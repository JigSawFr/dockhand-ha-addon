#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
set -euo pipefail

config_value() {
    local key="$1"
    if declare -F bashio::config >/dev/null 2>&1; then
        bashio::config "$key"
    else
        case "$key" in
            direct_proxy_token) printf '%s' "${DOCKHAND_TEST_DIRECT_PROXY_TOKEN:-}" ;;
            *) printf '\n' ;;
        esac
    fi
}

fail_without_secret() {
    if declare -F bashio::log.fatal >/dev/null 2>&1; then
        bashio::log.fatal 'direct_proxy_token must contain 32-128 characters from A-Z, a-z, 0-9, _ or -.'
    else
        printf '%s\n' 'direct_proxy_token must contain 32-128 safe characters.' >&2
    fi
    exit 1
}

TOKEN=$(config_value 'direct_proxy_token')
AUTH_MAP=${DOCKHAND_DIRECT_AUTH_MAP:-/etc/nginx/conf.d/00-direct-auth-map.conf}

if [ -n "$TOKEN" ] && ! [[ "$TOKEN" =~ ^[A-Za-z0-9_-]{32,128}$ ]]; then
    fail_without_secret
fi

mkdir -p "$(dirname "$AUTH_MAP")"
umask 077
tmp=$(mktemp "${AUTH_MAP}.tmp.XXXXXX")
cleanup() {
    rm -f -- "$tmp"
}
trap cleanup EXIT

{
    printf '%s\n' 'map "$direct_proxy_local:$http_x_dockhand_proxy_token" $direct_proxy_authorized {'
    printf '%s\n' '    default 0;'
    printf '%s\n' '    ~^1: 1;'
    if [ -n "$TOKEN" ]; then
        printf '    ~^0:%s$ 1;\n' "$TOKEN"
    fi
    printf '%s\n' '}'
} > "$tmp"

chmod 600 "$tmp"
mv -f "$tmp" "$AUTH_MAP"
trap - EXIT
