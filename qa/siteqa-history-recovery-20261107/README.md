# Site QA: History Lab release-recovery freshness gate (read-only)

**Scope:** isolated test code. No WordPress changes, HTTP requests, email sends, subscribers, plugin activation, deployment, merge, or spending. **DRAFT/RELEASE HOLD.** This does not replace Claude's History Lab release ownership or the broader QA preflight in PR #127.

## Why this exists
The WordPress Activity Log recorded the installation of the active **Final Vestige History Lab 0.4.0-rc24** at **2026-11-08 07:08:48 UTC**, then the installation of an **inactive** LIVEPASS Full34 Successor Controller 0.3.1-predeploy-full34-rc24 at **07:09:14 UTC**. The latest completed backup timestamp visible to independent QA was **04:30:02 UTC**, and the latest scan started at **04:30:10 UTC** (completed after 55 seconds). The two checks therefore predate the latest plugin changes. The site monitor reports UP, and the scan had no reported threats **before** these changes.

Previous Issue #126 backup/scan evidence for the earlier Readiness Inspector 0.3.0 remains valid for that earlier snapshot. It must not be reused as post-install coverage of the newer History Lab builds.

## Usage
Run six local regressions without contacting WordPress:

```sh
python3 qa/siteqa-history-recovery-20261107/verify_recovery.py --self-test
```

To evaluate a **locally sanitized** JSON snapshot assembled from read-only `wpcom_site_activity_log`, `wpcom_plugin_list`, `wpcom_jetpack_backup(action=rewind_status)`, `wpcom_jetpack_scan(action=status)`, and `wpcom_jetpack_backup(action=restore_status)` outputs:

```sh
python3 qa/siteqa-history-recovery-20261107/verify_recovery.py snapshot.json
```

Top-level JSON keys: `activity` (array of WordPress activity records), `plugins` (array of plugin inventory rows), `backup`, `scan`, `restore`. Extract the relevant **structured** fields, not connector envelope metadata. Do not include any credentials, visitor information, subscriber emails, or private logs.

The gate returns **HOLD** unless a completed successful backup and a completed non-error security scan occur *after* the most recent scoped custom History Lab plugin event. Exit status 2 means HOLD/error; exit status 0 means **PASS_FRESHNESS_ONLY**. It never claims working restoration, exact package provenance, successful browser usability, absence of vulnerabilities, or revenue. A later plugin change invalidates prior timestamp clearance.

## Independent acceptance requirements beyond this tool
Owner must validate package/release provenance, backup manifest coverage of modified custom plugins, a governed isolated restoration rehearsal, and actual page behavior in a browser. Preserve existing WordPress paths and backups. No change to production or release-governance rules is authorized by this draft.

**Comparison:** Issue #126 and PR #127; Focus issue #129, conversion issue #820. All future releases remain subject to Claude/QD/founder approval.
