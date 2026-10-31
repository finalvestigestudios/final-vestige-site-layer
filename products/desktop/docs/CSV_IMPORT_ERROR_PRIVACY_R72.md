# R72 — CSV importer diagnostic privacy (pre-release)

**Status:** development-only, draft PR stacked on R71. No Windows binaries, premium downloads, or production changes.

## Defect and scope

The shared financial CSV importer included a customer's raw source filename in several `ValueError` strings (missing/invalid file, bad header, ambiguous aliases, missing required columns, malformed rows, NULs and UTF-8/CSV parser failure). LedgerDiff Lite also emitted the filename for a blank normalized transaction ID. File basenames often contain client names, account identifiers or private case labels. This is an unnecessary disclosure risk if backend errors are logged, forwarded, or rendered by a non-GUI caller.

`csv_diagnostics.csv_input_error` produces a **closed catalog** of actionable, reproducible messages. It only formats an allowlisted internal field identifier, strictly validated integer column counts and physical CSV line references. Source paths, filenames, original headers, source values, private exception strings and unknown metadata are never interpolated. Parser exception causes are suppressed for diagnostic renderers. The common `engine.table` entrypoint and LedgerDiff's blank-ID check now use this catalog. The current UI already applies generic safe-message rendering; this closes a separate lower-level leakage path.

This protects the common CSV importer used by LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, GrantAudit Studio Pro, and ProcureGuard Studio Pro. Policy Delta Desk uses an independent text/CSV reader; its own R64 snapshot safeguards and error handling are unchanged.

## Audit / compatibility contract

- Preserve physical source rows, exact parsed bytes and SHA-256 snapshots, typed Decimal amount checks, normalized-key collision warnings and deterministic outputs.
- Preserve existing diagnostic substrings used by source integrity tests, including `invalid CSV header`, `blank or duplicate normalized CSV header`, `ambiguous 'amount' aliases`, `missing 'amount' column`, `malformed CSV record at physical line 2`, and `NUL character`.
- Do **not** promise caller-visible raw filenames or CSV original alias lists in errors; they must inspect their selected source locally if remediation is needed.
- No telemetry, networks, AI-driven adjudication, automated authorization, or modifications to original files.

## Tests and acceptance gate

Local Linux Python 3.13.5 isolated pure-module check: `PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_csv_diagnostics_r72.py' -v`, plus identical `python -OO` command and `compileall`, each must pass. The separate `test_csv_import_error_privacy_integration_r72.py` exercises the **real** five financial engines; it is source-committed but requires an authoritative full repository checkout/CI and cannot be counted as executed by the isolated module harness. Native Windows builds, GUI, entitlement, malware scanning and independent QD remain release gates. Do not publish artifacts until those pass.

**Next highest-impact step:** fix Actions runner-start issue #75, execute complete normal/optimized source suites plus the new real-import tests, then native Windows 11 x64 smoke and accessibility verification of all six applications under independent QD/founder approval.
