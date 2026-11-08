# Final Vestige Labs R287 — premium review-lock exception custody

**Status:** DRAFT / independent QD + founder HARD HOLD. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Based on immutable R286 `876203fe80ba34e800a37ed030ce411f10b113a4`, not production `main`. All six Windows x64 applications remain unreleased.

## Reproduced privacy defect

The prior `review_lock.py` explicitly chained the native `FileExistsError` from an existing premium journal lock and the native `FileNotFoundError` from a disappearing one. Such exceptions retain the private lock pathname in `__cause__` even when the visible ValueError message is fixed. Unexpected `os.open`, `os.lstat`, and `os.unlink` failures could also escape with the pathname. A traceback or direct exception-object inspection could expose client identifiers embedded in journal paths. This is a local privacy defect, **not** evidence of a real customer disclosure.

## Code change

- Route premium lock creation and pathname observation through `_create_private_lock` / `_safe_lstat`. Fixed failure diagnostics are raised **after** leaving the OS exception handler, avoiding retention of the original OSError in either `__cause__` or `__context__`.
- Guard owned-lock cleanup with `_remove_owned_lock`. Denied unlink now returns fixed text; suspect locks remain on disk for manual review. A preexisting lock is never opened or overwritten.
- Ordinary owner verification, lock contents (process ID only), acquisition exclusivity, fsync, and safe deletion on success remain unchanged. Original source audit trails, money computations, premium entitlements and required human review are not altered.

## Actual local verification (Linux, Python 3.13.5)

- New `tests/test_review_lock_privacy_r287.py`: **6/6 PASS** in standard Python, **6/6 PASS** under `-OO`, total **12/12 focused executions** using a real temporary filesystem and synthetic injected OS errors. `py_compile` passed.
- Cases: existing lock preserves bytes and no chained path; denied creation fails closed; missing lock rejects; denied `lstat` leaves evidence untouched; denied cleanup leaves evidence intact; successful lock can be reused twice.
- Byte-identical original R286 `review_lock.py` Git blob `1505f51c20a89b8983a552d34fc7fa5f15e9a18f` run against the *same* new tests: **2 assertion failures + 3 uncaught privacy-path errors, 1 pass**. The new helper Git blob `de5b5b8bfa09498f1ec55bb719a82ff89073c10e` and test blob `121e9cb7b4621fe858b5abeab2cfb2437fa07ee5` match the locally executed files.
- **Scope limitation:** focused execution used a local minimal equivalent of `csv_snapshot._same_path_descriptor_signature` (the sole dependency of `review_lock`); the full repository, existing review-lock integration tests, hosted CI, and native Windows tests did **not** execute in this environment.
- Windows-specific missing-path testing simulates path disappearance rather than unlinking an open lock (real Windows file-sharing semantics differ). Both OS jobs now require standard and optimized R287 tests.

## Release gates / next action

[Last inspected R286 Actions run #42508272054](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42508272054) ended in failure before either Ubuntu or Windows runner recorded a step (`steps:null`); infrastructure cause remains unconfirmed. The smallest owner action is to verify Actions billing/spend, workflow policy and runner availability, then rerun this draft PR. Next highest-value engineering milestone: full inherited desktop regression suite, then trusted Windows 11 x64 six-app private executable build/smoke/SHA-256/Microsoft Defender acceptance, physical keyboard and screen-reader tests and protected Pro distribution review.

This document does not authorize release, signing, payment approval or publishing any executable or URL. Independent QD review and founder authorization are mandatory.
