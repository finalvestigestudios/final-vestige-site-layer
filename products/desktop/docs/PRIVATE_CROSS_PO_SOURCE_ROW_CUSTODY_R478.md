# R478 — Private cross-purchase-order source-row parsing (internal; release HOLD)

Issue: #73. **DRAFT stack on R477**, never production `main`. Independent QD plus explicit founder approval required before merging or publishing.

## Defect and functional correction

Before R478, the ProcureGuard cross-PO helper sorted candidate source-row citations with `int(row)` after materializing evidence. A direct caller with a nonnumeric row such as `PRIVATE-CUSTOMER-ROW` caused a Python `ValueError` containing that raw private label. Extremely long numeric labels could also trip Python's integer-string conversion limit. The normal CSV parser already uses bounded physical-row indices; this closes the **shared helper's direct-call/error/privacy boundary**, not a claim that ordinary CSV files contain these labels.

`_source_row_sort_key` now accepts only native Python text of 1–10 ASCII decimal digits and emits a fixed, redacted `ValueError` for invalid values. The shared `_reserve_citation_budget` validates every source row of a qualifying cross-PO document during **all-type preflight**, before calling `_materialize_index` for any type, including when an earlier type's data is otherwise valid. Typed legacy wrappers use the same guard. Leading-zero numeric spellings remain accepted for backward compatibility with R477's deterministic numeric/text tie-break test; no normalized row is substituted into the report.

No original financial CSV bytes, source SHA-256, Decimal arithmetic, document keys, event classifications, PO balances, audit citations for valid data, or human-review decisions are altered. No telemetry or external API is involved.

## Artifact/verification inventory

- Production helper: `products/desktop/fvs_suite/procurement_cross_po_r471.py`, local candidate Git blob `887641e1d87cdd74502192ddbc2d53a029af1190`.
- New tests: `products/desktop/tests/test_procurement_cross_po_private_rows_r478.py`, local candidate Git blob `ee7d24f6cca6c45b68c0e1c765540e98cfb36143`.
- Existing R477 regression: `products/desktop/tests/test_procurement_cross_po_canonical_r477.py`, verified existing Git blob `fadb587ef2c1fb3f8e4ea0e31bcedf5fd0dee972`.
- CI workflow: `.github/workflows/desktop-source-evidence-r385.yml` now explicitly invokes the R478 tests in standard and optimized Python on Ubuntu and Windows runners. No release artifact uploaded by that workflow.

### Executed local evidence (Linux, Python 3.13.5)

1. Rebuilt the **exact byte-identical R477 helper** locally: `git hash-object` matched GitHub's parent blob `82e2cba446602c75a989fbfe3a482e6aaf999c18`.
2. Replaced only the three precise R478 helper sections; local Git blob `887641e1d87cdd74502192ddbc2d53a029af1190` matched GitHub committed source on branch.
3. Wrote 14 new unit methods and verified their Git blob `ee7d24f6cca6c45b68c0e1c765540e98cfb36143` against GitHub committed test.
4. Combined **R477's 8 exact-source tests plus R478's 14**: `22/22 PASS` using `python -W error -m unittest discover` and `22/22 PASS` using `python -OO -W error -m unittest discover`: **44/44 executed methods, zero skips**. R477's seeded 125 input permutations and 8 distinct child-process hash seeds passed in both modes.
5. Candidate Python `py_compile` and `compileall`: PASS.
6. Negative control: reverted local helper to byte-identical parent `82e2cba446602c75a989fbfe3a482e6aaf999c18`; the new R478 suite exited nonzero with **19 reported failures including subtests**. Direct unmocked parent repro raised `ValueError` with a private row label in its message; candidate raised a fixed redacted `ValueError`, without that label. This establishes change sensitivity, not a full-app security audit.

### NOT tested or approved

The **full 38-method ProcureGuard CSV integration suite**, the legacy R475/R476 helper test files, complete six-app regression suite, native Windows x64 packaged executables, Defender/screen-reader/keyboard accessibility, SHA256 distribution/entitlement and live premium delivery **have not been executed in this local slice**. Passing helper unit tests are not Windows release certification. GitHub Actions has repeatedly failed with `steps=null`; the underlying infrastructure cause remains unconfirmed. No files were published and no premium binaries were exposed.

## Owner/next action

Repository/org administrator: inspect Actions run failure annotations, billing/spending eligibility, hosted runner assignment and workflow permissions. Restore runnable CI on this **exact R478 head**, run its new tests plus the complete 38-method ProcureGuard CSV suite and the full six-app regression matrix. Only after green CI and independent QD/founder approval proceed to native Windows packaging, checksums, Defender, accessibility and gated premium distribution.
