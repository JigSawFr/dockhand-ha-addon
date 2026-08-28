# Troubleshooting

## Add-on refuses to start

Check the logs first.

Common causes:

- Protection Mode is still enabled.
- Docker socket is unavailable.
- `/data` is not writable.
- Dockhand database is corrupt.

## Protection Mode error

Dockhand requires Docker socket access.

Fix:

1. Open the add-on settings.
2. Disable **Protection Mode**.
3. Start the add-on again.

## Blank page through Ingress

Try:

1. Refresh the page.
2. Stop and start the add-on.
3. Clear the browser tab and reopen from Home Assistant sidebar.
4. Check logs for nginx errors.

If the page appeared immediately after enabling Dockhand authentication, current beta builds should redirect to the login page automatically. If the browser still shows stale content, refresh once and reopen from the Home Assistant sidebar.

## Terminal or live logs disconnect

Dockhand uses WebSockets and long-lived streams. The add-on enables Home Assistant ingress streaming and disables nginx buffering for Dockhand stream endpoints.

Usually benign symptoms if you leave a live page:

- stream closes when leaving a page
- logs reconnect after reopening
- UI remains usable

## Docker socket unavailable

Confirm:

- Protection Mode disabled
- add-on config includes Docker API access
- Home Assistant Supervisor is healthy

## Direct reverse-proxy access

Dockhand itself stays bound to loopback-only `127.0.0.1:3000`. The wrapper exposes a separate nginx endpoint on container port `3001` for trusted sibling add-ons and reverse proxies.

For a reverse proxy on the same Home Assistant add-on network, configure `direct_proxy_token` in the Dockhand add-on and use:

```text
http://<dockhand-add-on-hostname>:3001
```

The reverse proxy must add the same private value as an upstream-only header:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Dockhand-Proxy-Token "<same-private-token>";
```

The trusted proxy must overwrite these forwarding headers instead of preserving client-supplied values. A `403` from port `3001` means the token is missing or does not match. Do not expose this header to downstream clients or logs.

Do not target `8099`: it is reserved for Home Assistant Ingress and rejects other source addresses. Do not target `3000`: it is intentionally loopback-only.

If the reverse proxy is outside the Home Assistant add-on network, map optional `3001/tcp` to a host port in the add-on network settings. Keep it disabled when the internal add-on hostname is reachable.

Keep the token private, enable Dockhand authentication, and do not expose the host-published port directly to the public internet.

## Database corruption

Symptoms:

- environments fail to load
- SQLite errors in logs
- Dockhand starts but specific pages crash

Safe response:

1. Stop the add-on.
2. Create a Home Assistant backup.
3. Copy `/data/db` if possible.
4. Try restoring from a known-good backup.
5. Report the error with logs, but remove secrets and personal data first.

Do not delete database files unless you have a verified backup and understand the data loss.

## GHCR image pull fails

Check:

- release exists
- package visibility is public
- Home Assistant can reach `ghcr.io`
- architecture is supported (`amd64` or `aarch64`)

## Diagnostics

Recent add-on versions include helper commands inside the container:

```bash
dockhand-healthcheck
dockhand-diagnostics
```

For a file-based bundle:

```bash
dockhand-support-bundle
```

The diagnostics output is designed to redact common secrets, but review it before sharing publicly. See [Support bundle](support-bundle.md).
