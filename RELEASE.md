# Release process

See [docs/release.md](docs/release.md) for the full release process.

Short version:

1. Bump versions with `scripts/bump-version.py`.
2. Run local preflight checks.
3. Open a PR and wait for CI.
4. Merge to `main`.
5. Push a strict SemVer tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

The release workflow publishes GHCR images tagged `X.Y.Z` and `latest`, then creates a GitHub release from the changelog section.

Four-part versions such as `X.Y.Z.1` are intentionally not used.
