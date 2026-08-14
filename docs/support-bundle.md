# Support bundle

`dockhand-support-bundle` creates a small diagnostics file intended for issue reports.

Run it from inside the add-on container or from an add-on terminal when available:

```bash
dockhand-support-bundle
```

Default output:

```text
/data/dockerhand-support-bundle.txt
```

The bundle contains:

- add-on version and architecture
- Node and nginx versions
- `/data` writability and size
- Docker socket presence/read/write checks
- SQLite quick check result when the database exists
- recent nginx errors, redacted

## Redaction

The diagnostics pipeline redacts common credential shapes:

- `Authorization: Bearer ...`
- `Authorization: Basic ...`
- `token=...`
- `password: ...`
- `secret ...`
- `api_key ...`
- URL query parameters such as `?token=...&password=...`

Still review the file before sharing it publicly. Local environment names, container names, image names, and internal paths can still be sensitive even when credentials are redacted.

## What not to share

Do not post these publicly:

- raw Home Assistant backups
- Dockhand database files
- full unredacted logs
- private registry credentials
- tokens, passwords, private keys, or cookies
