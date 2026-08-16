# Installation

## Pick a channel

| Need | Use |
|---|---|
| Normal install | `Dockhand by JigSawFr` stable channel |
| Test upcoming wrapper changes | `Dockhand Beta by JigSawFr` beta channel |

## Stable install

Repository URL:

```text
https://github.com/JigSawFr/dockhand-ha-addon
```

Home Assistant path:

```text
Settings -> Add-ons -> Add-on Store -> menu -> Repositories
```

Or use the Home Assistant button in the README.

## Beta install

Repository URL:

```text
https://github.com/JigSawFr/dockhand-ha-addon#dev
```

The beta channel appears as `Dockhand Beta by JigSawFr` and publishes versions such as `1.0.41.2-beta.1`. It is intended for validating wrapper changes before they are promoted to stable.

See [Release channels](channels.md) for the full stable/beta policy.

## Install the add-on

1. Select **Dockhand** from the chosen repository.
2. Install the add-on.
3. Open the add-on settings.
4. Disable **Protection Mode**.
5. Start the add-on.
6. Open Dockhand from the sidebar or Ingress button.

## First Docker environment

On startup, the add-on creates a default **Home Assistant** Docker environment automatically when no equivalent `/var/run/docker.sock` environment exists.

Default values:

| Field | Value |
|---|---|
| Name | `Home Assistant` |
| Label | `ha` |
| Connection type | Unix socket |
| Socket path | `/var/run/docker.sock` |

Disable this with the add-on option `seed_home_assistant_environment: false` if you prefer to create environments manually.

Useful setting: enable automatic image pruning in Dockhand's environment **Updates** settings if you want to reduce unused image buildup.

## Optional direct proxy access

Dockhand normally runs through Home Assistant Ingress. This is the recommended mode.

For a trusted reverse proxy running as a sibling Home Assistant add-on:

1. Generate a private token containing 32-128 characters from `A-Z`, `a-z`, `0-9`, `_` or `-`.
2. Set that value in the Dockhand add-on option `direct_proxy_token` and restart Dockhand.
3. Target the Dockhand add-on hostname on internal port `3001`.
4. Configure the reverse proxy to send the same token without exposing it to clients:

   ```nginx
   proxy_set_header Host $host;
   proxy_set_header X-Forwarded-Host $host;
   proxy_set_header X-Forwarded-Proto $scheme;
   proxy_set_header X-Dockhand-Proxy-Token "<same-private-token>";
   ```

The trusted reverse proxy must overwrite these forwarding headers rather than preserve client-supplied values.

Dockhand itself remains on loopback-only `127.0.0.1:3000`. Requests to `3001` without the exact token return `403`.

Do not use port `8099` for this purpose: it is restricted to the Home Assistant Ingress gateway.

Reverse proxies outside the Home Assistant add-on network may optionally map `3001/tcp` to a host port in the add-on network settings. Host publication is disabled by default and should remain disabled when sibling-add-on routing is available.

Keep the token private, enable Dockhand authentication, and do not expose the port directly to the public internet.

## Updating

Home Assistant shows add-on updates when a new release is published.

Release tags use:

- `vX.Y.Z` for bundled Dockhand app bumps;
- `vX.Y.Z.N` for stable wrapper-only revisions;
- `vX.Y.Z.N-beta.M` for beta wrapper previews on `dev`.

## Uninstalling

Before uninstalling:

1. Create a Home Assistant backup.
2. Export anything you need from Dockhand.
3. Stop the add-on.

Uninstalling an add-on may remove its persistent data depending on Home Assistant behavior and selected cleanup options. Back up first.
