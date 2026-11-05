# R207 — CSV report header custody (DRAFT / HARD RELEASE HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on [R206 draft PR #1074](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1074), parent `559d44de3692fbb9cdcbb68f524b467c28c79e53`. Never target production/main directly.

## Reproduced defect and precise change

The shared `fvs_suite.atomic_reports.write_csv_report` sanitized **row cells**, but used `csv.DictWriter.writeheader()` to write **raw, unsanitized header labels**. A future dynamic or source-derived column label like `=HYPERLINK(1)` could therefore become an active spreadsheet formula even though the application supplied `engine.safe_cell`. Separate labels like `=SUM(1)` and `'=SUM(1)` could collapse to the same displayed heading after protection, obscuring column identity.

R207:
1. Materializes and validates plain-string, nonempty, unique source headers **before creating any staging file**.
2. Runs the same caller-supplied formula-protection callback against **every exported header** and continues to run it against every row value, including ignored extra columns.
3. Rejects non-string/empty/control-or-linebreak rendered headings and collisions **after** sanitization. It never silently merges ambiguous evidence columns.
4. Emits the safe header through the CSV writer, preserving original source-field keys for row lookup; retains BOM, fsync, exclusive non-overwriting publication and cleanup of partial files.

The actual desktop engine's `save()` calls this writer with `safe_cell`. R207 tests use a synthetic sanitizer to verify the writer's contract, not an end-to-end six-app packaging claim. No financial arithmetic, Decimal logic, premium licensing, audit approval workflow or source data is changed.

## Evidence actually executed (local Linux)

- CPython **3.13.5** in an isolated, minimal directory with source matching GitHub committed blob.
- Baseline before fix: R207 new suite **11 failures and 2 errors out of 14** — reproduces unsafe/raw headers and missing validation.
- After fix: **14/14 new R207 tests PASS** in normal Python and **14/14 PASS** under `-OO`.
- Existing exact R27 atomic export suite (with its expected header-callback order assertion updated): **11/11 PASS** in normal Python and **11/11 PASS** under `-OO`.
- **50/50 focused executions PASS** total (25 cases per mode), zero skips, Python compile PASS.
- Test fixtures are synthetic local temporary CSV files. Positive cases verify BOM and CSV roundtrip; negative cases verify no created report, no partial file, prior evidence untouched, and rejection of formula collisions, malformed headers, field subclass hooks and row-generator faults.
- Git blob identities, checked against local tested files:
  - shared writer `59af5aa1c6a57770844a3fef07693b01815fd969`
  - new R207 suite `42474f9e0649c81651e2874207c2f53909cfaa2e`
  - adjusted R27 suite `3e9d020f527771dd768fd4af49dbfa091d4db8fb`.
- Ubuntu `source-tests` and Windows `windows-build` now each have explicit R207 normal and optimized regression steps; Windows checks `$LASTEXITCODE`. **Configuration is not hosted execution evidence.**

## Remaining blockers and QD

R206's [Actions #42008016017](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42008016017) was completed/failure, with both jobs exposing no step records; root cause unverified. Restore GitHub-hosted runner execution (owner inspects Actions failure banner, billing/usage limits, workflow policy, and runner provisioning). Rerun **unchanged R207 head** and execute the full inherited desktop source suite on Ubuntu and Windows; verify the updated R27 legacy contract and the actual `engine.safe_cell` integration there. If platform behavior differs, fix on a new reviewable commit, never bypass tests.

The six Windows x64 candidate EXEs, native Windows 11/NVDA keyboard and high-DPI accessibility, checksums, Defender scan, code signing and protected premium downloads remain **unverified and unreleased**. QD independent review and founder approval remain required; no public executables, unrestricted premium file URLs, WordPress publishing or main merge.
