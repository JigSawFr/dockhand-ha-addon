<p align="center">
  <a href="https://www.home-assistant.io/"><img src="home-assistant-logo.svg" alt="Home Assistant Logo" height="60" /></a>
  &nbsp;&nbsp;<img src="plus-icon.svg" alt="Plus" height="30" />&nbsp;&nbsp;
  <a href="https://github.com/Finsys/dockhand"><img src="dockhand/logo.png" alt="Dockhand Logo" height="60" /></a>
</p>

# Dockhand Home Assistant Add-on

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

A Home Assistant add-on repository for [Dockhand](https://github.com/Finsys/dockhand), a modern lightweight Docker management UI and Portainer alternative.

This repository packages Dockhand for Home Assistant OS / Supervisor with Ingress support, persistent `/data` storage, and multi-arch images published to GHCR.

> Community project: this add-on is not affiliated with Dockhand, Finsys, or Home Assistant.

## Installation

### Automatic install

[![Open your Home Assistant instance and show the add-on repository dialog with this repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?repository_url=https%3A%2F%2Fgithub.com%2FJigSawFr%2Fdockhand-ha-addon&addon=dockhand)

### Manual install

1. Open Home Assistant.
2. Go to **Settings → Add-ons → Add-on Store**.
3. Open the ⋮ menu → **Repositories**.
4. Add this repository URL:

   ```text
   https://github.com/JigSawFr/dockhand-ha-addon
   ```

5. Install **Dockhand**.

## Running Dockhand

> **Protection Mode must be disabled**
>
> Dockhand requires access to the Docker socket. Disable **Protection Mode** in the add-on settings before starting it.

Security note: disabling Protection Mode gives this add-on privileged access to Docker, similar to Portainer. Only run it if you trust the workload.

Dockhand stores its SQLite database and app data in `/data`, mapped to persistent Home Assistant add-on storage. Data survives restarts and updates.

## Access

Dockhand is exposed through Home Assistant Ingress. Direct access outside Home Assistant is disabled by default.

## First use

To manage the local Home Assistant Docker environment:

1. Open Dockhand.
2. Go to settings.
3. Add an environment.
4. Use the local Docker socket option when available.

Worthwhile setting: enable automatic image pruning under the environment **Updates** settings to reduce disk pressure on Home Assistant OS.

## Versioning

The add-on version tracks the bundled Dockhand image version where practical.

Example:

- Dockhand image: `fnsys/dockhand:v1.0.29`
- Add-on version: `1.0.29`

If the add-on wrapper needs a fix without a Dockhand bump, the add-on may use an extra patch version such as `1.0.29.1`.

## Updates

This repository is maintained independently from the original wrapper repository. Dependency automation tracks:

- Dockhand image tags from `fnsys/dockhand`
- Home Assistant base images
- GitHub Actions

Releases are published manually at first, after CI validation.

## Attribution

This project is based on the Apache-2.0 licensed work from [`alexschwantes/home-assistant-dockhand-app`](https://github.com/alexschwantes/home-assistant-dockhand-app), adapted for independent community maintenance.

Dockhand itself is developed by [Finsys](https://github.com/Finsys/dockhand).

## Known issues

- **Authentication page refresh:** after enabling Dockhand authentication, you may need to refresh the page once to see the login screen.
- **Ingress stream disconnect noise:** Home Assistant Supervisor logs may show transient stream disconnects when navigating away from long-lived Dockhand pages. This is usually benign.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[releases-shield]: https://img.shields.io/github/release/JigSawFr/dockhand-ha-addon.svg
[releases]: https://github.com/JigSawFr/dockhand-ha-addon/releases
[project-stage-shield]: https://img.shields.io/badge/project%20stage-development-yellowgreen.svg
