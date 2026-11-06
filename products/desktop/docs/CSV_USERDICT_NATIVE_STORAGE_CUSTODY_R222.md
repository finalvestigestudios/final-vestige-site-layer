# R222 — UserDict native-storage custody for six-app CSV audit exports

**Status: DRAFT / QD + founder HARD HOLD.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). R222 is stacked only on R221 [draft PR #1179](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1179) (parent `e65ae2e5859a985d33a81710621866c16b2a6656`), **not** production `main`. All six products are UNRELEASED.

## Defect / scope

R221 used `dict.items(row)` to defeat forged `dict` subclass views. A second supported public API shape is `collections.UserDict`. Its subclasses can override `.items()` while retaining a different native `.data` dictionary. A well-formed virtual three-column view could therefore misstate a transaction identifier/amount, hide a source-row omission, or conceal an unsafe extra column without triggering the R217 pair-shape validation. This is a **synthetic direct-API evidence-integrity risk**, not a claim of customer exploitation.

## Change

- New `fvs_suite/csv_userdict_custody.py` checks any `UserDict`-derived record's supplied, structurally validated native two-tuples against **actual built-in dictionary backing storage** reached through the native instance dict and `dict.items(backing)`. It bounds reads at 257 entries; requires native string keys; compares exact immutable primitives by value and other values only by object identity, without running user-defined equality hooks. On mismatch, rejects with generic no-customer-data `UserDictCustodyError`; deliberate failures cannot retain exception context.
- `fvs_suite/atomic_reports.py` invokes the check **after** original R217 malformed-pair rejection and before sanitizing/publishing any row. It renders the authoritative native snapshot, not the virtual view.
- Exact `dict`/subclass, `MappingProxyType` and other non-`UserDict` Mapping paths retain the R221 API. Standard `UserDict`, Decimal scale, negative amounts, atomic no-overwrite, UTF-8 BOM, 256-column / 200k-row / 64-MiB protections, local-only privacy and human decision authority remain unchanged.
- This does **not** certify arbitrary non-`UserDict` custom Mapping implementations, including mapping classes with virtual `.items()` and no verifiable native backing. Compatibility and trust boundaries still require QD review.

## Test inventory and evidence

**Committed source-owned tests:** `tests/test_userdict_storage_r222.py` has **23** helper-level synthetic unit methods. `tests/test_atomic_userdict_custody_r222.py` has **7** full publisher/rollback/Decimal integration methods. Both are explicitly required on **Ubuntu and Windows** in the existing `.github/workflows/desktop-build.yml`, with both regular Python and `python -OO` runs (60 expected method executions when runners actually start).

**Updated local verification (supersedes earlier 46-execution scope):** Linux x86_64 CPython 3.13.5, synthetic fixtures and byte-exact committed Git blobs: the new helper (`1a6afd...`), 23-case helper test (`572df87...`), 7-case full-writer test (`419f4a6...`), **patched actual writer** (`da00254f...`), and inherited formula/native-cell modules (`79e493...`, `1030e18...`) were individually checked against `git hash-object`. The isolated reconstructed package ran **30/30 methods PASS normal + 30/30 PASS `python -OO` = 60/60 local method executions**, zero skips, `PYTHONWARNINGS=error`, Python compilation PASS. **Red-before-green proof:** reverting only the writer to its byte-exact R221 Git blob (`63909a...`) made the seven new writer tests fail (**5 failures, 1 error, 1 pass**); restoring byte-exact R222 source made all 7 pass in both modes. An earlier helper draft had two context-privacy failures; corrected before push. This executes actual byte-identical writer + tests in an **isolated reconstructed package**, NOT an intact full repository checkout or Windows runner. Inherited six-engine tests and native Windows binary acceptance are still unverified.

**Local reproducer scope:** Helper-level test inputs include forged ID and amount, hidden extra/formula, missing source, reordered view, str subclass, hostile custom `__eq__`, direct backing corruption, oversize backing, standard `UserDict`, mappingproxy passthrough and Decimal scale. End-to-end CI methods cover atomic rollback, existing destination, UTF-8 BOM and exact Decimal output.

## Release hold and smallest unblock

As of R221 [Actions #42141442976](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42141442976), both Ubuntu/Windows jobs were **completed failure with no execution steps**; root cause remains unconfirmed. Inspect the owner-visible Actions pre-start error plus billing/limits/permissions/runner availability; restore allocation and rerun **unchanged R222 head**. If R222 jobs are similarly pre-start failed, no hosted PASS may be claimed.

Next: run all 30 new tests and inherited six-app tests on intact Ubuntu/Windows checkouts, including R220's seven unrun engine integration methods; privately build, checksum, scan and real-Windows-11 smoke-test six distinct x64 executables; perform 46 physical accessibility observations; validate protected premium download/licensing; obtain independent QD and explicit founder release approval.

**Do not merge to main, publish/download executables, create ungated Pro download URLs, or update the live site as a release.**
