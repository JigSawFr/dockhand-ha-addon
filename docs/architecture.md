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

Installs and runs the add-on container, manages Ingress, backups, and updates.

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
