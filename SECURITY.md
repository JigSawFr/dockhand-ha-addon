# Security Policy

Dockhand by JigSawFr is a community-maintained Home Assistant wrapper around [Dockhand](https://github.com/Finsys/dockhand).

## Security model

This add-on intentionally requires Docker access.

To manage containers, images, volumes, and networks, Dockhand needs access to the Home Assistant host Docker socket. That means:

- **Protection Mode must be disabled** before starting the add-on.
- The add-on can control Docker workloads on the host.
- Anyone with access to Dockhand has powerful administrative capability.

This is similar in risk to running Portainer or any Docker management UI with `/var/run/docker.sock` access.

## Recommended usage

- Install only on Home Assistant systems you administer.
- Keep Home Assistant and this add-on updated.
- Use Home Assistant user access controls carefully.
- Make a Home Assistant backup before destructive container/image operations.
- Do not expose Dockhand directly to the internet.
- Prefer Home Assistant Ingress access over direct ports.

## Supported versions

Only the latest released version is supported for security fixes.

## Reporting a vulnerability

Please use GitHub Security Advisories when available.

If you cannot use advisories, open a minimal issue without exploit details and ask for a private contact path.

Do not include secrets, tokens, personal data, database dumps, or full Home Assistant diagnostics in public issues.

## What counts as a vulnerability

Examples:

- unintended direct network exposure
- authentication or Ingress bypass
- leaked secrets or credentials
- unsafe default configuration beyond the documented Docker socket requirement
- supply-chain compromise in the wrapper or release workflow

## By design

The following are expected behavior when Protection Mode is disabled:

- Dockhand can control Docker containers.
- Dockhand can access Docker metadata.
- Docker socket access is highly privileged.

These are documented operational risks, not vulnerabilities by themselves.
