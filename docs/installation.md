# Installation

## Add the repository

Use the Home Assistant button from the README, or add the repository manually:

```text
https://github.com/JigSawFr/dockhand-ha-addon
```

Home Assistant path:

```text
Settings -> Add-ons -> Add-on Store -> menu -> Repositories
```

## Install Dockhand

1. Select **Dockhand**.
2. Install the add-on.
3. Open the add-on settings.
4. Disable **Protection Mode**.
5. Start the add-on.
6. Open Dockhand from the sidebar or Ingress button.

## First environment

To manage the local Home Assistant Docker host:

1. Open Dockhand.
2. Go to settings or environments.
3. Add an environment.
4. Use the local Docker socket option when available.

## Optional direct access

Dockhand normally runs through Home Assistant Ingress. This is the recommended mode.

Advanced users may optionally expose Dockhand's internal `3000/tcp` port from the add-on network settings. The port is disabled by default.

Only enable it on trusted networks or behind your own authenticated reverse proxy. Direct access bypasses Home Assistant Ingress protections.

Do not expose this port directly to the public internet.

## Updating

Home Assistant shows add-on updates when a new release is published.

The add-on uses strict SemVer. Release tags use `vX.Y.Z`.

## Uninstalling

Before uninstalling:

1. Create a Home Assistant backup.
2. Export anything you need from Dockhand.
3. Stop the add-on.

Uninstalling an add-on may remove its persistent data depending on Home Assistant behavior and selected cleanup options. Back up first.
