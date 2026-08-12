# Migration

This guide is for moving from another Dockhand Home Assistant wrapper to this add-on.

## Before starting

1. Create a full Home Assistant backup.
2. Export or record important Dockhand settings.
3. Stop the old Dockhand add-on.
4. Do not delete the old add-on until the new one is verified.

## Data location

This add-on stores Dockhand data in:

```text
/data
/data/db
```

Older wrappers may store data in different container paths, depending on how they mapped Dockhand.

## Safe migration approach

1. Install this add-on.
2. Disable Protection Mode.
3. Start once to create `/data` structure.
4. Stop the add-on.
5. Copy the old Dockhand data into this add-on's `/data` storage.
6. Start the add-on.
7. Verify environments, stacks, repositories, and credentials.
8. Keep the old add-on stopped as rollback until satisfied.

## Rollback

If migration fails:

1. Stop this add-on.
2. Start the old add-on.
3. Restore from backup if needed.

## Database integrity

If Dockhand reports SQLite corruption, do not keep retrying destructive actions.

Create a backup, inspect logs, and restore from a known-good copy if available.
