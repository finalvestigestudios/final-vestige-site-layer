# Final Vestige Labs R482 — shared cross-order numeric source-row key cache

**State:** DRAFT / QD + founder HARD HOLD / source-only. Parent: R481 draft PR #2787,
exact parent `553dfb1a02dd67b90c7c91bc1b47c6472d786686`. Tracks issue #73.
Never merge into production, ship portable Windows x64 EXEs, expose premium downloads,
change WordPress, issue licenses, or state compliance determinations without
independent QD and explicit founder approval.

## Actual engineering change

`procurement_cross_po_r471.py` now caches the validated immutable
`(int(row), len(row), row)` key during the conservative citation-budget preflight,
and reuses it when rendering cross-PO evidence. The same row spelling is only
parsed once across the **four** typed invoice, credit, receipt and return streams
and across overlapping document references and affected PO/line groups. The
legacy typed index wrappers share the same optimization. This extends the
R481 foreign-offset cache to the original-document cross-PO evidence path.

All four types must reserve within the shared 1,000,000-citation limit before
**any** evidence expansion. The cache is local to one function invocation.
Its key is the original text, not numeric equivalence: `2` and `02` stay
distinct, sorted `2`, `02`, `10` when applicable. If a caller bypasses
preflight or changes a mapping between stages, materialization falls back to
the fixed privacy-safe numeric validator instead of a potentially sensitive
`KeyError`. Non-native source-row objects fail redacted validation **before**
their custom hash method could run. There is no disk persistence or network I/O.

## Measurable, scoped proof

A local functional **reconstruction of the affected helper functions**, not
the entire byte-identical committed module, passed **12/12** Python 3.13.5
`-W error` unittest methods and **12/12** optimized `-OO -W error` methods.
The same new test file was committed and its Git blob hash matched the local
test file. The **committed module plus test file have not run together**;
GitHub-hosted/full-application/native-Windows results remain unverified.

The 12 methods exercise 220 seeded four-type parity scenarios per mode
(880 kind-specific oracle comparisons per mode), stable leading-zero source
row ordering, same-PO suppression, overlapping references, input immutability,
privacy-redacted invalid rows, no partial output after later-type failures,
and exact-bounded citation reservations. Instrumented reconstructed-helper
calls for one ID across 30 POs: **31 numeric validations before R482 vs 1
after**. Four document types sharing the same spelling: 1 validation after
R482. The 25-PO legacy typed wrapper also has 1 validation after R482.
These are *call counts*, not measured speedups or Windows benchmark results.

## Reproduce on an authorized checkout

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_procurement_shared_row_key_cache_r482.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_procurement_shared_row_key_cache_r482.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_procurement_integration_r5.py
```

The source-evidence workflow requests normal/optimized R482 native test runs on
Ubuntu and Windows. It is not a substitute for Windows x64 executable
packaging, actual installed UI/accessibility tests, Defender scans, checksums,
premium authorization checks, or verified customer download links.

## QD review checklist and next highest-impact step

1. Restore GitHub Actions **step execution** (past R481 exact-commit
   Windows #43956611162 and source #43956611221 failed with `steps=null`).
   Repo administrator: inspect workflow run annotations, account billing and
   runner assignment. The root cause has not been confirmed.
2. Execute the committed R482 tests on the exact PR head in normal and
   optimized modes; run inherited R475–R481 tests and the actual 38-method
   ProcureGuard CSV integration suite, then the complete six-app matrix.
3. Independently verify local-only processing, Decimal-safe money, original
   source SHA-256 custody, deterministic evidence, redacted error chains and
   human-only review flags; require explicit QD and founder approvals.
4. Only after successful Windows builds: verify the actual portable x64
   binaries, accessibility, Defender scan, file SHA256, entitlement enforcement,
   and separate premium download access gates. No binary or link is released
   by this sprint.
