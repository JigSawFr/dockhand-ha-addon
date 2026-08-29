## 1.0.45.1

- Promote tested beta 1.0.45.1-beta.1 to stable.
- Stable Home Assistant add-on wrapper revision for Dockhand `fnsys/dockhand:v1.0.45`.
- Promoted from the tested beta channel.
- Dockhand 1.0.45 release notes: https://github.com/Finsys/dockhand/releases/tag/v1.0.45

## 1.0.45.1-beta.1

- Prepare beta validation for Dockhand upstream v1.0.45.
- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.45`.
- Published from the `dev` channel for testing before a stable release.
- Dockhand 1.0.45 release notes: https://github.com/Finsys/dockhand/releases/tag/v1.0.45

## 1.0.44.1-beta.1

- Prepare beta validation for Dockhand upstream v1.0.44.
- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.44`.
- Published from the `dev` channel for testing before a stable release.
- Dockhand 1.0.44 release notes: https://github.com/Finsys/dockhand/releases/tag/v1.0.44

## 1.0.43.1-beta.1

- Prepare beta validation for Dockhand upstream v1.0.43.
- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.43`.
- Published from the `dev` channel for testing before a stable release.
- Prepared by the release automation workflow.

## 1.0.41.5-beta.1

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Sync the beta channel with stable `1.0.41.4`: the direct proxy endpoint on `3001` with a required `direct_proxy_token`, and the runtime `git` and `openssh-client` tools for Git stack SSH deploys.
- Keep the release automation, promotion workflow, and channel guards introduced on the beta channel.
- Does not change the bundled Dockhand application version (`fnsys/dockhand:v1.0.41`).

## 1.0.41.4

- Add a dedicated nginx direct endpoint on internal port `3001` for trusted sibling add-ons and reverse proxies.
- Require an exact, masked `direct_proxy_token` on every network request to port `3001`; deny access by default and strip the token before proxying to Dockhand.
- Keep Dockhand bound to loopback-only `127.0.0.1:3000` and keep port `8099` restricted to the Home Assistant Ingress gateway.
- Keep `/api/activity/events` and `/api/audit/events` unbuffered on both proxy paths, alongside the existing event and stream endpoints.
- Replace the ineffective optional `3000/tcp` host mapping with optional `3001/tcp`, disabled by default.
- Add static guards for stream routing and redirect rules, plus Docker E2E coverage for direct authentication, listener isolation, real login redirects and Ingress shim behavior.
- Does not change the bundled Dockhand application version (`fnsys/dockhand:v1.0.41`).

## 1.0.41.3

- Restore Git stack deploy/redeploy support in the Home Assistant wrapper by shipping runtime `git` and `openssh-client` tools.
- Fix SSH-backed repositories failing before clone with `Cannot read properties of undefined (reading 'toString')` when `ssh-keygen` is unavailable.
- Does not change the bundled Dockhand application version (`fnsys/dockhand:v1.0.41`).

## 1.0.41.2

- Stable Home Assistant add-on wrapper revision for Dockhand `fnsys/dockhand:v1.0.41`.
- Create a default `Home Assistant` Docker environment on startup when no equivalent `/var/run/docker.sock` environment exists.
- Add `seed_home_assistant_environment`, enabled by default, for users who prefer manual environment creation.
- Enable Home Assistant ingress streaming and add a native Docker `HEALTHCHECK`.
- Add backup hooks, redacted diagnostics, support bundle, release dry-run checks, and runtime regression tests.
- Add real Docker-based Home Assistant Ingress E2E coverage plus SQLite seed/backup/diagnostics tests.
- Add Renovate/Dependabot automation, focused issue templates, SBOM/provenance, and cosign signing in the release workflow.
- Promote the tested beta wrapper changes to stable without changing the bundled Dockhand application version.

## 1.0.41.2-beta.5

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Published from the `dev` channel for testing before a stable release.
- Create a default `Home Assistant` Docker environment on startup when no equivalent `/var/run/docker.sock` environment exists.
- Add `seed_home_assistant_environment` add-on option, enabled by default, for users who prefer manual environment creation.
- Add SQLite regression tests for the default environment seed and cover it in smoke/preflight checks.
- Does not change the bundled Dockhand application version.

## 1.0.41.2-beta.4

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Published from the `dev` channel for testing before a stable release.
- Add a real Docker-based Home Assistant Ingress E2E smoke test.
- Add Renovate and Dependabot automation targeting `dev` for Docker images and GitHub Actions.
- Pin moving Home Assistant workflow actions and add release SBOM/provenance plus cosign signing.
- Add regression tests for startup SQLite backups, retention, diagnostics redaction, and release dry-run metadata.
- Add `dockhand-support-bundle` for reviewed redacted diagnostics files.
- Add stable/beta matrix details, support/supply-chain docs, and focused GitHub issue templates.
- Does not change the bundled Dockhand application version.

## 1.0.41.2-beta.3

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Published from the `dev` channel for testing before a stable release.
- Redirect automatically to Dockhand login after authentication is enabled successfully through Home Assistant Ingress.
- Add a regression test for ingress shim auth redirect and path rewriting behavior.
- Move previous auth refresh and stream disconnect notes out of the active Known Issues section.
- Replace the stale add-on-local documentation page with pointers to the current repository docs.
- Does not change the bundled Dockhand application version.

## 1.0.41.2-beta.2

- Beta Home Assistant add-on wrapper preview for Dockhand `fnsys/dockhand:v1.0.41`.
- Published from the `dev` channel for testing before a stable release.
- Enable Home Assistant ingress streaming and add a native Docker `HEALTHCHECK`.
- Keep the packaged AppArmor profile active through Home Assistant's default behavior for beta validation.
- Add Home Assistant backup hooks to checkpoint SQLite and exclude local startup backup copies.
- Rename Home Assistant repository branding to Dockhand stable/beta names.
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
