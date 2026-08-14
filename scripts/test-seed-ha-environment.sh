#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
script="$repo_root/dockhand/rootfs/usr/bin/dockhand-seed-ha-environment"
tmp=$(mktemp -d)
cleanup() {
    rm -rf "$tmp"
}
trap cleanup EXIT

if ! command -v sqlite3 >/dev/null 2>&1; then
    mkdir -p "$tmp/bin"
    cat > "$tmp/bin/sqlite3" <<'PY'
#!/usr/bin/env python3
import sqlite3
import sys

if len(sys.argv) < 2:
    raise SystemExit('usage: sqlite3 DB [SQL]')
path = sys.argv[1]
sql = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
conn = sqlite3.connect(path)
cur = conn.cursor()
for stmt in [part.strip() for part in sql.split(';') if part.strip()]:
    cur.execute(stmt)
    if cur.description:
        for row in cur.fetchall():
            print('|'.join('' if value is None else str(value) for value in row))
conn.commit()
conn.close()
PY
    chmod +x "$tmp/bin/sqlite3"
    export PATH="$tmp/bin:$PATH"
fi

create_db() {
    local db="$1"
    sqlite3 "$db" <<'SQL'
CREATE TABLE environments (
    id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
    name text NOT NULL,
    host text,
    port integer DEFAULT 2375,
    protocol text DEFAULT 'http',
    tls_ca text,
    tls_cert text,
    tls_key text,
    tls_skip_verify integer DEFAULT false,
    icon text DEFAULT 'globe',
    collect_activity integer DEFAULT true,
    collect_metrics integer DEFAULT true,
    highlight_changes integer DEFAULT true,
    labels text,
    connection_type text DEFAULT 'socket',
    socket_path text DEFAULT '/var/run/docker.sock',
    hawser_token text,
    hawser_last_seen text,
    hawser_agent_id text,
    hawser_agent_name text,
    hawser_version text,
    hawser_capabilities text,
    created_at text DEFAULT CURRENT_TIMESTAMP,
    updated_at text DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX environments_name_unique ON environments (name);
SQL
}

# Creates the default Home Assistant environment when no equivalent exists.
db_create="$tmp/create.sqlite"
create_db "$db_create"
DOCKHAND_DB_PATH="$db_create" \
DOCKHAND_SEED_REQUIRE_SOCKET=false \
bash "$script" >/dev/null

row=$(sqlite3 "$db_create" "SELECT name || '|' || connection_type || '|' || socket_path || '|' || labels || '|' || icon || '|' || collect_activity || '|' || collect_metrics || '|' || highlight_changes FROM environments;")
[ "$row" = 'Home Assistant|socket|/var/run/docker.sock|["ha"]|globe|1|1|1' ] || { echo "unexpected seeded row: $row"; exit 1; }

# Idempotent: running again does not duplicate.
DOCKHAND_DB_PATH="$db_create" \
DOCKHAND_SEED_REQUIRE_SOCKET=false \
bash "$script" >/dev/null
count=$(sqlite3 "$db_create" "SELECT COUNT(*) FROM environments;")
[ "$count" = "1" ] || { echo "expected one environment after second run, got $count"; exit 1; }

# Existing socket environment means the HA environment already effectively exists.
db_socket="$tmp/socket.sqlite"
create_db "$db_socket"
sqlite3 "$db_socket" "INSERT INTO environments (name, connection_type, socket_path, labels) VALUES ('Custom Docker', 'socket', '/var/run/docker.sock', '[\"custom\"]');"
DOCKHAND_DB_PATH="$db_socket" \
DOCKHAND_SEED_REQUIRE_SOCKET=false \
bash "$script" >/dev/null
count=$(sqlite3 "$db_socket" "SELECT COUNT(*) FROM environments;")
name=$(sqlite3 "$db_socket" "SELECT name FROM environments;")
[ "$count" = "1" ] && [ "$name" = "Custom Docker" ] || { echo "seed duplicated existing socket environment"; exit 1; }

# Existing HA name with another socket is respected.
db_name="$tmp/name.sqlite"
create_db "$db_name"
sqlite3 "$db_name" "INSERT INTO environments (name, connection_type, socket_path) VALUES ('Home Assistant', 'socket', '/custom/docker.sock');"
DOCKHAND_DB_PATH="$db_name" \
DOCKHAND_SEED_REQUIRE_SOCKET=false \
bash "$script" >/dev/null
count=$(sqlite3 "$db_name" "SELECT COUNT(*) FROM environments;")
path=$(sqlite3 "$db_name" "SELECT socket_path FROM environments;")
[ "$count" = "1" ] && [ "$path" = "/custom/docker.sock" ] || { echo "seed overwrote existing Home Assistant environment"; exit 1; }

# Disabled option is a no-op.
db_disabled="$tmp/disabled.sqlite"
create_db "$db_disabled"
DOCKHAND_DB_PATH="$db_disabled" \
DOCKHAND_TEST_SEED_HA_ENVIRONMENT=false \
DOCKHAND_SEED_REQUIRE_SOCKET=false \
bash "$script" >/dev/null
count=$(sqlite3 "$db_disabled" "SELECT COUNT(*) FROM environments;")
[ "$count" = "0" ] || { echo "expected no seed when disabled, got $count rows"; exit 1; }

# Missing schema is a safe no-op.
db_empty="$tmp/empty.sqlite"
sqlite3 "$db_empty" 'CREATE TABLE placeholder (id integer);'
DOCKHAND_DB_PATH="$db_empty" \
DOCKHAND_SEED_REQUIRE_SOCKET=false \
bash "$script" >/dev/null

echo 'ha_environment_seed_tests=ok'
