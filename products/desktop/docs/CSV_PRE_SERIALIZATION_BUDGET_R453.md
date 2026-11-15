# Labs R453 — bound CSV row serialization *before* allocation

**Issue:** #73 · **Parent:** R452 draft PR #2633, commit `d02e45663e65b6c706bac879f6e3d8294220e7b4` · **Status:** DRAFT / RELEASE HARD HOLD. Never publish executables or bypass QD.

## Concrete resource-safety defect

All six standalone desktop utilities share `fvs_suite.atomic_reports` for local financial CSV reports. Before R453, `_BudgetedCSVTextSink.write()` limited actual on-disk bytes to 64 MiB including the UTF-8 BOM. However, **CPython `csv.writer.writerow()` first constructs the full serialized row in memory, then calls `write()`**. A direct API call with 256 allowed cells, each as long as 1,048,576 characters, could therefore induce a large temporary serialized string (and quote doubling) before the existing byte limit rejected publication. This is a bounded-memory issue; it is not evidence of a real-world exploit or a confirmed Windows crash.

## Implementation

- Added `_BudgetedCSVTextSink.preflight(values)`: subtract exact encoded UTF-8 lengths of sanitized visible fields from the **current** remaining file-byte budget. Reject if the lower-bound total cannot fit. This does **not** mutate the sink budget.
- Check headers and every row **before** invoking the native CSV serializer. Only columns included in the exported report affect the lower bound; extra fields still undergo the existing sanitizer.
- Preserve the exact subsequent `write()` byte calculation, which still accounts for BOM, separators, CSV quoting, escape expansion and CRLF line endings. Thus borderline records can be accepted or refused as before, but oversized impossible records cannot enter `writerow`.
- No source files are changed; no truncation or partial final report; no automated compliance decisions; no edits to Decimal-safe calculations, audit trails or local-first privacy controls.

## Evidence, 2026-11-15

**Source artifacts:**
- Production `products/desktop/fvs_suite/atomic_reports.py`
- `products/desktop/tests/test_csv_serialization_preflight_r453.py` — **11 new regression methods**: header and first/second-row allocation guards, current-budget tracking, multibyte UTF-8, exact final-byte success/fail boundary, quote-expansion enforcement, ignored-extra formula checking, negative financial amount fidelity and existing-output no-overwrite.
- Both workflow files `.github/workflows/desktop-source-evidence-r385.yml` and `.github/workflows/desktop-build.yml` explicitly run the R453 tests in standard and `-OO` mode, including Windows before packaging.

**Local execution limitation:** The private GitHub repository could be inspected and updated using the GitHub connector, but it was **not clonable by the isolated Linux shell** (network DNS refused). We executed a manually reconstructed projection of the changed sink + real CPython `csv.DictWriter`, UTF-8-BOM output and synthetic temporary files using Python 3.13.5: **11/11 PASS standard; 11/11 PASS optimized**. Removing the preflight in the same projection caused **four of four allocation-order regressions to fail**, showing the focused checks discriminate the changed behavior. This is **not** a claim that the committed full-module regressions or a real Windows executable ran. Python source CI and Windows job execution are mandatory.

## Release and next action

The six apps remain separate: four free (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and two gated premium (GrantAudit Studio Pro, ProcureGuard Studio Pro). No downloadable EXE, premium artifact, license, or site changes occur in this sprint.

**Blocker inherited from R452:** workflow runs #43727206681 (source) and #43727206701 (Windows build) reported failed jobs with **zero recorded steps and no runner assignment**. The cause cannot be inferred from that alone. Restore GitHub Actions runner/account eligibility by checking repository/owner billing, spending limits, Actions policy and workflow/job annotations. Then execute this branch's full six-app source regressions and native Windows x64 packaging, Defender, keyboard/accessibility, SHA-256 and protected premium distribution gates. **Independent QD signoff and explicit founder authorization are required before release or production merge.**
