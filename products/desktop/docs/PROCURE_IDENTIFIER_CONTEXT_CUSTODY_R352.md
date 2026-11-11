# R352 — ProcureGuard document-identifier callback Decimal-context custody

**Status:** Draft engineering evidence only. Issue #73; stacked on R351 draft PR #2032. Independent QD review and founder authorization remain mandatory. No binaries, public downloads, site changes or premium payloads released.

## Defect / threat model

`review_line` runs in a fresh 64-digit `decimal.Context` to preserve exact source money. Numeric parsers already execute inside `localcontext()` (R348), but the injected `identifier` callback used by `normalized_document_key` did not. A direct API caller could return a perfectly valid native normalized string **while lowering `getcontext().prec` to 1, replacing the context with `setcontext()`, changing rounding, enabling traps or changing Emax/Emin and status flags**.

Invoice/receipt document normalization occurs before `review_line`'s final `net_inv_qty * order_price` reviewer comparison. Callback precision corruption can therefore round the *expected* source total and produce an inaccurate human price-variance flag. Under `prec=1`, `Decimal(3) * Decimal("0.12345678")` becomes `0.4` instead of the exact `0.37037034`, although the gross invoice amount was already computed at full precision. This is financial evidence/review integrity, not automatic approval.

## Correction

`products/desktop/fvs_suite/procurement_reference.py`: call the external `identifier(text)` inside `decimal.localcontext()`. Python restores the prior active context on normal return, replacement via `setcontext`, and an exception. Existing native text/integer source validation, exact native `str` return requirement, confidential-error redaction, lossy identity semantics, and human-only review flags remain unchanged. No financial row values, audit source hashes or source files are modified.

This is **not** an arbitrary Python sandbox: callbacks can still mutate captured objects, process-level state or perform unrelated side effects. The scope is the active Decimal calculation context.

## Test evidence (2026-11-11)

- Exact Git blob of modified helper: `9ec6e775d6f8f97785e1e8bde14b05af85d4c133`.
- Exact Git blob of focused unit tests: `fa1b3a8b07a173a7504e8f59acd6aec805170b25`.
- Exact Git blob of added real-engine integration tests: `7e09adb164797c2006fc2bb0112bc28804a96358`.
- Linux CPython **3.13.5**, isolated `fvs_suite` package containing the exact helper and a minimal stub for the separate `ascii_case_identity` import; synthetic IDs only.
- Baseline replay with the R351 helper (no `localcontext`): **14 failures / 26 tests**; source-integrity failure reproduced.
- Fixed helper, normal `python -W error -m unittest`: **26/26 PASS**.
- Fixed helper, optimized `python -OO -W error -m unittest`: **26/26 PASS**. **52 focused passing executions** total.
- All three source/test modules syntactically compile. SHA for tested helper/unit/integration test files verified against actual GitHub blob IDs.
- Eight **additional genuine `review_line` integration methods committed and syntax-checked, but NOT EXECUTED** because a complete checkout is unavailable to the local runner. They check false-positive and legitimate variance review flags, context mutations, private error redaction, and determinism.
- Ubuntu and Windows workflow adds **four unit/integration commands per OS** (normal and `-OO`), for eight commands total. Hosted CI status still must be checked against this new branch.

## CI blocker and release hold

Prior R351 [Actions run #43000417883](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43000417883) has both Ubuntu `source-tests` and Windows `windows-build` failed with **zero recorded steps**. The cause is not established; GitHub's relevant check-annotation endpoint is unavailable through the present connector. The repository owner must inspect the UI annotations and check Actions billing/spending, runner provisioning and workflow permissions. A successful workflow for the R352 commit must execute the **complete** repository suite, inherited R342–R352 integration cases and 22 real AES-GCM cases before any acceptance.

Then run signed/unsigned Windows 11 x64 native builds, file/manifest SHA-256 attestation, Defender scanning, GUI accessibility/smoke checks, and protected premium distribution checks for all six products. Do not promote draft PRs or publish untested files. Independent QD and founder approval are required before production release.
