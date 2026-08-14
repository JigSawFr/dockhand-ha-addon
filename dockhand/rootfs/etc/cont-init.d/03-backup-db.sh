#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
set -euo pipefail

log_info() {
    if declare -F bashio::log.info >/dev/null 2>&1; then
        bashio::log.info "$@"
    else
        printf 'INFO: %s\n' "$*"
    fi
}

log_warning() {
    if declare -F bashio::log.warning >/dev/null 2>&1; then
        bashio::log.warning "$@"
    else
        printf 'WARN: %s\n' "$*" >&2
    fi
}

config_true() {
    local key="$1"
    if declare -F bashio::config.true >/dev/null 2>&1; then
        bashio::config.true "$key"
    else
        [ "${DOCKHAND_TEST_AUTO_BACKUP:-true}" = "true" ]
    fi
}

config_value() {
    local key="$1"
    if declare -F bashio::config >/dev/null 2>&1; then
        bashio::config "$key"
    else
        case "$key" in
            backup_retention) printf '%s\n' "${DOCKHAND_TEST_BACKUP_RETENTION:-5}" ;;
            *) printf '\n' ;;
        esac
    fi
}

if ! config_true 'auto_backup_on_start'; then
    log_info "Startup database backup disabled."
    exit 0
fi

DB=${DOCKHAND_DB_PATH:-/data/db/dockhand.db}
BACKUP_DIR=${DOCKHAND_BACKUP_DIR:-/data/backups}
RETENTION=$(config_value 'backup_retention')
RETENTION=${RETENTION:-5}

if ! [[ "$RETENTION" =~ ^[0-9]+$ ]] || [ "$RETENTION" -lt 1 ]; then
    log_warning "Invalid backup retention '${RETENTION}', falling back to 5."
    RETENTION=5
fi

if [ ! -f "$DB" ]; then
    log_info "No Dockhand database found yet; skipping startup backup."
    exit 0
fi

mkdir -p "$BACKUP_DIR"
stamp=$(date +%Y%m%d-%H%M%S)
out="$BACKUP_DIR/dockhand-db-${stamp}.sqlite"

if [ "${DOCKHAND_FORCE_COPY_BACKUP:-false}" != "true" ] && command -v sqlite3 >/dev/null 2>&1; then
    if sqlite3 "$DB" ".backup '$out'"; then
        log_info "Created Dockhand database backup: $out"
    else
        log_warning "SQLite backup failed; falling back to file copy."
        cp -a "$DB" "$out"
    fi
else
    cp -a "$DB" "$out"
    log_info "Created Dockhand database backup by file copy: $out"
fi

# Keep newest N backups.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'dockhand-db-*.sqlite' -printf '%T@ %p\n' \
    | sort -nr \
    | awk -v keep="$RETENTION" 'NR > keep { $1=""; sub(/^ /, ""); print }' \
    | while IFS= read -r old; do
        [ -n "$old" ] || continue
        rm -f -- "$old"
        log_info "Removed old Dockhand database backup: $old"
    done
