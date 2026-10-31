# R93 — Invoice Twin Scout source-row canonicalization (DRAFT / HOLD)

## Scope and defect

`candidate_pairs()` is a public, local-only invoice review API. The R92 predecessor validated canonical, unique physical CSV line positions, but **built duplicate groups in caller iterable order**. A direct caller passing the same verified records in a different order changed:

- the anchor and orientation of `exact_invoice_key` pairs;
- ordering of independent exact-key and same-vendor/same-amount candidate groups;
- presentation order and, because provenance hashes the ordered pair, downstream `candidate_ref` values.

Example: rows 4, 2, 3 with the same invoice key produced pairs (4,2) and (4,3); source-order canonical review should produce (2,3) and (2,4). This is a **review reproducibility issue**, not evidence of duplicate payment or fraud.

## Engineering change

`fvs_suite/invoice_match.py` now fully validates the bounded direct input and then **sorts validated records numerically by original physical CSV line**, before constructing the same exact-key and amount groups. The existing 200,000 source-record ceiling, 100,000 candidate ceiling, date-oriented near-match window, source-line citations, Decimal amounts, normalized IDs and human-review classifications remain unchanged. No original record mapping is modified; sorting uses only already-validated ASCII row numbers, never floating-point money conversion.

Canonical source iteration was already the normal file-import order, so this preserves ordinary CSV workflow ordering while making direct unsorted iterables deterministic. Cost: an additional O(n log n) sorting step and an in-memory list of up to 200,000 record references. Source content remains locally processed with no telemetry.

## Reproducible regression evidence

Added `tests/test_invoice_source_order_r93.py` with **15** unit tests: reversed source positions, numeric vs lexical line ordering, interleaved groups, **30 seeded input permutations**, date-ordered near matches, quoted-newline physical line gaps, equal Decimal representations, hostile Decimal context with traps, generator parity, immutable inputs, duplicate-line protection, candidate cap, record cap, and **25,000 reversed independent source rows**.

Local Linux x86_64 / Python **3.13.5**, an isolated exact-source workspace:

- **RED:** the same 15 tests against the R92 module yielded **7 failures**, demonstrating the defect.
- **GREEN:** **15/15 passed** against R93 in normal Python, **15/15 under `python -OO`**; `compileall` succeeded.
- Changed source Git blob **`d1befc13cdc248585a802dfb9ad8b0462220d1d2`** and test blob **`b17e9d4c0f01b1591da6ada58bc2a5d32e69e4c5`** were byte-matched with the actual tested local files after publishing to the branch.
- The isolated workspace uses a minimal `review.ascii_case_identity` stub; the modified `candidate_pairs` path does not invoke it. This is **not** whole-repository execution or native Windows GUI/EXE validation.

## Release and review boundaries

This R93 work is a stacked draft on R92, **not** `main`. No production site, WordPress, payment gate, binary, download, approval policy or release artifact was modified.

**HOLD:** full repository normal and optimized regressions, integrated Invoice Twin CSV→candidate→provenance run, actual Windows 11 x64 packaging/AV/smoke and keyboard/screen-reader review remain outstanding. Existing GitHub-hosted CI has been failing before job steps (tracked as issue #75), so isolated local passes must not be represented as a passing Actions job. No premium file should be placed on public unrestricted distribution.

**Next highest-impact action:** repository administrator restores one GitHub Actions runner with a visible executed step and log; rerun all source suites plus this test on the full checkout, then produce native Windows 11 x64 six-app build/smoke and independent QD/founder review. Keep all six tools **unreleased** until verified.
