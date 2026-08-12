# Release process

1. Update `dockhand/Dockerfile` to the target `fnsys/dockhand:vX.Y.Z` tag.
2. Update `dockhand/config.yaml` version to `X.Y.Z`.
3. Add a matching `## X.Y.Z` section to `dockhand/CHANGELOG.md`.
4. Open a PR and wait for lint/build/smoke checks.
5. Merge to `main`.
6. Create and push tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

7. The release workflow publishes GHCR images tagged `X.Y.Z` and `latest`, then creates a GitHub release from the changelog section.

For wrapper-only fixes without a Dockhand bump, use an extra patch version such as `X.Y.Z.1`.
