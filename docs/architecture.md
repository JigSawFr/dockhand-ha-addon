# Architecture

```text
Home Assistant UI                     Trusted sibling reverse proxy
    |                                             |
    | Ingress                                     | internal HTTP
    v                                             v
nginx :8099 (HA gateway only)          nginx :3001 (direct endpoint)
    |                                             |
    +----------------------+----------------------+
                           |
                           | reverse proxy
                           v
                 Dockhand 127.0.0.1:3000
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

The add-on runs one nginx process with two separated listeners:

- `8099` is the Ingress-facing endpoint and only allows the Home Assistant Ingress gateway address;
- `3001` is the token-authenticated direct endpoint for trusted sibling add-ons or an optional host mapping.

Both listeners proxy to Dockhand on loopback. Only the Ingress listener injects the Home Assistant base path and shim. Network access to `3001` is denied until `direct_proxy_token` is configured and supplied in the `X-Dockhand-Proxy-Token` request header.

nginx handles:

- source isolation between Ingress and direct access
- Ingress path handling
- WebSocket upgrade headers
- unbuffered long-lived API streams
- long-lived stream timeouts
- HTML base path injection on Ingress only
- static Ingress shim delivery on Ingress only

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
