# Labs R214 — serialized CSV byte and cell capacity custody

**2026-11-05 UTC — DRAFT / QD HOLD / NOT FOR RELEASE.**

Parent: R213 `f2bc99059be3f4f6bc5ac8e5d5d0cc4b6658b72a` (draft PR #1121). Feature branch: `feature/labs-r214-bounded-csv-bytes-20261105`. No main/WordPress changes, no downloadable executable, and no premium payload publication.

## Reproduced problem and mitigation

R213 capped report rows (200,000) and fields (256), but accepted arbitrarily long per-cell text and never bounded the **on-disk CSV byte count**. The combination can still fill a disk or cause a very large report even with legal schema/row counts. Quoting, embedded delimiters, CRLF and multibyte UTF-8 make raw character counts an inaccurate proxy for output size.

R214 adds a **1,048,576-character cap per rendered, sanitized cell** (including header labels and sanitized-but-ignored extra row fields). It also wraps the underlying CSV writer in a bounded text sink that counts the **final serialized UTF-8 bytes** of each CSV record, including quoting and line endings, and reserves the three-byte UTF-8 BOM. A report **larger than 64 MiB (67,108,864 bytes)** fails before the overflowing write. At exactly the budget, it succeeds. Larger workloads require deliberate operator-reviewed report batching; no silent truncation or automatic splitting.

The writer still stages files in the destination folder, flushes/fsyncs, and publishes without overwriting existing evidence (exclusive link on POSIX, non-replacing rename on Windows). Limit errors use fixed strings that exclude customer identifiers; no telemetry or uploads. The shared financial engine's Decimal logic and human approval boundaries are unchanged.

## Reproducible local test evidence

Tested against a **local source reconstruction with exact Git blob identity** to branch files, using synthetic fixtures only, Linux CPython 3.13.5. The original parent R213 `atomic_reports.py` was Git blob `b266cc29ae5e3186e3804d78c2593880ae02d044`. On that parent, the new R214 suite was **RED: 17 cases, 10 failures + 3 errors** (four tests passed). After patch: production source blob `1356f6e0b4f102d8640295fca04141b4b6afa628` and R214 test blob `298c969bf5809533fc1b1d0a87d85341836b64f8` both matched committed GitHub blobs byte-for-byte.

Executed locally with `PYTHONPATH=.` and `-W error`:

```sh
python -W error -m unittest discover -s tests -p 'test_atomic_*.py' -q
python -OO -W error -m unittest discover -s tests -p 'test_atomic_*.py' -q
python -m py_compile fvs_suite/atomic_reports.py tests/test_atomic_byte_budget_r214.py
```

Result: R214 **17/17** + unchanged R213 **15/15** = **32/32 normal**, **32/32 optimized (-OO)**; **64/64 focused test-method executions**, no skips, compilation PASS. The inherited R213 test blob was independently matched to GitHub `e1abe29b44291ca08a2840255d45a632290bf31d`. R213's full 200,000-row acceptance and 200,001-row rejection were actually exercised in both modes (~3 seconds per mode). The R214 suite covers exact-byte threshold, one-byte-over rollback, BOM, UTF-8 emoji, CSV escaping/multiline values, zero-row reports, late failure, prior-evidence preservation, no extra generator consumption, ignored-extra-field behavior, cell-length boundaries, private-value-free errors and Decimal 0.10.

### Critical scope limitations

These tests ran in an **isolated reconstruction** of the two GitHub source/test files, not a full checked-out repository. The complete inherited suite, six GUI-to-CSV integrations, native Windows filesystem behavior, real x64 binaries, Defender scanning, 46-point accessibility matrix, encrypted premium entitlement and full-site delivery are **NOT VERIFIED**. GitHub-hosted CI remains blocked before step records in previous runs, with exact cause unknown.

## CI and release policy

`.github/workflows/desktop-build.yml` invokes R214 tests in **both normal and -OO modes on Ubuntu and Windows**, with fail-closed exit statuses and no financial fixture output in CI logs. GitHub-hosted execution must be witnessed; a workflow text change is not acceptance evidence.

**Owner smallest unblock:** inspect the GitHub Actions failure banner, billing/usage limits, repository Actions policy and hosted runner allocation; restore runners; rerun the unchanged feature commit. Once green, run all inherited desktop tests and six report-path integration smokes, privately build+checksum+Defender-scan+run six Windows x64 binaries, manually verify Win11 keyboard/NVDA/high-DPI UX, and test access-controlled premium distribution. Independent QD review and founder release authorization remain required. All six apps stay unreleased.
