# Architecture

```text
Home Assistant UI
    |
    | Ingress
    v
nginx :8099
    |
    | reverse proxy
    v
Dockhand :3000
    |
    | Docker API
    v
/var/run/docker.sock
    |
    v
Home Assistant OS Docker host
```

## Components

### Home Assistant Supervisor

Installs and runs the add-on container, manages Ingress, backups, health monitoring, and updates.

The add-on declares:

- `ingress_stream: true` for long-lived Dockhand requests.
- Docker `HEALTHCHECK` runs the packaged healthcheck helper.
- Home Assistant's default admin-only panel behavior is kept linter-compatible.
- backup hooks that checkpoint SQLite before HA backups and exclude local startup backup copies.
- startup seeding for a default `Home Assistant` Docker environment when no equivalent `/var/run/docker.sock` environment exists.

### nginx

The add-on runs nginx as the Ingress-facing proxy. It listens on port `8099` inside the add-on and only allows the Home Assistant Ingress gateway address.

nginx handles:

- Ingress path handling
- WebSocket upgrade headers
- long-lived stream timeouts
- HTML base path injection
- static Ingress shim delivery

### Dockhand

Dockhand runs as a Node.js production app on `127.0.0.1:3000` inside the add-on.

Runtime environment:

```text
DATA_DIR=/data
PORT=3000
HOST=127.0.0.1
NODE_ENV=production
```

### Persistent data

`/data` is the Home Assistant add-on persistent storage mount.

Dockhand database files live under `/data/db`.

### Docker socket

The add-on needs `/var/run/docker.sock` to manage Docker. Protection Mode must be disabled.

### AppArmor

The packaged AppArmor profile is enabled for beta validation. It is defense in depth around the wrapper runtime; it does not make Docker socket access low-risk.
