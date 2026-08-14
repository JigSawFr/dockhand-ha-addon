# Security model

Dockhand by JigSawFr packages Dockhand as a Home Assistant Supervisor add-on.

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

## AppArmor

The add-on ships and enables an AppArmor profile as a defense-in-depth layer. This does not remove the Docker socket risk, but it narrows ordinary filesystem/process access around the wrapper runtime, nginx, Dockhand, `/data`, and the Docker socket.

Beta releases validate this profile before promotion to stable.

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

## Optional direct access port

The add-on declares an optional `3000/tcp` port, disabled by default.

Enabling this port exposes Dockhand directly and bypasses Home Assistant Ingress. That means Home Assistant's Ingress path handling and access controls no longer protect the Dockhand UI.

Only enable direct access when all of the following are true:

- you are on a trusted private network, or you place Dockhand behind your own authenticated reverse proxy;
- Dockhand authentication is configured when appropriate;
- you understand that Dockhand controls Docker through `/var/run/docker.sock`;
- you do not expose the port directly to the public internet.

Leave the port disabled for the normal Home Assistant sidebar/Ingress workflow.

## Data stored by the add-on

Dockhand stores its application data under `/data`, including its SQLite database.

Home Assistant add-on backups include this persistent add-on data.

The add-on asks Home Assistant to run a SQLite WAL checkpoint before backups when the database exists. Lightweight startup database copies under `/data/backups/*.sqlite` are excluded from Home Assistant backups to avoid recursively storing rollback copies inside full backups.

## Incident response

If Dockhand behaves unexpectedly:

1. Stop the add-on.
2. Create a Home Assistant backup.
3. Export add-on logs.
4. Run `dockhand-support-bundle` and review the generated file before sharing excerpts.
5. Review Docker containers created or modified recently.
6. Report security-sensitive issues privately.
