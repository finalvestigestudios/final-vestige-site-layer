# R480 — foreign-offset citation preflight consolidation (DRAFT / HOLD)

Date: 2026-11-16. Tracking: [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked strictly on R479 draft PR #2780 at `6f7e30097532da8941f9ca14bf536e66fd6d459e`; not production `main`.

## Actual code change

ProcureGuard Studio Pro's `cross_po_foreign_offset_source_rows` previously regenerated the complete set of original source rows for **every foreign PO/line** that referred to the same invoice or receipt identifier. It then rescanned those original entries again to expand the final report. For `S` original events and `F` foreign groups sharing one normalized identifier, that duplicated preflight input work `F` times before producing any evidence.

R480 computes the eligible foreign groups and unique validated original rows **once per normalized reference**, reserves `distinct_rows * foreign_groups` against the existing combined credit-plus-return citation budget, and only then materializes sorted evidence. It eliminates redundant source-list traversal and duplicate preflight validation; final report output remains inherently proportional to expanded citations. This is NOT an unbounded-memory defense, a new citation ceiling or a measured native-Windows speedup.

The same-PO-on-any-line suppression remains intact. Inputs, money amounts, original CSV byte digests, physical row citations, deterministic PO/line order and numeric source-row tie ordering do not change. The exception text for a bad row remains fixed and redacted. References remain flags and evidence only; **no payment, compliance or licensing decision is made automatically**.

## Tests, scope and limits

- New committed `products/desktop/tests/test_procurement_foreign_offset_fanout_r480.py`: 12 `unittest` methods. Includes preflight validation-count regression (30 foreign groups, one original source row => 31 sort-key calls total, one preflight + 30 final citations), duplicate rows, exact-budget pass/fail, combined credit+return budget failure, same-PO exclusion, normalized IDs, private error text, event type isolation, canonical sorting and 140 seeded reference-specification parity scenarios.
- **Local behavioral fixture only** (2026-11-16): isolated Python module containing this updated R480 resolver and `_source_row_sort_key`; **12/12 PASS** under normal `python -W error` and **12/12 PASS** under `python -OO -W error`, zero failures/skips. This was **not** the complete GitHub-committed module or end-to-end CSV application.
- GitHub workflow `.github/workflows/desktop-source-evidence-r385.yml` now requires both modes for the new test file, alongside inherited R479 source and real CSV integration tests.
- Full Python repository checkout, 16 R479 unit methods, 4 R479 CSV integration methods, 38 inherited ProcureGuard CSV cases, all-six engine regression and native Windows x64 executable validation **have not been run in this sprint**.

## Release governance

DRAFT / HOLD. No `main` merge, WordPress/site edit, executable, download link, license issuance or unrestricted premium artifact. Maintain local-only private finance processing, Decimal money safety, deterministic audit traces and human review. Windows Defender, keyboard/screen-reader accessibility, immutable checksums and premium entitlement-controlled downloads remain required release gates. Independent QD review and explicit founder approval are still required.

## Next highest-impact step

The repository/organization Actions administrator should inspect the actual run-banner error/annotations for the latest source and Windows workflows; check billing/spending eligibility, permissions and hosted-runner assignment. Restore *one job with real steps*, rerun this exact draft head and fix any failing inherited tests. Then run the six-engine matrix, native Windows x64 packaging and release safety gates before any QD/founder release decision.
