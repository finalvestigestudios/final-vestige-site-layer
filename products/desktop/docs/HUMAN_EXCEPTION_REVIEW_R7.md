# R7 — Human Exception Review for Final Vestige Labs

**Pre-release, local-only, human-operated. No financial authorization.** This sprint adds a reviewer console to GrantAudit Studio Pro and ProcureGuard Studio Pro without altering the four free utilities or the separate seven-product desktop initiative.

## User workflow

Generate a synthetic premium exception report in the desktop app, click **Review exceptions (human only)…**, select a flagged record, enter reviewer identity, choose needs_evidence, escalated or reviewed, and write a substantive rationale. Nothing is recorded automatically; entries marked matched are excluded from the review queue.

The reviewer journal is saved locally next to the source report with suffix .review.jsonl. The application records a human event; it NEVER approves payment, determines allowability, certifies an audit, authorizes procurement, asserts fraud, or updates the source ledger. Even a reviewed case still requires any external approval process.

The **Export review register…** button writes a fresh, separate CSV including all flagged rows, the precise originating report SHA-256, status flags, original reference and source row, and the most recent human outcome or pending. CSV-formula characters in exported text are neutralized.

## Design and safety guarantees

- The report is read as one immutable byte snapshot (UTF-8 CSV, 64 MiB and 200,000 row limits). Its exact SHA-256 binds the issue IDs and all review events.
- Each event has schema version, product, originating report hash, source row, original status flags, reviewer, decision, rationale, UTC timestamp, preceding event hash, and its own canonical JSON SHA-256.
- The writer checks the whole previous journal, acquires an exclusive non-blocking .lock file, appends only, flushes, and fsyncs. Changes to original CSV evidence, edited/reordered events, torn journal records, stale selections, duplicate JSON keys, missing cases, invalid statuses and concurrent writers fail closed.
- The .lock file may persist after a crash; operators must ensure no process is active and inspect evidence before manually deleting it.
- Source reports are never overwritten. The review state is not inserted into source rows. Journal entries are never silently deleted.
- Reviewer names/rationales are **plaintext** in local files. Users must not use prerelease code with confidential production financial data. This prototype does not implement encrypted-at-rest storage.

**Security limitation:** A plain SHA-256 chain is NOT cryptographically signed, cannot authenticate the reviewer, and does not prevent an attacker with write access from deleting or rewriting all history and recomputing hashes. For regulated or multiuser production workflows the product still needs external signed checkpoints, encrypted storage, robust lock recovery, retention/backup policy and legal review. This prototype does not constitute a secure evidence vault.

## Developer API

From the repo root, import read_cases, append_review, latest_states, export_register from the fvs_suite.exception_review module.

Example sequence:

    batch = read_cases("exceptions.csv", "grants")
    record = batch.cases[0]  # only flagged cases are returned
    append_review(
        "exceptions.csv", "grants", "exceptions.review.jsonl",
        case_id=record.case_id, expected_report_sha256=batch.report_sha256,
        reviewer="Example Reviewer", decision="needs_evidence",
        rationale="Obtain evidence to substantiate allocation and approval.",
    )
    state = latest_states("exceptions.review.jsonl", batch)
    export_register("exceptions.csv", "grants", "exceptions.review.jsonl", ".")

For procurement, specify product="procurement". A reviewer may record a subsequent action, but each action remains in the append-only event chain. A report modified since loading must be reopened and reviewed under a new journal.

## Validation status

- 18 independent, synthetic regression tests committed in products/desktop/tests/test_human_review_r7.py, including journal integrity, stale evidence, formula injection, concurrency lock, human rationale validation, and source preservation.
- Both premium packaged-EXE smoke paths extended to exercise review recording and sanitized register export. The free apps' smoke paths remain unchanged.
- **NOT YET VERIFIED:** complete repository tests, Windows packaged-executable CI, clean-machine GUI keyboard operation, AV/SmartScreen, premium licensing and gated download. Hosted GitHub Actions recently failed before executing any runner step; do not assume green checks until verified on the exact head SHA.
- Existing QD review and protected production publishing requirements remain mandatory; no public releases or premium downloads authorized.
