# Supply-chain posture

This repository publishes Home Assistant add-on images to GHCR.

## Release provenance

Release images are built by GitHub Actions from a signed Git tag that must be contained in the matching release branch:

- stable tags from `main`
- beta tags from `dev`

The release workflow publishes multi-arch images and asks BuildKit to attach:

- SBOM metadata
- provenance attestations

It also signs published GHCR image references with keyless Sigstore/cosign signing when the release workflow runs in GitHub Actions.

## Dependency updates

Renovate and Dependabot target `dev` first. They watch:

- upstream Dockhand Docker image
- Home Assistant base image
- GitHub Actions
- Dockerfile dependencies

Updates should be validated on the beta channel before promotion to stable.

## Action pinning

Third-party actions should use explicit versions or commit SHAs. Moving refs such as `@master` and `@main` are avoided for runtime/release-critical workflows.

## Verification checklist

After a release, verify:

```bash
cosign verify ghcr.io/jigsawfr/dockhand-ha-addon:<version> \
  --certificate-identity-regexp 'https://github.com/JigSawFr/dockhand-ha-addon/.github/workflows/release.yaml@refs/tags/v.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Also verify that `beta` and `latest` point to the expected digests before announcing a channel update.
