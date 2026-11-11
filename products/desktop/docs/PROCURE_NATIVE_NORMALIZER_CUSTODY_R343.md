# R343 — ProcureGuard native normalization and physical-source citation custody (DRAFT / HARD HOLD)

**Target:** ProcureGuard Studio Pro only; issue #73. Parent is exact R342 commit `feb499cd068f6cf0edbb3c7c50b51b4d9ce0c368` on draft PR #1974. No merge to `main`, WordPress publication, Windows executable, premium delivery or compliance approval.

## Defect and change

R342 guarded original-spelling comparison, but `review_line` and `offset_source_line_links` still called the injected `identifier` normalizer **before** that guard in 17 places. A forged direct-API document-label object could therefore reach a caller-defined conversion callback, and a callback could return an untrusted key object or raise a private-path-bearing exception. Even without any credit or return event, document display could encounter a non-native cell.

- `fvs_suite.procurement_reference.normalized_document_key` now validates original input using R342's native-text/bounded-native-integer primitive **before** calling `identifier`; converts approved numeric input to built-in text; requires the callback result to be exact built-in `str`; and redacts ordinary callback errors without masking `KeyboardInterrupt` or `SystemExit`.
- `fvs_suite.procurement.review_line` now requires native `str` cells for all invoice/receipt `document_id` and `related_document` fields **before** monetary processing or human display. Its 15 normalization call sites and the two in `offset_source_line_links` use the guarded callback. This distinction is intentional: the native-integer helper retains standalone legacy compatibility, while physical CSV review rows always contain text.
- Candidate identity remains *lossy*, never evidence of exact source spelling. A punctuation/Unicode mismatch still creates a human-review flag. Exact Decimal finance calculations, physical-row provenance and no-silent-approval rules are unchanged.

## Source and test inventory

- `fvs_suite/procurement_reference.py` — helper implementation, Git blob `67ad682084da29789056cb1f3cfa5bd63405cce3`.
- `fvs_suite/procurement.py` — guarded integration across both review and source-line link generation.
- `tests/test_procurement_normalized_key_r343.py` — 26 adversarial helper tests, Git blob `5eb648c9d856067bab0cf4ae68821401f1d55e37`.
- `tests/test_procurement_document_boundary_integration_r343.py` — 20 *real-engine* tests for forged cells, callback failure/result integrity, normalization review flags, Decimal totals and offset physical-row citations, Git blob `4d5338672cef8afb9fc23c2a3b3c9e5e8e36193e`.
- `.github/workflows/desktop-build.yml` — explicitly gates both new suites on Ubuntu and Windows, standard and optimized Python, before Windows packaging.

## Executed evidence and limits

**Linux CPython 3.13.5, locally isolated helper package:** `python -W error -m unittest discover -s tests -p 'test_procurement_normalized_key_r343.py'` yielded **26/26 PASS**; `python -OO -W error -m unittest discover -s tests -p 'test_procurement_normalized_key_r343.py'` yielded **26/26 PASS**. Total **52 executed helper method cases**, no skips. `py_compile` of helper and both new test files PASS. Actual executed helper and test contents were independently checked by `git hash-object` against GitHub's exact committed blobs above; the isolated `review.ascii_case_identity` dependency faithfully reconstructs R342's five-line implementation, not a full repository checkout.

**Not executed locally:** The 20 full-engine integration cases (only their syntax compiled); existing ProcureGuard regression suites; 22 genuine AES-GCM integration cases; all six native Windows 11 x64 builds, smoke tests, SHA checks, Defender scans, accessibility and entitlement-controlled distribution. The changed `procurement.py` was inspected and GitHub updated, but **not independently executed in the local environment** because the private repository could not be cloned by the container and runner-hosted jobs remained unavailable. Do not interpret source-case passes as Windows acceptance.

## Active CI blocker and next highest-impact work

The immediately preceding R342 [Actions run 42936932275](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42936932275) failed on **November 10, 2026 PST / November 11 UTC**, with `source-tests` and `windows-build` reporting `steps=null`; the underlying reason is **not yet confirmed**. The connected read endpoint for check-run annotations returned HTTP 400 (unsupported fetch route), so owner inspection is required.

**Smallest unblock:** repo owner opens GitHub Actions run, expands each failed job's annotations, and checks Actions billing/spend limit and runner allocation/workflow permissions. Once runners work, run both R343 suites plus the full ProcureGuard/R75 regression selection and genuine encryption integration; resolve any failures before QD review. After that, complete six-app native Windows acceptance and protected premium distribution. Keep this stacked PR DRAFT/HOLD; do not merge or publish without independent QD and founder approval.

No client source data, uploaded financial evidence, telemetry, premium binaries, public download links, compliance decisions, site changes, or production mutations were made.
