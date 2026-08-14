# Backup and restore

Dockhand stores persistent data under `/data`.

Home Assistant add-on backups should include this directory.

## What to back up

Important paths:

```text
/data/db/
/data/backups/
```

The SQLite database normally lives under `/data/db`.

## Before risky operations

Create a Home Assistant backup before:

- updating the add-on
- changing authentication settings
- pruning images aggressively
- removing containers, volumes, or networks
- restoring Dockhand data

## Restore strategy

1. Stop the add-on.
2. Restore the Home Assistant backup or copy the known-good Dockhand data back to `/data`.
3. Start the add-on.
4. Check logs.
5. Open Dockhand and verify environments.

## Automatic local backups

The add-on can create lightweight SQLite backups during startup when enabled.

These are not a replacement for Home Assistant backups. They are a convenience for quick rollback.

Home Assistant backup integration also runs a SQLite WAL checkpoint before the backup when `/data/db/dockhand.db` exists. Local startup backups matching `/data/backups/*.sqlite` are excluded from Home Assistant backups so full backups do not grow with nested rollback copies.

## Sharing backups

Never share raw backups publicly. They may contain:

- environment names
- container names
- image names
- credentials or tokens depending on Dockhand configuration
- internal host details
