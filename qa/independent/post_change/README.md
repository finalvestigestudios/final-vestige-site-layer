# Independent post-change security and recovery evidence gate

Review-only, inert snapshot checker. This adds a focused security/backup timing gate not covered by the general-purpose readiness checker in draft PR #127. It contains **no network calls or production operations**, creates no subscriber/visitor/customer records, and needs no credentials.

Run tests from the repository root:
python -m unittest discover -s qa/independent/post_change -p 'test_*.py' -v

To inspect an authorized, private, sanitized JSON snapshot:
python qa/independent/post_change/post_change_coverage.py /private/path/site_snapshot.json --strict

Accepted snapshot keys: changes (array with timezone-aware at), scan (Jetpack status with last_scan.started_at/error/progress), backup (rewind_status with backups.last_backup_when/last_attempt_status/last_attempt_failed and restore_preflight_status), restore (restore_status with last_restore.has_restore_record), optional backup_log_warnings (list of severity/message only). Keep snapshots outside Git. Do not include emails, API keys, visitor logs, analytics identifiers, purchase/customer records, raw WordPress credentials, or raw plugin code. Unknown or timezone-naive dates never pass as confirmed coverage.

The checker distinguishes scan CLEAN and backup SUCCESS before a plugin installation from jobs definitely covering the new code. It requires a scan **starting after** the latest change and a reported successful backup **snapshot after** the change. An observed charset mismatch in a backup log is REVIEW, not evidence of data loss. Even COVERED is *not* a code audit, proof of successful restoration, or safe production deployment. Missing restore-preflight/rehearsal is HOLD; no real restore is attempted.

2026-11-11 source-linked facts: review plugin installed 22:09:50 UTC and activated 22:11:05 UTC; scan started 04:32:09 UTC and backup snapshot was 04:31:53 (provider record; local-time interpretation must be verified when used programmatically). Both predate activation. A private History Lab table/connection charset mismatch warning was recorded; no data loss proven. Reference: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/126#issuecomment-6809198897 . All real production approvals stay with founder / Claude / History Lab owner and QD/Decision Queue. Do not merge, deploy, alter site, or queue paid calls under this QA lane.
