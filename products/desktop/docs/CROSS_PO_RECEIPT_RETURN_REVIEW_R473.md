# R473 — Cross-PO receiving and return document reuse (DRAFT / QD HARD HOLD)

## Defect and review purpose
R471/R472 detect shared invoice and credit document identifiers across distinct purchase
orders, but the receipt CSV could reuse a receiving document or a return identifier
on two different orders without a cross-PO citation. Such reuse can be legitimate:
this change marks **human-review candidates** only, never duplicates as fraud,
payment approvals or compliance determinations.

## Implementation
- Extend the same typed, normalized, nonblank document-id index in
  `fvs_suite/procurement_cross_po_r471.py` to the receipt CSV's `receipt`
  and `return` event types separately. Cross-PO means distinct normalized
  PO keys; two lines on ONE PO never trigger these flags.
- Add `receipt_document_cross_po_review` and
  `return_document_cross_po_review` statuses plus
  `cross_po_receipt_source_rows` and `cross_po_return_source_rows`
  to the ProcureGuard CSV. Source rows are original **physical receipt CSV**
  row numbers, numerically ordered and semicolon-separated.
- Preserve all prior invoice/credit flags and evidence columns, exact Decimal
  totals, per-source SHA-256, original inputs, offline-only execution and
  manual compliance review. Do not infer offsets or deduplicate movements.

## Test evidence and acceptance
- Add eight committed real CSV/report integration methods in
  `tests/test_procurement_integration_r5.py`: normalized receipt reuse,
  normalized return reuse, same-PO multi-line receipt and return,
  distinct IDs, blank IDs, typed namespace isolation and simultaneous
  invoice + receipt evidence. Method inventory moves **24 to 32**.
- Isolated Linux Python 3.13.5 helper reconstruction: 8 standard and
  8 optimized `-OO -W error` focused methods passed. This is not a full
  repository or Windows application execution; committed integration tests
  have not run. Execute them on this exact PR head before any acceptance.
- Mandatory full six-app offline regression, installed Win x64 packaging,
  Defender/SmartScreen checks, keyboard and screen-reader accessibility,
  authentic checksums and entitlement-gated premium download verification
  remain release-blocking until run with evidence.

## Infrastructure hold
R472 source workflow https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43873953609
and Windows internal build https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43873953532
both failed before job steps (`steps=null` for four jobs). Runner/billing cause
has not been established. Repository administrator: inspect GitHub Actions
job annotations, billing and eligible runners; restore execution, then run
the exact R473 source integration and Windows workflows.

No production/main edits, merge, binaries, downloads, licenses or WordPress
publication. Independent QD review and explicit founder sign-off are required.
