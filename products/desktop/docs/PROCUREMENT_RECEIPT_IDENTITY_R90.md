# R90 — ProcureGuard receiving-document and return identity custody

**DRAFT SOURCE ONLY / RELEASE HOLD.** No payment approvals, fraud determinations, premium entitlement changes, customer-data uploads, or executable releases.

## Why this matters

ProcureGuard's predecessor review_line counted repeated normalized invoice document IDs, but **not repeated receipt document IDs**. A perfectly balanced synthetic three-way match could therefore emit matched for PO quantity 10, invoice quantity 10, and *two* receipt entries of quantity 5 bearing the same physical receipt reference. Equality of amounts does not establish two distinct receiving events. The same blind spot existed for repeated return references and for a return borrowing its source receipt's own document ID.

This is conservative **human-review evidence**, not an assumption that a repeat constitutes an improper purchase, false receipt or fraud. A legitimate system may repeat identifiers across distinct line movements; reviewers must inspect source documents and organizational rules.

## Implemented change

- Regular-receipt rows flag repeated_receipt_document_id_review when two nonblank receipt references share the existing normalized matching key, including punctuation and ASCII-case collisions.
- Return rows similarly flag repeated_return_document_id_review.
- A return whose nonblank document ID matches a regular receipt's normalized ID receives reused_receipt_document_id_review. Existing linked-return checks and unidentified_return_review still apply.
- Blank optional **receipt** IDs do not become a fake shared ID. Missing return document IDs retain the pre-existing flag. Invoice/credit handling, quantities, prices, policy thresholds, Decimal logic, and human-review controls are unchanged.
- Two **append-only** CSV columns, receipt_documents and return_documents, display distinct original labels for each event type (not merely normalized keys). They apply existing audit_display.visible_source_text to expose control, bidirectional and visually blank Unicode and to distinguish actual escape characters from literal backslashes. These two columns are **display strings**, not byte-for-byte originals; use the original CSV, physical row references and source hashes for evidence.
- Existing SHA-256 manifest, private staging, atomic publication and preservation of original inputs remain intact.

## Minimal reproduction

PO PO-A/1, qty 10 at $5; invoice qty 10 at $5; two receiving rows of qty 5 each, both document_id=REC-1. Previously, if other conditions agreed, the three-way status could be matched. After R90, it contains repeated_receipt_document_id_review, receipt_rows=2;3 and the receipt_documents display cell REC-1. The engine makes no approval or compliance decision.

## Tests and limits

The committed tests/test_receipt_identity_r90.py contains **19 new regression methods**: normal distinct receipts, duplicate and punctuation/case collisions, Unicode visibility, empty optional IDs, 500 unique receipts, return ID duplicates/reuse, unchanged originals, deterministic operation, hostile Decimal caller settings, local CSV-to-manifest integration, optional alias headers, physical row references, and invalid-source no-partial-bundle behavior.

**Executed isolated Linux preflight** using a copied source-equivalent receipt identity block (not a repository checkout): **16/16 normal, 16/16 with python -OO, compilation successful**, including 200,000 distinct-receipt synthetic entries. The old missing detection is established by predecessor source inspection and a corresponding equal-total synthetic reproducer. The **19 committed repository tests have NOT run** in an authenticated checkout, and there is NO Windows executable acceptance.

Full checkout acceptance commands (run from repository root):

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_receipt_identity_r90.py' -v
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_receipt_identity_r90.py' -v
    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -v
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -v

## Mandatory release gates

GitHub Actions issue #75 remains a separate blocker: both source and Windows jobs have repeatedly failed **before recorded steps**. Restore a hosted Linux test step, then full normal/-OO tests and Windows 11 x64 GUI/EXE installation, accessibility, AV checks, SHA-256/download verification and independent QD/founder approval. No executables, premium links, entitlements, website publication or production branch changes are authorized.
