# Post-change backup and Jetpack Scan chronology — independent QA

This standalone, offline gate answers only whether authenticated, sanitized WordPress evidence shows a specific plugin activation/update followed by a successful full backup containing that plugin and a completed Jetpack security scan without reported active or ignored threats. It makes **no network calls** and **no WordPress changes**.

It does **not** certify the backup is restorable, that the installed plugin matches reviewed source, that Jetpack Scan detects all vulnerabilities, or that user-facing signup, PDF delivery and mobile presentation work. PASS is not overall release authorization.

## Execute

Run from the repository root:

    python -m unittest discover -s qa/post_change_protection -p 'test_*.py' -v
    python -m py_compile qa/post_change_protection/*.py
    python qa/post_change_protection/audit_postchange.py /private/sanitized_snapshot.json

Last command returns 0 on narrow evidence PASS and nonzero on HOLD. The snapshot is private, local, sanitized and **never committed**. Exclude subscriber data, authentication material, user identities and server paths.

## Inputs

- change.at: plugin activity time in timezone-aware ISO 8601, change.kind plugin_activated/plugin_updated, change.slug exact inventory slug.
- backup.started_at: normalized UTC start time from authenticated Jetpack Backup; if its API returns timezone-less values, establish its time base before normalization.
- backup.completed_at: **separate** Jetpack full-backup completion activity timestamp, not the start time.
- backup.type: full; backup.plugins: exact plugin snapshot from backup-complete activity backup_stats; backup.errors and backup.warnings: JSON-decoded arrays from that event; backup.last_attempt_failed: Jetpack rewind status.
- scan.started_at, duration_seconds, progress, error, threats and ignored_threats: current Jetpack Scan status.

Illustrative snapshot (no personal data):

    {
      "change": {"kind":"plugin_activated","slug":"fv-focus-popup","at":"2026-10-31T22:16:28Z"},
      "backup": {"started_at":"2026-11-01T02:42:35Z","completed_at":"2026-11-01T02:46:36Z","last_attempt_failed":false,"type":"full","plugins":["fv-focus-popup"],"errors":[],"warnings":[]},
      "scan": {"started_at":"2026-11-01T02:45:03Z","duration_seconds":87,"progress":100,"error":false,"threats":[],"ignored_threats":[]}
    }

Distinct from draft PR #127 (latest-backup failure checks without chronology) and #372 (offline ZIP provenance, not backup/scan recency). Draft-only and gated by QD/Decision Queue; never automatically merge, deploy, or publish.
