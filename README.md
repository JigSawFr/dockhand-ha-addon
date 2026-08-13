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

Read the full security model before exposing this add-on to other Home Assistant users: [docs/security-model.md](docs/security-model.md).

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

- Dockhand image: `fnsys/dockhand:v1.0.41`
- Add-on version: `1.0.41`
- Wrapper-only revision: `1.0.41-ha.1`

The add-on uses SemVer-compatible revisions anchored to the bundled Dockhand version. Wrapper-only fixes use `X.Y.Z-ha.N` instead of pretending to be the next Dockhand patch. Four-part versions and `+` build metadata are not used for release/package tags.

## Updates

This repository is maintained independently from the original wrapper repository. Dependency automation tracks:

- Dockhand image tags from `fnsys/dockhand`
- Home Assistant base images
- GitHub Actions

Releases are published from SemVer tags after CI validation. See [docs/release.md](docs/release.md).

## Documentation

- [Installation](docs/installation.md)
- [Security model](docs/security-model.md)
- [Architecture](docs/architecture.md)
- [Migration](docs/migration.md)
- [Backup and restore](docs/backup-restore.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release process](docs/release.md)

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
