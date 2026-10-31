# Offline security-scan change-window QA

This guard answers **only** whether a recorded plugin, theme or core code change happened after the site's latest **reported completed** Jetpack security scan. It cannot establish the site's true vulnerability status or replace a scan. The intended result is coordinated editorial/operations REVIEW, never automatic remediation.

Supply a **locally sanitized** JSON snapshot with `scan.last_scan` (`started_at`, `duration_seconds`, `error`) and `activities` containing **only** `{name,date}` objects. Do not save/commit live activity actors, emails, plugin credentials, tokens, customer data or raw API responses. It performs **no networking, WordPress writes, scans, merges, deployments or plugin operations**.

Commands: `node qa/security_scan_delta/guard.cjs /path/to/sanitized-snapshot.json --as-of 2026-10-31T05:55:00Z` and `node --test qa/security_scan_delta/guard.test.cjs`.

Exit statuses: `0` no reported code change since last completed scan; `1` review needed; `2` unknown/malformed input. A `NO_ALERTS_IN_SNAPSHOT` result is **not** a security certification. This is distinct from recovery-point backup guard in draft PR #235; a healthy backup does not mean newer plugin code was covered. Review actual scan status after legitimate changes through existing owner/Claude/QD workflow; do not trigger scans or modify production automatically.
