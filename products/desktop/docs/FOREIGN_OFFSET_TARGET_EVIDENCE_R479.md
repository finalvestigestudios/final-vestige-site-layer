# R479 — cross-PO offset reference to original-document source rows

Issue: [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). **Internal stacked draft on R478**. Independent QD and founder approval required; no production merge, download, entitlement or publish.

## Concrete ProcureGuard review gap

An offset document with a unique credit-memo or return ID could reference an original invoice or receipt that exists **only on another purchase order**. Previously the affected PO line received a generic `unlinked_credit_review` or `unlinked_return_review` but did not tell a reviewer *which foreign original physical CSV row* to inspect. Existing cross-PO duplicate-document checks only consider the identity of the original or credit/return itself; an unrelated offset ID does not trigger those reuse checks.

R479 adds the bounded, local-only `cross_po_foreign_offset_source_rows` resolver for both `credit → invoice` and `return → receipt`. It scans each input stream once for this resolver, classifies each event once in that pass, and indexes normalized `document_id` and `related_document` without putting private document IDs in new report fields. It emits foreign original-source **physical row labels** only when a reference resolves to a source on another **PO** and there is no original with the same normalized ID anywhere on the offset's own PO (including another line). This intentionally favors existing local evidence over a new foreign-reference finding, while existing cross-PO duplicate-document warnings still apply independently.

New review flags: `credit_reference_cross_po_review`, `return_reference_cross_po_review`. New columns: `cross_po_credit_target_rows` (invoice CSV source rows) and `cross_po_return_target_rows` (receipt CSV source rows). The flag and row list are **review cues, not proof of fraud or permission to approve/reject a payment**. The previous generic unlinked flags remain.

## Privacy, determinism and failure semantics

- No original CSV input, parsed numeric cell, source SHA-256, Decimal calculation, original audit field or payment action is rewritten.
- The renderer uses the already-reviewed numeric source-row parser (native 1–10 ASCII digits) and deterministic `(int(row), len(row), row)` order; PO/line group order is sorted.
- Each offset's original reference is namespace-scoped to the correct typed source. Original invoices cannot satisfy return references and original receipts cannot satisfy credits. Missing or blank references do not generate evidence.
- Before creating any **expanded foreign-target report** evidence, a separate conservative `1,000,000`-citation preflight validates both credit and return target row labels, with fixed redacted errors. Repeated references can conservatively overcount the reservation; this is a release HOLD rather than silently truncating evidence. The existing shared cross-PO document-reuse index has its own separate 1,000,000-citation preflight, so **this is not an overall process-memory guarantee**.
- A same-PO original suppresses this specific foreign-target flag even when a foreign duplicate exists; the original shared-document cross-PO warning remains available. Human review must resolve contradictions.
- No telemetry, network upload, external inference, auto-approval, or public premium links.

## Exact repo artifacts

- `products/desktop/fvs_suite/procurement_cross_po_r471.py`: new resolver.
- `products/desktop/fvs_suite/procurement.py`: invokes resolver, inserts review flags, and adds report CSV columns.
- `products/desktop/tests/test_procurement_cross_po_foreign_offset_r479.py`: **16 new committed unit methods**, including source namespace isolation, collisions, deterministic rows, absence of false positives, source-row privacy, budget failure, and one event-classifier call per scanned row.
- `products/desktop/tests/test_procurement_foreign_offset_integration_r479.py`: **4 new full-CSV integration methods** with source SHA-256 custody, Decimal total conservation and human-readable review flags.
- `.github/workflows/desktop-source-evidence-r385.yml`: both new test files in standard and `-OO` Python modes on both Ubuntu and Windows runners.

## Executed versus unverified

Executed a **local isolated prototype** of the exact *algorithmic shape* on Linux: **14/14 tests standard Python and 14/14 optimized Python, 28/28 total**, including credit, return, normalized references, same-PO suppression, cross-stream isolation, sort ties, duplicate rows, redaction, budget and insertion-order invariance. The local prototype was **not the GitHub-byte-identical complete ProcureGuard module**; no claim is made that the 16 committed tests or four complete CSV integration methods ran. The last inherited six-engine/Windows hosted workflows repeatedly failed before any job step ran (`steps=null`, infrastructure root cause unconfirmed). Once a live R479 PR run exists, inspect its exact-run job metadata before claiming any hosted success.

**Not validated:** all six source engines together, full R5 CSV integration suite, real native Windows x64 executables, Defender scan, accessibility, SHA256 of binaries, premium entitlement/distribution or site downloads. No release gate has been satisfied.

## Next highest-impact action

Repository/org administrator: inspect failed GitHub Actions run annotations and billing/hosted-runner eligibility; restore runner scheduling and execute the exact R479 branch's new 16 + 4 methods (normal/optimized), inherited full 38-method ProcureGuard CSV integration and all-six regression gate. Correct any integration failures on a new draft commit, then pursue signed/unsigned Windows x64 QA, Defender/keyboard/screen-reader evaluation, reproducible checksums and protected premium delivery. Independent QD review plus explicit founder approval remain mandatory before any merge or publication.
