# R429 — Bound SpendMap vendor-label audit report amplification

**Issue:** #73. **Scope:** SpendMap Lite report display/evidence only. **Release hold:** source-only draft, no build, download, entitlement, or site change. Not an identity verification, fraud finding, payment decision, or compliance approval.

## Defect and rationale

R428 correctly retained distinct original vendor strings so humans could see source spaces, Unicode, controls and separators. It still concatenated **every distinct original source label** into `source_vendor_labels` for **every category/month row** associated with that normalized vendor. A valid 64 MiB source file can contain thousands of distinct labels collapsed by a user-supplied normalization rule. Repeated full label lists could turn a bounded source into very large in-memory reports or CSV/GUI cells.

A deterministic synthetic 2,000-label case (each original 906 characters) generated **1,815,998 characters** in the old one-vendor label cell, versus **7,373 characters** with this patch; normalized identity counts both remained **2,000**. This is source-memory amplification, not an alleged production exploit.

## Behavior

- Up to **32** distinct source labels appear in deterministic original-label order; the combined label field is capped at **8,192 characters**.
- Labels whose full visible representation is at most **1,024 characters** remain **unchanged**. Longer originals show a visible first-64-codepoint prefix followed by a non-source marker `\\u[LABEL_PREFIX_ONLY]`. Large or heavily escaped labels are not silently presented as complete.
- Any omitted labels or any clipped individual label produce an explicit `\\u[PREVIEW_ONLY:shown=N:omitted=M:sha256=H]` trailer. Its SHA-256 covers **all distinct complete original labels**, not just the preview, and is stable under record permutation.
- A literal input beginning with `\\u[` has its backslash escaped by the existing renderer and cannot impersonate this marker. The annotation is report-display metadata, not part of the original CSV.
- Short source labels, normalization/collision calculations, `vendor_label_variants`, the source snapshot SHA, source row references, exact Decimal cents, gross/credit totals, full vendor/month membership digests and all review-only flags are unchanged. Only the over-budget `source_vendor_labels` field changes relative to R428.

### Recomputing a truncated-label fingerprint

Deduplicate **native original** vendor strings (excluding empty/ASCII-only-whitespace values per the existing SpendMap evidence contract), then sort by `(value.casefold(), value)`. SHA-256 the UTF-8 byte string `FVS-SPEND-RAW-VENDOR-LABELS-v1\\n`, followed for **each** distinct original label by its UTF-8 byte length as an eight-byte unsigned big-endian integer and its complete UTF-8 bytes. This digest is independent of the report truncation and guards accidental mismatch during human review; **it is not a keyed MAC, a signature, proof that the source is trustworthy, or a replacement for the original file**.

Reviewers must refer to the preserved original CSV, its independently verified `source_sha256` and physical row citations whenever `PREVIEW_ONLY` appears. Do not treat the abbreviated field as an exhaustive source transcription.

## Artifacts and executed evidence

- `fvs_suite/spend_vendor_evidence_r358.py` — bounded preview and full-label digest without modifying matching policy.
- `tests/test_spend_source_label_custody_r428.py` — **17 added R429 unit methods** alongside the 18 inherited R428 methods, already targeted by `.github/workflows/desktop-source-evidence-r385.yml` on Ubuntu and Windows, standard and `-OO -W error`.
- `tests/test_spend_source_label_integration_r428.py` — **3 committed real-engine integration methods** alongside existing five, also already wired to both OS CI lanes.

**Actually executed locally (Linux Python, isolated package):** 35/35 methods standard + 35/35 optimized `-OO -W error`, 70 total passing executions; `compileall` passed. These exercised the exact new helper body and the existing R428 test semantics with **local stand-ins for the unchanged shared display/ASCII identity dependencies**, not a full repository checkout or native Windows application. The three new real-engine methods were **committed, not executed**. The full inherited repository suite and cryptographic, entitlement, packaging and Windows release gates remain unverified.

The local controlled before/after benchmark used synthetic labels, not private customer data. Its before result reconstructed the pre-R429 concatenation semantics; it is **not** a production profiling trace.

## Mandatory gates and next step

1. Restore Actions runner eligibility: inspect organization/repository Actions billing, spending limit, runner/policy restrictions and job-assignment diagnostics. Recent source and desktop build workflows concluded failure with zero recorded job steps and no assigned runner; precise cause has not been verified.
2. Run exact-commit Ubuntu and Windows source tests, inherited R358, added R429 and genuine SpendMap integration in normal and optimized modes. Check schema/CSV export consumers of `source_vendor_labels` for partial-field handling and ensure no truncation is mistaken for full provenance.
3. Then run full six-engine Decimal, audit, signing, entitlement, release candidate, Windows 11 x64 smoke, accessibility, Defender and protected premium delivery acceptance gates.
4. Independent QD review and explicit founder approval are required before merge to production, build release or download publication. `release_authorized=false`.

No executables, unprotected premium files, fabricated download URLs, website publication, broker connection, network upload or telemetry introduced.
