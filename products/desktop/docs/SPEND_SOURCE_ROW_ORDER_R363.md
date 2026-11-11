# R363 — Deterministic SpendMap Physical-Row Citations

**Status: draft engineering only.** Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73); no release, merge, QD approval, founder approval, or premium download exposure.

## Defect and scope

The R362 SpendMap input boundary intentionally accepts direct API `list` records in any order, including valid out-of-order numeric physical CSV row coordinates. In `summarize_spend`, bucket `source_rows` was populated in that arbitrary input order, even while `vendor_month_evidence_rows` and its SHA-256 membership fingerprint were sorted. For the same already-verified source facts, rows `10,2,9` displayed `10;2;9` while the equivalent permutation showed `2;9;10`. Reviewers could see different physical-citation sequences without any difference in money, source digest or source membership.

## Implemented safeguard

- A scoped `canonical_spend_source_rows` helper requires a native list of native strings, canonical positive 2–10-digit physical CSV record-start rows, uniqueness and the 200,000-row envelope; it sorts by integer coordinate (not lexicographic string). It emits safe generic errors with no private input echo.
- The real SpendMap summarizer calls the helper **only when presenting the existing per-vendor/month/category `source_rows` string**. The report schema, row set, membership fingerprint, totals, exact Decimal arithmetic, review flags, source labels, originals and callback input order remain unchanged.
- This improves **presentation determinism**. It does not authenticate arbitrary direct-call SHA-256 values or claim that a reviewer should approve a transaction.

## Evidence and limitations

- `test_spend_source_row_order_r363.py`: 21 synthetic standard-library methods for numeric sorting, all 24 permutations of 4 lines, source immutability, duplicate/malformed/Unicode/subclass rejection, capacity, privacy and repeatability.
- `test_spend_source_row_order_engine_r363.py`: 8 complete-engine test methods for bucket grouping, direct-input permutations, source immutability, precision and rejection. Require repository checkout and have **not yet been executed** by the isolated local harness.
- Linux Python 3.13.5: 21/21 focused helper tests passed with `-W error`, and 21/21 with `-OO -W error` (42 separate test executions). No native Windows executable, 22 AES-GCM cases, CI job or full-suite pass is inferred from those focused results.
- Ubuntu and Windows source CI now run both test modules in normal and optimized mode. Existing runner provisioning failures can still prevent those checks from executing.

## Next validation

Restore real Ubuntu/Windows Actions job allocation; run the new 8 engine tests, inherited desktop regressions and 22 genuine AES-GCM integration cases; perform physical Windows 11 x64 six-app packaging, Defender, keyboard/screen-reader, SHA-256, signed/unsigned disposition, and independent QD + founder acceptance before any catalog publication or premium download.
