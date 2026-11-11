# R353 — ProcureGuard per-operation document-key snapshot

**Status: engineering draft; QD / founder HARD HOLD.** Applies to Issue #73 and is stacked on R352 draft PR #2038, not on production `main`. No executable, artifact, public download, license entitlement, WordPress publication or premium distribution changes.

## Actual defect and acceptance target

`review_line` looks up the **same original invoice/receipt/document ID repeatedly** while building candidate sets, duplicate counts, credit/return links and missing-reference review flags. `offset_source_line_links` also looks up both the source document and a credit/return's related-document label. Previously each request called the injectable `identifier` callback again. A stateful callback could normalize `"INV-42"` to `"INV-42"` once and `"POISONED"` on its next invocation. Thus the exact same source record could move between candidate groups *during one review*, producing inconsistent duplicate flags and false unresolved offset links. This is an evidence/provenance concern, not a payment decision.

The deterministic built-in `engine.key` is unaffected. The defect concerns the exposed `review_line` and `offset_source_line_links` Python API when a custom identifier callback is supplied.

## Code correction

- `fvs_suite/procurement_reference.py`: add `document_key_session(identifier)`, a per-operation closure with a plain `dict[str, str]` cache keyed by **exact native original source text**.
- Validate source IDs using `_native_document_text` **before cache lookup** to reject foreign objects/subclasses even if their apparent characters match an existing key. Preserve native bounded-integer compatibility.
- Perform first-use normalization using the R352 `normalized_document_key` implementation: result must be a native `str`; exceptions are redacted; Decimal context is restored. Failed callbacks do **not** populate the cache.
- `fvs_suite/procurement.py`: create independent local caches at the beginning of both `review_line` and `offset_source_line_links`. Replace both repeated raw callback closures. No global cache, disk cache, telemetry, financial record mutation, SHA changes, policy widening, or automatic compliance adjudication.
- Original source-label comparisons remain separate and conservative. Exact strings such as `"INV A"` and `"INV-A"` are **not** merged in the cache even if the configured lossy normalizer maps them to the same candidate key.

### Scope and limitation

Only repeated original labels within **one** call are frozen. This does not prove a malicious callback's *first* value is truthful or make different source IDs equivalent. New operations intentionally start with new caches; an arbitrary Python callback is not sandboxed. A direct caller may supply synthetic records, and only descriptor-verified CSV snapshots/digests establish original file provenance. The existing human review flags, local-first design and Decimal-safe financial rules stay in force.

## Reproducible local tests (2026-11-11)

- Environment: Linux CPython **3.13.5**; synthetic document identifiers, isolated `fvs_suite` helper package with an ASCII identity stand-in for the independent `review` import (not a full repository checkout).
- Verified exact Git blob IDs of tested files against committed branch: helper `df93e00db2d96e4f50d37c3e0f420a0eae29bd5e`; 26-method unit suite `4a0bb138fa262d453d205cbd8ef2a28b1fe3b677`; full-engine integration source `57e23c808f1cf288086e7587528b1f969cbc1134`.
- **26/26 PASS**: `PYTHONPATH=<isolated_package> python -W error -m unittest discover -s <isolated_tests> -p 'test_procurement_identifier_session_r353.py'`.
- **26/26 PASS**: same command with `python -OO -W error`. **52/52 passing focused executions** total.
- Baseline demonstration: repeated calls to R352 `normalized_document_key("INV-42", stateful_callback)` returned `["INV-42", "POISONED", "POISONED"]`; with R353 `document_key_session` they returned `["INV-42", "INV-42", "INV-42"]` with callback invoked **once**.
- All new source/unit/integration files passed `py_compile`; no customer data used.
- **NOT executed:** the 10 new tests against genuine `procurement.review_line` and `offset_source_line_links` because the isolated runner does not have the full private checkout. These cover repeated invoice/receipt/return IDs, legitimate credit/return references, two distinct physical source-row citations, empty references, deterministic exact Decimal totals and manual review flags. Do not count these as passing.
- Ubuntu and Windows CI now require **four commands per OS**, covering 26 unit methods + 10 integration methods in normal and `-OO` Python. Hosted jobs must execute successfully, not merely parse the workflow.

## Existing CI / release hold

R352's [Actions run #43008680287](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43008680287) reported failure for `source-tests` (Ubuntu) and `windows-build` with zero recorded job steps; root cause cannot be established through the available GitHub job metadata. Owner should inspect each failed check's **annotation** and Actions billing/spending limits, runner provisioning, and permissions. Confirm the new R353 PR run and rerun once runner checks can execute.

Before release, execute full inherited R342–R353 source/engine integration suites including 22 genuine AES-GCM cases. Then perform **native Windows 11 x64** build/smoke, SHA256 candidate receipt verification, Defender scan, UI accessibility, and locked premium distribution checks for **all six** utilities. Independent QD and founder review remain mandatory. Do not merge or expose premium downloads without approvals and verified gates.
