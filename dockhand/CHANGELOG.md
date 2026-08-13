## 1.0.41-ha.1

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
