# Release process

See [docs/release.md](docs/release.md) for the full release process.

Short stable version:

1. Bump versions with `scripts/bump-version.py`.
2. Run local preflight checks.
3. Open a PR and wait for CI.
4. Merge to `main`.
5. Push a Home Assistant-compatible stable tag:

   ```bash
   git tag vX.Y.Z.N
   git push origin vX.Y.Z.N
   ```

Short beta version:

1. Work from the `dev` branch.
2. Bump to `X.Y.Z.N-beta.M`.
3. Run local preflight checks.
4. Push `dev` and the beta tag:

   ```bash
   git tag vX.Y.Z.N-beta.M
   git push origin dev vX.Y.Z.N-beta.M
   ```

Stable releases publish GHCR tags `X.Y.Z[.N]` and `latest`.

Beta prereleases publish GHCR tags `X.Y.Z.N-beta.M` and `beta`, never `latest`.

Wrapper-only stable releases use `X.Y.Z.N`; beta wrapper previews use `X.Y.Z.N-beta.M`. Build metadata with `+` is intentionally not used because Docker tags do not allow `+`.
