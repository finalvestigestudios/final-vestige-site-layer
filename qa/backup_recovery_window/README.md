# Offline backup recovery-window guard

Read-only QA companion to draft PR #127; that preflight detects explicit failed backup attempts, but not an old last successful recovery point or recorded edits afterward.

Run using a LOCAL SANITIZED JSON file with backup.rewind_status response under backup and activity.get reduced to objects with only date and name under activities. Never commit live snapshots, actor identity, emails, tokens, credentials or customer data.

Example JSON: {"backup":{"backups":{"last_backup_when":"2026-10-30 02:26:30","last_attempt_failed":false,"last_attempt_status":"finished"}},"activities":[{"date":"2026-10-30T16:13:31Z","name":"post__updated"}]}

Commands:
  node qa/backup_recovery_window/guard.cjs sanitized.json --as-of 2026-10-31T02:49:44Z --max-hours 24
  node --test qa/backup_recovery_window/guard.test.cjs

REVIEW flags for stale recovery point or newer site writes do NOT prove backup service failure or lack of other incremental protections. FAILED_ATTEMPT is separately P0; unknown and future timestamps fail closed. Current Jetpack data shows latest attempt finished without failure but last confirmed recovery point still 2026-10-30 02:26:30 UTC, with approved WordPress edits 16:13-16:14 UTC and WordPress Agent plugin update 22:46 UTC.

No network, CMS writes, subscriber actions, backups, plugin changes, deployment or expenses. Keep DRAFT; verify a newer Jetpack recovery point and coordinate any live action with Claude and QD.
