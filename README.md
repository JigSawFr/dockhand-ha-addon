<p align="center">
  <a href="https://www.home-assistant.io/"><img src="home-assistant-logo.svg" alt="Home Assistant" height="58" /></a>
  &nbsp;&nbsp;<img src="plus-icon.svg" alt="plus" height="28" />&nbsp;&nbsp;
  <a href="https://github.com/Finsys/dockhand"><img src="dockhand/logo.png" alt="Dockhand" height="58" /></a>
</p>

<h1 align="center">Dockhand by JigSawFr</h1>

<p align="center">
  <strong>Dockhand packaged cleanly for Home Assistant OS / Supervisor.</strong><br />
  Docker management through Home Assistant Ingress, with persistent data, beta channel, and multi-arch GHCR images.
</p>

<p align="center">
  <a href="https://github.com/JigSawFr/dockhand-ha-addon/releases"><img alt="Release" src="https://img.shields.io/github/v/release/JigSawFr/dockhand-ha-addon?label=release" /></a>
  <img alt="Project stage" src="https://img.shields.io/badge/project%20stage-development-yellowgreen.svg" />
  <img alt="aarch64" src="https://img.shields.io/badge/aarch64-yes-green.svg" />
  <img alt="amd64" src="https://img.shields.io/badge/amd64-yes-green.svg" />
  <img alt="Home Assistant" src="https://img.shields.io/badge/Home%20Assistant-Add--on-41BDF5" />
</p>

---

## Why this add-on?

[Dockhand](https://github.com/Finsys/dockhand) is a modern, lightweight Docker management UI — a cleaner Portainer-style experience for day-to-day container operations.

This repository wraps Dockhand as a Home Assistant add-on with:

- **Home Assistant Ingress** as the default access path.
- **Persistent `/data` storage** for Dockhand database and app data.
- **Multi-arch images** for `aarch64` and `amd64`.
- **Stable + beta channels** so risky wrapper changes can be tested first.
- **Explicit security documentation** for Docker socket access.

> Community project: this add-on is not affiliated with Dockhand, Finsys, or Home Assistant.

## Install

### Stable channel

Best for normal use.

[![Open your Home Assistant instance and show the add-on repository dialog with this repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?repository_url=https%3A%2F%2Fgithub.com%2FJigSawFr%2Fdockhand-ha-addon&addon=dockhand)

Manual repository URL:

```text
https://github.com/JigSawFr/dockhand-ha-addon
```

Repository name in Home Assistant:

```text
Dockhand by JigSawFr
```

### Beta channel

Best for testing wrapper changes before stable promotion.

Add this repository URL manually:

```text
https://github.com/JigSawFr/dockhand-ha-addon#dev
```

Repository name in Home Assistant:

```text
Dockhand Beta by JigSawFr
```

Beta versions look like `1.0.41.2-beta.1` and publish GHCR tags `beta` plus the exact version. See [Release channels](docs/channels.md).

## First start

1. Install **Dockhand** from the selected repository.
2. Open the add-on page.
3. Disable **Protection Mode**.
4. Start the add-on.
5. Open Dockhand from the Home Assistant sidebar or Ingress button.
6. The add-on creates a default **Home Assistant** Docker environment automatically when no equivalent `/var/run/docker.sock` environment exists.

Useful Dockhand setting: enable automatic image pruning under environment **Updates** to reduce image buildup.

## Security, plainly

Dockhand manages Docker. This add-on therefore needs access to the Docker socket and requires **Protection Mode disabled**.

That is powerful access. Treat it like Portainer:

- install it only on Home Assistant systems you administer;
- keep access through Home Assistant Ingress where possible;
- do not expose the optional direct port to the public internet;
- read the [Security model](docs/security-model.md) before sharing access with other users.

Defense-in-depth included by the wrapper:

- Home Assistant's admin-only panel default;
- optional direct port disabled by default;
- Docker `HEALTHCHECK` using the packaged healthcheck helper;
- Ingress streaming support for long-lived UI flows;
- packaged AppArmor profile validation on beta before stable promotion;
- Home Assistant backup hooks for the SQLite database;
- safe support bundle generation with redaction tests;
- release dry-run, SBOM/provenance, and image signing for release automation.

## Channels at a glance

| Channel | Home Assistant repository | Branch | Current version | Versions | GHCR tags |
|---|---|---:|---:|---|---|
| Stable | `Dockhand by JigSawFr` | `main` | `1.0.41.2` | `X.Y.Z`, `X.Y.Z.N` | `<version>`, `latest` |
| Beta | `Dockhand Beta by JigSawFr` | `dev` | `1.0.41.2-beta.5` | `X.Y.Z.N-beta.M` | `<version>`, `beta` |

Stable users do not receive beta builds unless they explicitly add the `#dev` repository URL.

## Add-on options

| Option | Default | Purpose |
|---|---:|---|
| `seed_home_assistant_environment` | `true` | Create a default `Home Assistant` Docker environment for `/var/run/docker.sock` when no equivalent environment exists. |
| `auto_backup_on_start` | `true` | Create a lightweight SQLite backup during startup. |
| `backup_retention` | `5` | Keep the newest local startup backups. |

## Versioning

The add-on version stays anchored to the bundled Dockhand version.

Example:

| Surface | Example |
|---|---|
| Bundled Dockhand image | `fnsys/dockhand:v1.0.41` |
| First stable wrapper | `1.0.41` |
| Stable wrapper-only fix | `1.0.41.1` |
| Beta wrapper preview | `1.0.41.2-beta.1` |

Wrapper-only stable updates use numeric revisions (`X.Y.Z.N`) so Home Assistant can sort them as updates from `X.Y.Z`.

## Documentation

- [Installation](docs/installation.md)
- [Release channels](docs/channels.md)
- [Security model](docs/security-model.md)
- [Architecture](docs/architecture.md)
- [Migration](docs/migration.md)
- [Backup and restore](docs/backup-restore.md)
- [Support bundle](docs/support-bundle.md)
- [Supply-chain posture](docs/supply-chain.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release process](docs/release.md)

## Attribution

This project is based on the Apache-2.0 licensed work from [`alexschwantes/home-assistant-dockhand-app`](https://github.com/alexschwantes/home-assistant-dockhand-app), adapted for independent community maintenance.

Dockhand itself is developed by [Finsys](https://github.com/Finsys/dockhand). This repository packages the upstream application; it does not replace upstream Dockhand licensing, privacy, or support terms.

## Resolved / mitigated issues

- **Authentication enable flow:** the Home Assistant ingress shim now redirects to Dockhand login automatically after authentication is enabled successfully.
- **Ingress stream disconnect noise:** `ingress_stream: true` and unbuffered stream proxying are enabled. A one-off stream close while navigating away from live views can still be benign.
