# R360 — SpendMap per-report vendor normalization custody

**Status:** DRAFT, QD + founder HOLD. This does not authorize release, supplier verification, financial approval, or a compliance finding.

## Reproduced code-path weakness

`validated_spend_rows` calls a user-supplied `normalize_vendor` for every row. Before R360, the same original vendor could produce a different accepted ASCII key on a later callback invocation, e.g. `ACME` on CSV physical row 2 and `OTHER` on row 3. Every individual key passed lexical validation, so the report silently split the vendor into distinct month/category buckets and potentially concealed an offset or spend spike. Similar discrepancies could affect source-equivalent ASCII-case and ASCII-boundary-space variants. The original rows and source SHA remained unchanged, obscuring the issue.

## Exact change

- A per-report `SpendVendorSession` maps ASCII-case-insensitive, ASCII-boundary-whitespace-trimmed **original** vendor labels to the first validated normalized key.
- Each later normalization of that source-equivalent label must produce the **same key**. A mismatch raises a sanitized `ValueError` with only the already-validated physical row number, before `validated_spend_rows` yields even one row or `summarize_spend` builds a report.
- Unicode distinctions are retained: NBSP (U+00A0), figure space (U+2007), narrow NBSP and non-ASCII case variants are **not** folded. R358's independent normalized-vendor collision flags continue to surface distinct original labels when those labels share a matching key.
- Session state is constructed for each source-call invocation. It does not cross customers, reports, calls, files or runs. Strict builtin `str` checks prohibit user-defined string operations.
- Normal CSV processing using deterministic native `key`, exact Decimal money, original-source date custody and source rows remains unchanged. No telemetry, source mutation, automated legal/compliance conclusion or premium access change.

## Artifacts

- `products/desktop/fvs_suite/spend_vendor_session_r360.py`: source-equivalent identity ledger and fail-closed check.
- `products/desktop/fvs_suite/spend_input.py`: real direct-summarizer input boundary wiring after lexical validation, before any report rows can escape.
- `products/desktop/tests/test_spend_vendor_session_r360.py`: **20** focused synthetic methods.
- `products/desktop/tests/test_spend_vendor_session_engine_integration_r360.py`: **13** full-checkout integration methods (direct caller, actual summarizer and CSV engine).
- `.github/workflows/desktop-build.yml`: **8** mandatory targeted commands (Ubuntu and Windows, normal and `-OO`, focused and integration).

## Verification and limits

The standalone R360 helper and its 20 focused tests were run on **Linux Python 3.13.5** with `PYTHONPATH=.` and `-W error`: **20/20 PASS normal; 20/20 PASS `-OO`** (40 method executions). Byte-for-byte committed Git blob hashes for the helper and focused test files were compared with the local executed files. The additional integration module was syntax-checked locally but **not run against the real repository**. The edited `spend_input.py` path, other inherited tests, six packaged Windows x64 binaries and all 22 authentic AES-GCM cases are **not validated** by the local helper run. Existing GitHub Actions jobs have failed before receiving a runner; do not imply application-test failure or success.

## Remaining hard gates

Restore hosted Ubuntu/Windows runner assignment and inspect exact failing check annotations; run the complete desktop suite including all 13 R360 real-engine tests and inherited R342–R359 / AES-GCM coverage. Verify native Windows 11 x64, PE signatures/checksums, Microsoft Defender scan, offline/local privacy, GUI keyboard/scale accessibility, premium license/access control and safe site download paths. Independently review in QD and obtain founder approval **before merge or publishing**.
