# Final Vestige Labs R165 — Invoice Twin immutable input ownership

**2026-11-03 · tracks issue #73 · engineering draft / release HOLD**

## Defect and threat model

`candidate_pairs(records)` is a public, reusable local Invoice Twin Scout engine that accepts any iterable of validated financial records, including generators. Before R165, `_validated_records` yielded the *caller's dict itself*, then the engine materialized and sorted the yielded objects. A memory-efficient importer/third-party caller can legitimately rewrite the **same dict** and yield it repeatedly. Previously all saved references then reflected the **last** row, even though each prior physical row, exact Decimal value, invoice identity, and date was independently validated when yielded. This can fabricate candidates, hide real duplicates, duplicate physical row citations, and misdirect audit evidence. A caller could also mutate source dictionaries after `candidate_pairs` returned, changing a saved review pair.

## Fix

`fvs_suite/invoice_match.py::_validated_records` now yields a **fresh shallow copy after validating each record**. The relevant established fields (physical row, normalized vendor and invoice identities, parsed calendar date, exact finite Decimal amount, original text vendor and invoice labels) are ordinary immutable values in the importer. The engine therefore consumes a per-yield snapshot rather than retaining an alias to a caller-owned mutable mapping. No source importer, CSV schema, report encoding, amount rounding, 7-day default, candidate limit, human review rule or premium entitlement is changed.

**Boundary:** This fixes cooperative caller dict reuse and later mapping edits; it does **not** authenticate arbitrary direct-API input, defend against hostile in-place races on user-defined mutable values, prove an original invoice genuine, decide fraud, or approve payment. The original source-file SHA-256 and physical CSV row references remain essential audit evidence.

## Regression and acceptance

`tests/test_invoice_snapshot_r165.py` adds 20 synthetic-only methods covering two/three record mapping reuse, exact and near matches, cross-vendor and cross-amount isolation, source-row anchor order, distinct source labels/reviewer flags, independent result identity, post-call mutation, source SHA-256 provenance stability, precise eight-place Decimal amounts, hostile ambient Decimal contexts, duplicate/invalid physical lines, candidate cap, empty input and original-list preservation.

Run from the repository root:

```shell
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r165.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r165.py
```

PowerShell: set `$env:PYTHONPATH="products/desktop"` and run the two Python commands above. The strict runner rejects missing, skipped, duplicate, renamed or unexpected methods, while suppressing private exception details. The internal desktop CI gates both Ubuntu and native Windows for normal and `-OO` execution (**20 × 2 × 2 = 80 planned R165 method executions**), in addition to inherited six-app source tests and Windows x64 internal packaging.

## Release and operations

This change remains on an isolated branch / draft PR stacked on R164. Do not merge into `main`, publish executable downloads, expose unrestricted premium binaries, or call successful CI a physical Windows 11 accessibility assessment. All six apps remain **UNRELEASED** pending 46 independent real Windows 11 observations, genuine Defender/EDR checks, code signing, protected premium delivery, QD review and founder authorization. No client financial records, telemetry or network upload are introduced.
