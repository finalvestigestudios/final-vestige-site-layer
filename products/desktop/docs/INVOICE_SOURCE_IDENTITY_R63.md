# R63 — Invoice Twin Scout: verifiable source snapshot and candidate references

Status: **source-only development candidate, not released**. Applies only to the free Invoice Twin Scout app. No changes to premium credentials, payment, downloads, telemetry, or WordPress.

## User-facing defect and behavior

Previously invoice candidate exports cited physical CSV rows but not the exact source version from which the matches came; regenerating after a source edit could silently change results. Now the importer requests `(records, source_sha256)` from the existing descriptor-verified CSV snapshot. It never reopens the source path to compute that digest. Each candidate appends exactly two columns to the existing 13-column report, in order:

1. `source_sha256`: lowercase SHA-256 over exact imported CSV bytes (includes BOM, newlines, unused columns and whitespace).
2. `candidate_ref`: SHA-256 over a domain-separated encoding of the source SHA-256, physical `row_a`, `row_b` and deterministic status (`exact_invoice_key` or `review_possible_duplicate`). No supplier name, account, amount or invoice number is serialized directly into this reference.

The candidate identifier is stable when the same file bytes and candidate classification are supplied again, even if the output report filename/timestamp changes. Different file bytes produce different source identity and candidate references. The exact 13 existing columns, Decimal-safe amounts, date-window matching, cap of 100,000 candidates, original label/collision flags, physical source rows, CSV spreadsheet-formula protection and atomic report writer are unchanged. An unsupported status, invalid digest, repeated identical candidate reference or malformed physical source line fails closed **before** the report is written.

**Interpretation:** A hash is a reproducible *byte identity*, not an authenticated signature or evidence of a vendor's identity. A candidate reference is a review locator, not a fraud finding, compliance determination, reimbursement approval, or proof a duplicate payment occurred. Human review is required. Source inputs remain offline and unmodified; no telemetry or cloud submission.

## Reviewer verification

1. Export the original input CSV intact and retain it in approved secure storage. Obtain its SHA-256 with a trusted independent tool such as Windows PowerShell `Get-FileHash -Algorithm SHA256 <file>`; compare to every nonempty report row's `source_sha256`.
2. Trace `row_a` and `row_b` to physical CSV record-start lines; multiline quoted fields may span more than one physical line. Verify normalized vendor/invoice key and amount/date review flags against the retained original.
3. Two generated reports over *identical bytes* should contain identical candidate references, while an edited CSV (including line-ending differences) changes them. The reference does **not** authenticate the retained source; independent custody and human evidence review remain necessary.
4. **Limitation:** With zero review candidates the CSV contains only headers, so no per-row source hash is present. Do not claim the header-only report proves which empty or unmatched source file was checked. A separate always-present evidence sidecar is a future enhancement with its own atomicity and release-gate tests.

## Test and release gates

- Focused pure tests: `python -W error -m unittest -v tests.test_invoice_provenance_r63` and `python -OO -W error -m unittest -v tests.test_invoice_provenance_r63`.
- Engine/CSV tests on a **trusted complete checkout**: `python -W error -m unittest -v tests.test_invoice_source_engine_integration_r63` and repeat under `-OO`. Verify physical CSV lines with BOM/quoted newlines, stable/changed fingerprints, source replacement after snapshot, candidate cap no partial output, and collision review.
- Full offline source gate normal and `-OO` for all six apps, Windows 11 x64 PyInstaller builds, all six packaged smoke runs, AV/SmartScreen, keyboard/screen-reader testing, checksums, entitlement-gated premium distribution, and independent QD/founder approval remain REQUIRED before any release. This patch is not a release authorization.

If GitHub Actions jobs continue failing before a runner starts (tracked in #75), do not describe those runs as passing or failing app tests. Use a trusted full local checkout or restore runner allocation. No private financial data should enter CI fixtures or logs.
