# Release process

See [docs/release.md](docs/release.md) for the full release process.

Short version:

1. Bump versions with `scripts/bump-version.py`.
2. Run local preflight checks.
3. Open a PR and wait for CI.
4. Merge to `main`.
5. Push a Home Assistant-compatible tag:

   ```bash
   git tag vX.Y.Z.N
   git push origin vX.Y.Z.N
   ```

The release workflow publishes GHCR images tagged `X.Y.Z[.N]` and `latest`, then creates a GitHub release from the changelog section.

Wrapper-only releases use `X.Y.Z.N`. Build metadata with `+` is intentionally not used because Docker tags do not allow `+`.
