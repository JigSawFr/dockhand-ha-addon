#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
set -euo pipefail

if ! bashio::config.true 'auto_backup_on_start'; then
    bashio::log.info "Startup database backup disabled."
    exit 0
fi

DB=/data/db/dockhand.db
BACKUP_DIR=/data/backups
RETENTION=$(bashio::config 'backup_retention')
RETENTION=${RETENTION:-5}

if [ ! -f "$DB" ]; then
    bashio::log.info "No Dockhand database found yet; skipping startup backup."
    exit 0
fi

mkdir -p "$BACKUP_DIR"
stamp=$(date +%Y%m%d-%H%M%S)
out="$BACKUP_DIR/dockhand-db-${stamp}.sqlite"

if command -v sqlite3 >/dev/null 2>&1; then
    if sqlite3 "$DB" ".backup '$out'"; then
        bashio::log.info "Created Dockhand database backup: $out"
    else
        bashio::log.warning "SQLite backup failed; falling back to file copy."
        cp -a "$DB" "$out"
    fi
else
    cp -a "$DB" "$out"
    bashio::log.info "Created Dockhand database backup by file copy: $out"
fi

# Keep newest N backups.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'dockhand-db-*.sqlite' -printf '%T@ %p\n' \
    | sort -nr \
    | awk -v keep="$RETENTION" 'NR > keep { $1=""; sub(/^ /, ""); print }' \
    | while IFS= read -r old; do
        [ -n "$old" ] || continue
        rm -f -- "$old"
        bashio::log.info "Removed old Dockhand database backup: $old"
    done
