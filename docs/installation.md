# Installation

## Pick a channel

| Need | Use |
|---|---|
| Normal install | `Dockerhand by JigSawFr` stable channel |
| Test upcoming wrapper changes | `Dockerhand Beta by JigSawFr` beta channel |

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

The beta channel appears as `Dockerhand Beta by JigSawFr` and publishes versions such as `1.0.41.2-beta.1`. It is intended for validating wrapper changes before they are promoted to stable.

See [Release channels](channels.md) for the full stable/beta policy.

## Install the add-on

1. Select **Dockhand** from the chosen repository.
2. Install the add-on.
3. Open the add-on settings.
4. Disable **Protection Mode**.
5. Start the add-on.
6. Open Dockhand from the sidebar or Ingress button.

## First Docker environment

Inside Dockhand:

1. Open settings or environments.
2. Add an environment.
3. Use the local Docker socket option when available.
4. Save and verify the dashboard loads containers/images.

Useful setting: enable automatic image pruning in Dockhand's environment **Updates** settings if you want to reduce unused image buildup.

## Optional direct access

Dockhand normally runs through Home Assistant Ingress. This is the recommended mode.

Advanced users may optionally expose Dockhand's internal `3000/tcp` port from the add-on network settings. The port is disabled by default.

Only enable it on trusted networks or behind your own authenticated reverse proxy. Direct access bypasses Home Assistant Ingress protections.

Do not expose this port directly to the public internet.

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
