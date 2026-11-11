# R344 — ProcureGuard native row storage and physical citation grammar (DRAFT / HARD HOLD)

**Scope:** ProcureGuard Studio Pro (premium), six-app Labs issue #73. This branch is stacked **only** on R343 draft PR #1983 at exact commit `9347ab7371633e0f53eeedd83dacf72e5d7371d7`; it is not based on production main. QD independent review and founder authorization are required before merge, packaging, premium delivery or website changes.

## Verified boundary and correction

R343 validates document text before normalization, but its `review_line` preflight still invokes `row.get(...)` directly, and subsequent Decimal and identity logic invokes `row[...]` on caller-supplied mappings. Direct Python callers may pass a `dict` subclass whose virtual methods lie about actual stored quantity, price, reference, event type or physical row and/or throw an exception containing a private client path. `offset_source_line_links` likewise read virtual views and accepted arbitrary `row` labels into provenance JSON.

R344 snapshots **actual dictionary storage** of all PO, invoice and receipt rows before **any** conversion, callback or display in `review_line`, and snapshots every offset-link row before event classification. Existing `event_custody.snapshot_event_record` bypasses overrideable `dict` methods, validates native text field names, and returns ordinary private dictionaries. The new helper enforces an exact native `list` outer container before walking it. Original inputs are never mutated. This is defensive API validation; **it does not authenticate direct-caller input**.

The offset citation path now validates every stored `row` value as exact built-in ASCII decimal with no leading zeros, number >=2 and <=10 digits, matching the existing `procurement_input.event_kind` error-citation grammar. Nonnative objects, control/Unicode digits and malicious subclasses are rejected without invoking conversion hooks or exposing private file paths. Source-line values from parsed CSV (including physical positions after multiline records) remain unchanged. **A syntactically valid fabricated row number is not proven genuine**; immutable CSV snapshot hashes are the authoritative provenance boundary.

Exact Decimal arithmetic, R343 identity normalizer custody, human-review flags, local-first processing, offline-only behavior and the six-suite QD/production hold remain unchanged.

## Artifacts and executed evidence

- `fvs_suite/procurement_native_rows.py`: new native storage and citation grammar helper.
- `fvs_suite/procurement.py`: all three `review_line` streams and the `offset_source_line_links` stream are copied before access; output structure preserved.
- `tests/test_procurement_native_rows_r344.py`: **36** adversarial unit methods.
- `tests/test_procurement_native_row_integration_r344.py`: **18** genuine ProcureGuard review/citation integration methods for Decimal totals, source rows, mismatched reference and forged views.
- `.github/workflows/desktop-build.yml`: Ubuntu/Windows must execute both R344 suites under normal and `-OO` Python *before* private Windows packaging, in addition to R343 and inherited regressions.

**Actually executed locally:** isolated `fvs_suite.event_custody` and `fvs_suite.procurement_native_rows` using the exact helper and test Git blobs. Linux CPython 3.13.5: `python -W error -m unittest discover -s tests -p 'test_procurement_native_rows_r344.py'` **36/36 PASS**; `python -OO -W error -m unittest discover -s tests -p 'test_procurement_native_rows_r344.py'` **36/36 PASS**, 72 focused method executions total, zero skips. `py_compile` PASS for both helper and integration test source. `event_custody.py` on disk matched prior Git blob `b78a78c79ee83b39dfe506909c6867f2d88eafdc`. Local helper Git blob `f858ab5993eee81c2d460a7d22fa56c8ef25cd2d`, unit suite Git blob `dd67411935e0a448095f4b0cbe42ab31210764ec`, integration syntax-only blob `52af6510177e245888aacfacff8c729474731a47`, all independently matched the new branch via GitHub fetch.

**Not executed:** modified `procurement.py` in a complete checkout, the **18 real integration methods**, entire inherited procurement regression set, **22 genuine AES-GCM integration cases**, hosted Ubuntu/Windows CI, or real Windows 11 x64 executables. Do **not** interpret `py_compile` as functional proof of real-engine tests. R344 is a draft candidate pending those gates.

## Required release gates and rollback

1. Unblock GitHub Actions job provisioning, inspect the failed check-run annotations and obtain real step-level Ubuntu and Windows logs.
2. Execute full desktop test discovery including R342/R343/R344, verify R344 integration behavior on actual data boundaries (no customer data required), normal and `-OO`, plus 22 AES-GCM cases.
3. QD review source/raw snapshot consistency and examine any existing direct-call clients that intentionally pass non-list streams; if incompatible, explicitly adapt client at controlled boundary rather than relaxing the fail-closed default.
4. Privately build/smoke six Windows x64 executables, scan with Defender, verify SHA-256 manifests, accessibility and protected premium entitlement delivery.
5. Founder authorization and separate site approval before production merge or any download publication.

No main merge, website changes, public EXEs, unrestricted premium assets, payment approval, compliance determination, network transmission or release has occurred.
