## 1.0.41.2-beta.2

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Published from the `dev` channel for testing before a stable release.
- Enable Home Assistant ingress streaming and add a native Docker `HEALTHCHECK`.
- Keep the packaged AppArmor profile active through Home Assistant's default behavior for beta validation.
- Add Home Assistant backup hooks to checkpoint SQLite and exclude local startup backup copies.
- Rename Home Assistant repository branding to Dockerhand stable/beta names.
- Polish README and channel/install documentation.
- Harden the public privacy guard against local-environment disclosure.
- Does not change the bundled Dockhand application version.

## 1.0.41.2-beta.1

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Published from the `dev` channel for testing before a stable release.
- Does not change the bundled Dockhand application version.

## 1.0.41.1

- Home Assistant add-on wrapper revision for Dockhand `fnsys/dockhand:v1.0.41`.
- Fix GHCR release publishing workflow without changing the bundled Dockhand application version.

## 1.0.41

- Bundle Dockhand `fnsys/dockhand:v1.0.41`.

## 1.0.29

- Maintenance handover: prepare independent community-maintained Dockhand Home Assistant add-on.
- Bundle Dockhand `fnsys/dockhand:v1.0.29`.
- Publish images under `ghcr.io/jigsawfr/dockhand-ha-addon`.
- Add Renovate configuration for Dockhand image, Home Assistant base image, and GitHub Actions updates.
- Update public repository metadata, OCI labels, and installation documentation.

## 1.0.2

- Fix: authentication login redirects to allow Dockhand user authentication.

## 1.0.1

- Fix: nginx startup no longer emits `initgroups(root, 0) failed (1: Operation not permitted)` in Home Assistant addon containers.
- Dev: implement release process

## 1.0.0

- Initial release
- Dockhand Docker management UI wrapped as a Home Assistant app
- Ingress support for sidebar access
- Docker socket passthrough (requires Protection Mode disabled)
- SQLite-backed persistent storage
- Known issue: Home Assistant ingress can log transient stream disconnect noise
  (`net::ERR_FAILED`, `Cannot write to closing transport`) during page navigation;
  this is usually benign when streams reconnect and UI remains responsive
