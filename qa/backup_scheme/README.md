# Backup URL scheme QA — metadata only (DRAFT / nonblocking)

This offline comparator checks canonical WordPress `home` and `siteurl` against the `backup_stats.site_url` embedded in Jetpack full-backup activity events. It makes no HTTP/API calls, never edits WordPress, and never initiates a restore.

Run from repository root:

    python -m unittest discover -s qa/backup_scheme -p 'test_*.py' -v
    python qa/backup_scheme/check_backup_site_url.py sanitized-snapshot.json

Sanitized JSON shape: `{"settings":{"general":{"home":"https://example.test","siteurl":"https://example.test"}},"activity":{"activities":[{"date":"2026-11-01T02:46:36Z","object":{"backup_info":{"backup_stats":"{\"site_url\":\"http://example.test\"}"}}}]}}`

**Actual November 1, 2026, read-only observation:** Current WordPress.com settings specify `https://finalvestige.com` for both canonical URLs. Seven separate full-backup events dated October 26–November 1 record `backup_stats.site_url` as `http://finalvestige.com`. Backups report complete with no warnings; latest attempt finished and `last_attempt_failed=false`.

This is a **persistent metadata representation discrepancy**, NOT proof of an outage, compromised HTTPS, invalid restore, or malformed backed-up WordPress database. The semantics of this Jetpack summary field and contents of any restored database are unverified.

Jetpack documents that sites should have a consistent HTTP/HTTPS canonical entry point before performing a restore, but it does not say that `backup_stats.site_url` controls restore destinations or redirects. Reference: https://jetpack.com/support/backup/troubleshooting-jetpack-restores/

**Safe follow-up:** WordPress.com/Jetpack support can clarify this metadata; during any separately approved nonproduction recovery rehearsal, independently verify canonical HTTPS, WordPress options, media paths, redirects and backups. No production restore, changes, upgrades or expenses are authorized.

`REVIEW` returns exit code 0 intentionally (informational, no CI gate). Invalid snapshots return exit code 2. Never commit raw production activity dumps, secrets, account emails or user/subscriber details.
