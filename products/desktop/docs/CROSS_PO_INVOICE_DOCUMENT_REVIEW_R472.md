# R472 — Cross-PO invoice document reuse review (DRAFT / QD HARD HOLD)

## Defect / scope
ProcureGuard Studio Pro already flagged repeated original invoice IDs **within** a
PO/line and R471 flagged cross-PO **credit** memo ID reuse. Two independent
purchase orders could still share the same normalized **invoice** document ID
without a specific cross-order review flag. An invoice can legitimately cover
several POs, so this is only a human-review candidate, not a fraud finding.

## Change
- The typed source-index helper `fvs_suite/procurement_cross_po_r471.py`
  now supports **invoice** and **credit** identities in disjoint namespaces.
  It deliberately does not treat different lines of the same PO as cross-PO.
  IDs must be nonblank and event type must explicitly match.
- ProcureGuard adds `invoice_document_cross_po_review` to affected output
  statuses and `cross_po_invoice_source_rows` with numeric-order **physical**
  invoice CSV source-row citations, retaining prior `cross_po_credit_source_rows`.
- Source input snapshot digests and original document labels are retained.
  No financial values, Decimal precision, rows, credits, approvals or
  original files are changed; no telemetry or uploading is introduced.

## Test acceptance
- Five new actual CSV/report integration tests in
  `tests/test_procurement_integration_r5.py`: normalized cross-PO duplicate,
  legitimate multi-line same PO, distinct IDs, blank IDs, and event namespace
  isolation. This mandatory integration suite inventory rises 19 -> 24.
- Separately executed isolated helper regression: eight synthetic methods
  in Python standard and eight in `-OO -W error`, all passing on Linux.
  These test the helper, **not** the committed full ProcureGuard engine.
- Source gate's `SOURCE_INPUTS` already includes both edited Python files
  (through the suite import root and explicit helper path) and the edited
  integration test, so no inventory expansion is necessary.
- Full repository regression gate and native Windows tests must run on the
  exact PR head before acceptance. Synthetic helper pass != binary ready.

## Release gates (still BLOCKED)
GitHub Actions for preceding R471 SHA `458358b197dcde9c4b9c8ea0ce1d1ed18fe9bd60`
reported both source and Windows workflows failed with all four jobs
`steps=null`. The infrastructure root cause is unconfirmed. Check exact
R472 head workflow runs and administrator failure annotations; restore runners
before testing the complete 24-method ProcureGuard suite, full six-app
regressions, Windows x64 build, Defender scan, installation/keyboard/screen
reader audit, immutable SHA-256 and premium entitlement/access verification.

No deployment, production merge, binaries, unrestricted premium URLs,
WordPress publication or financial compliance decisions. Independent QD
review and explicit founder authorization remain mandatory.
