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

If Dockhand authentication was enabled, a refresh may be required after redirects.

## Terminal or live logs disconnect

Dockhand uses WebSockets and long-lived streams. Home Assistant Ingress can log transient disconnects when navigating away from live views.

Usually benign symptoms:

- stream closes when leaving a page
- logs reconnect after reopening
- UI remains usable

## Docker socket unavailable

Confirm:

- Protection Mode disabled
- add-on config includes Docker API access
- Home Assistant Supervisor is healthy

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

The diagnostics output is designed to avoid secrets, but review before sharing publicly.
