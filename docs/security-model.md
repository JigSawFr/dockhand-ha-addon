# Security model

Dockhand Home Assistant Add-on packages Dockhand as a Home Assistant Supervisor add-on.

## Trust boundary

```text
Home Assistant user
  -> Home Assistant Ingress
  -> nginx inside the add-on
  -> Dockhand Node.js app
  -> /var/run/docker.sock
  -> Home Assistant OS Docker host
```

The important boundary is Docker socket access. Once enabled, Dockhand can manage Docker resources on the host.

## Protection Mode

Protection Mode must be disabled because Home Assistant otherwise blocks the privileged access needed by Docker management tools.

This is intentional and explicit.

## Operational risk

Docker socket access is effectively administrative host access. A user who can control Dockhand can start, stop, inspect, remove, and create Docker workloads.

Run this add-on only if you accept that trade-off.

## Safer operating practices

- Keep access through Home Assistant Ingress.
- Do not enable direct external ports unless you know exactly why.
- Restrict Home Assistant admin access.
- Keep backups before destructive maintenance.
- Keep the add-on updated.
- Avoid running unknown third-party containers from Dockhand.

## Data stored by the add-on

Dockhand stores its application data under `/data`, including its SQLite database.

Home Assistant add-on backups include this persistent add-on data.

## Incident response

If Dockhand behaves unexpectedly:

1. Stop the add-on.
2. Create a Home Assistant backup.
3. Export add-on logs.
4. Run diagnostics if available.
5. Review Docker containers created or modified recently.
6. Report security-sensitive issues privately.
