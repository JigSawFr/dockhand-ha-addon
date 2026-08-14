#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
script="$repo_root/dockhand/rootfs/etc/cont-init.d/03-backup-db.sh"
tmp=$(mktemp -d)
cleanup() {
    rm -rf "$tmp"
}
trap cleanup EXIT

db="$tmp/dockhand.db"
backups="$tmp/backups"
mkdir -p "$backups"

python3 - "$db" <<'PY'
import sqlite3, sys
conn = sqlite3.connect(sys.argv[1])
conn.execute('CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT NOT NULL)')
conn.execute('INSERT INTO items(name) VALUES (?)', ('fixture',))
conn.commit()
conn.close()
PY

# Seed old files so retention can prove it keeps the newest backups only.
for n in 1 2 3; do
    old="$backups/dockhand-db-2000010${n}-000000.sqlite"
    printf 'old-%s\n' "$n" > "$old"
    touch -t "2000010${n}0000" "$old"
done

DOCKHAND_TEST_AUTO_BACKUP=true \
DOCKHAND_TEST_BACKUP_RETENTION=2 \
DOCKHAND_DB_PATH="$db" \
DOCKHAND_BACKUP_DIR="$backups" \
bash "$script" >/dev/null

count=$(find "$backups" -maxdepth 1 -type f -name 'dockhand-db-*.sqlite' | wc -l | tr -d ' ')
[ "$count" = "2" ] || { echo "expected 2 backups after retention, got $count"; find "$backups" -type f -maxdepth 1 -print; exit 1; }

latest=$(find "$backups" -maxdepth 1 -type f -name 'dockhand-db-*.sqlite' -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
python3 - "$latest" <<'PY'
import sqlite3, sys
conn = sqlite3.connect(sys.argv[1])
value = conn.execute('SELECT name FROM items WHERE id=1').fetchone()[0]
conn.close()
assert value == 'fixture', value
PY

sleep 1
DOCKHAND_TEST_AUTO_BACKUP=true \
DOCKHAND_TEST_BACKUP_RETENTION=1 \
DOCKHAND_FORCE_COPY_BACKUP=true \
DOCKHAND_DB_PATH="$db" \
DOCKHAND_BACKUP_DIR="$backups" \
bash "$script" >/dev/null

count=$(find "$backups" -maxdepth 1 -type f -name 'dockhand-db-*.sqlite' | wc -l | tr -d ' ')
[ "$count" = "1" ] || { echo "expected 1 backup after forced-copy retention, got $count"; exit 1; }

disabled_out=$(DOCKHAND_TEST_AUTO_BACKUP=false DOCKHAND_DB_PATH="$db" DOCKHAND_BACKUP_DIR="$backups" bash "$script")
printf '%s\n' "$disabled_out" | grep -F 'Startup database backup disabled.' >/dev/null

echo 'backup_tests=ok'
