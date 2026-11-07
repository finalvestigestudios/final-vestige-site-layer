# R257 — leak-safe SHA-256 inventory descriptor adoption

**DRAFT / independent QD and founder HARD HOLD.** Scope: shared `fvs_suite.manifest_guard._hash_regular`, which writes descriptive SHA inventories for local financial source and output files, including premium evidence. No data format, hashing algorithm, money calculation, licensing, or compliance decision changed. Parent: immutable R256 head `fb8a18e059ccc38719eeeeca25cc0677a9787885` (draft PR #1406), not `main`.

## Reproduced defect and fix

The previous SHA inventory hasher opened a private file with `os.open` and immediately passed the raw descriptor to `os.fdopen` inside a `with` statement. If stream adoption raised before the context manager existed, the raw descriptor could remain open. This occurred for regular `OSError` and exceptional/interrupt paths. An unexpected adoption error could also propagate a private path.

The shared hasher now calls the existing `premium_link_custody.open_inventory_stream` helper from R256. That helper closes a raw FD if `fdopen` fails for **any `BaseException`**, while successful streams remain owned by `with`. Missing-file exceptions keep their sanitized message; other adoption errors become a fixed, path-free `ValueError`. `KeyboardInterrupt` and `SystemExit` still propagate after descriptor cleanup. Regular-file, descriptor identity, bounded streaming, SHA-256, provenance digests and post-read metadata checks are retained.

## Local test evidence (2026-11-07)

Development environment: Linux, CPython 3.13.5, entirely synthetic local financial CSV and report bytes, no customer data or network. Isolated tests used Git-blob-matching copies of the changed `manifest_guard.py`, new `test_manifest_stream_adoption_r257.py`, and unchanged existing `csv_snapshot.py` and `premium_link_custody.py`. Relevant blob SHAs: changed guard `686613719e974d5f0b5029a09780396e76386168`; new regression tests `c2257ac837ca6b84794031d994717ba5d7aba5bc`; csv snapshot `108f330c46c536debff0b0303c5f7dc8f8c3f88d`; R256 descriptor helper `7b66c0cbe4f67f488e6f4d991fc49805a3e74da0`.

**Red first:** running the 15 new tests against the original `os.open`/`os.fdopen` path failed **4** adoption cases (3 failures, 1 error: OSError, RuntimeError, KeyboardInterrupt, SystemExit). **Green:** unchanged new tests against the committed fix passed **15/15 normal** and **15/15 optimized**; 30/30 local test-method executions, zero skipped. Normal and optimized commands (from `products/desktop`):

```sh
python -W error -m unittest -v tests.test_manifest_stream_adoption_r257
python -OO -W error -m unittest -v tests.test_manifest_stream_adoption_r257
python -m compileall -q fvs_suite tests
```

The 15 tests cover genuine SHA-256 content, ordinary and optimized inventory generation, exact source snapshot digest enforcement, no-open rejection for oversized or linked files, hardlink and basename alias rejection, missing-file privacy, correct stream closure after normal operation, no `fdopen` after failed `os.open`, and actual raw FD closure after four distinct adoption faults. No SHA stubs are used.

## Release gates / limits

Local testing covers the exact changed guard and new tests, plus exact unchanged dependencies in an isolated package. It **does not** certify the full repository test suite, native Windows 11 x64, GUI accessibility, signed/private EXEs, Defender/EDR, checksum/smoke, premium access control, or production site download URLs. A descriptor is owned only for the duration of verification; this is not immutable filesystem custody or source authenticity.

Hosted Actions runs were failing before reported steps, including R256 #42370857038 (both Ubuntu `source-tests` and Windows `windows-build` had `steps=null`, `logs_url=null`). Owner must restore GitHub Actions execution if billing/usage, Actions policy, or runner provisioning is blocking it; rerun this exact head through the full suite and Windows build. Keep the PR **draft**, do not merge or publish without independent QD + founder authorization.
