# R362 — SpendMap Direct-Source Field Cardinality Custody

**Status:** Draft engineering increment for [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). No approval, merging, publishing, or executable release is implied.

## Reproduced resource gap

R361 bounds total UTF-8 field text to 64 MiB, at most 64 columns per record and 200,000 records. Those limits alone do **not** bound Python dictionary and analysis bookkeeping allocations in proportion to bytes: 200,000 records containing 64 tiny/empty columns can hold **12,800,000 fields** and still fit under a 64 MiB field-text budget (2 bytes of framing plus compact keys/empty values). Per-dictionary allocation, copying, and report metadata can dominate input byte size. This is a memory availability risk, not a known compliance misclassification or evidence forgery.

## Change

- In the already-wired `SpendSourceBudget.attest` preflight, charge the **number of native dictionary fields**, including empty values and unused columns, to a report-scoped `MAX_SPEND_SOURCE_TOTAL_FIELDS = 2_000_000` limit.
- Check cardinality before encoding, callbacks, or yielding verified rows; reject with a private-value-free error when the limit is exceeded.
- Advance both field and UTF-8 counters *only* after a complete row passes validation. Failed rows do not consume either budget.
- The existing 64-column/row, 1,048,576-character/cell, 64 MiB UTF-8, 200,000-row, original source/date/Decimal, provenance and callback protections stay in force. Default cap supports 200,000 rows with an average of **10 columns**; wider large exports may now be explicitly rejected rather than risking large memory consumption.
- Input records and source evidence are not modified; no telemetry, networking, compliance auto-approval, payment processing, or premium distribution changes.

## Tests and gates

- `test_spend_source_field_budget_r362.py`: 16 focused methods (exact and overflow limits, many empty cells, counters transactional, UTF-8 and text-cap failures, native dictionary boundary, privacy, Unicode, and report isolation).
- `test_spend_source_field_engine_integration_r362.py`: 6 actual `validated_spend_rows` / `summarize_spend` / CSV `spend_map` regressions requiring the whole checkout.
- Workflow `desktop-build.yml`: Ubuntu and Windows normal/optimized Python runs of both files (eight explicit commands).
- Isolated local Linux CPython tests passed **41/41 normal** and **41/41 optimized (`-OO -W error`)**, **82 focused executions** (25 inherited R361 + 16 new R362). Exact locally tested helper and both unit test files match GitHub blob SHAs: `50f3c052820234a4ae2eed5cdfc0229c43a04f31`, `aaea33eaeff310d9de31ab244bce47bdb4de72f8`, `aff9864c7bf39a945bc6bb15e5d50d45b3e7a130`. The new integration test file (`c0bd5c182e367de21aed801cfb2830d2879d2346`) was locally compiled, **not executed** with the engine.
- **Not yet validated:** whole-repository integration tests, all other suite tests, Windows runner, executable build, antivirus, accessibility, QD and founder acceptance. Do not represent test files being committed as passing tests.

## Next high-impact step

Restore GitHub Actions job execution (both Ubuntu/Windows jobs have repeatedly failed before runner steps). Run the complete inherited desktop test suite, R361/R362 integration, all 22 authentic AES-GCM cases, then Windows 11 x64 native packaging and smoke verification for all six distinct utilities. Do not publish binaries or unlock premium downloads before QD and founder gates.
