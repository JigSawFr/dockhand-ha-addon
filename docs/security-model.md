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

## Optional direct proxy endpoint

Dockhand remains bound to loopback-only `127.0.0.1:3000`. A separate nginx listener on container port `3001` supports trusted sibling add-ons and reverse proxies without exposing the upstream application directly.

The listener is deny-by-default. Network clients must send the exact `direct_proxy_token` value in the `X-Dockhand-Proxy-Token` header; the option is empty by default and masked in the Home Assistant UI. The wrapper validates the token format, stores the generated nginx auth map with mode `0600`, and removes the token header before forwarding the request to Dockhand.

The add-on declares optional `3001/tcp` host publication, disabled by default. A reverse proxy on the same Home Assistant add-on network can use the add-on hostname on port `3001` without publishing that port on the host, but it still requires the token.

Using this endpoint bypasses Home Assistant Ingress path handling and access controls. Port `8099` remains restricted to the Home Assistant Ingress gateway.

Only use direct proxy access when all of the following are true:

- the caller sends the private proxy token and does not expose it to clients or logs;
- the caller is a trusted sibling add-on, private-network client, or authenticated reverse proxy;
- Dockhand authentication is enabled;
- you understand that Dockhand controls Docker through `/var/run/docker.sock`;
- you do not publish the port directly to the public internet.

Leave host publication disabled for the normal Home Assistant sidebar/Ingress workflow and for same-network add-on proxies.

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
