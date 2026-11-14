# Final Vestige: isolated security recovery chronology gate

This QA lane is **offline, read-only, draft-only**. It does not touch WordPress, initiate scans, restore backup, deploy, merge, contact visitors, or execute purchases. It is not evidence of successful real restoration, exploit absence, or checkout readiness.

Run from the repository root:

    python -m unittest discover -s qa/security_recovery -p 'test_*.py' -v
    python qa/security_recovery/recovery_gate.py /private/sanitized_snapshot.json --json

Provide a sanitized local JSON containing only:
- plugin: current installed plugin version and status
- scan: last_scan started_at/error, threats, ignored_threats, and recent_fixes status/description/fixed_on
- backup: backups.last_attempt_status and backups.last_attempt_failed
- activity: filtered action=backup_complete_full and date items
- fixed_version: the minimum vendor fixed version, 3.7.5 in this case

Never commit raw WordPress activity logs, private user identifiers, IP addresses, emails, purchase events, credentials, keys, or cookies.

Five explicit checks: patched plugin active; zero reported active/ignored threats; documented fix timestamp; completed successful full backup strictly later than the patch; and a clean scan started strictly after patch completion. Missing evidence means HOLD. Exit 0 = all five have sufficient evidence; 1 = HOLD; 2 = invalid snapshot.

Observed case: Burst Statistics 3.7.4 -> 3.7.5 fixed on 2026-11-14 02:30:35 UTC, but the latest full backup completed 02:29:17 UTC and latest scan started 02:27:21 UTC. Thus three gates PASS; post-fix backup and post-fix clean-scan gates HOLD. A recovery from the latest pre-fix point may restore the vulnerable version. Recheck plugin version after any authorized restoration.

Tests were executed locally (14 of 14 pass), but GitHub CI, exact committed-source checkout execution, actual restore, and live browser work remain UNVERIFIED. Do not use this code as an automatic release, restore, or QD bypass. Complements historical QA draft PR #127, whose backup check did not compare fix/backup/scan timestamps. Issue #126 is the coordination record.
