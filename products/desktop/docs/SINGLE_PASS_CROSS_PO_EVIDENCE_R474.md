# Final Vestige Labs R474 — Single-pass cross-PO document evidence (DRAFT / QD HOLD)

## Defect and improvement
ProcureGuard Studio Pro's cross-order audit evidence formerly invoked four independent typed document scans: invoice, credit, receipt and return. The invoice CSV was classified once for invoice and again for credit; the receiving CSV was classified once for receipt and again for return. This duplicates classification work and, for a directly invoked helper with a stateful classifier, can produce mutually inconsistent typed evidence across separate scans.

R474 adds `cross_po_all_document_source_rows` to index all **four** explicitly typed namespaces while classifying each input row **once**. The production reconciliation path now uses the one bulk result. The original four narrow helper interfaces remain intact for compatibility and parity testing. The visible report schema, source-row CSV citations, normalizers, flags, policy, Decimal computations and human-review rules are unchanged.

**Privacy/custody:** No source document IDs, customer input data, local paths or financial amounts are emitted by the index itself. Nonblank normalized IDs are candidates, not proof of document identity or fraud. Original physical CSV row labels remain numerically ordered in the report; invoices and receiving events remain separate typed namespaces, as do original and offset events. Invoices and receipts are never deduplicated, modified, sent to a server, automatically approved or rejected.

## Committed acceptance tests
Five new methods in `tests/test_procurement_integration_r5.py`, raising its declared method inventory from **32 to 37**:
1. Actual CSV/report fixture with all four typed cross-PO reuse warnings, original source citations, unchanged exact Decimal totals and three SHA-256 custody columns.
2. Same identifier in distinct event *types* does not create cross-PO warnings.
3. Multiple shared document identities aggregate only their proper PO/line physical source rows, in numeric order.
4. Bulk helper produces the same evidence as each legacy typed helper and calls event classifiers exactly once per source row.
5. Reordered input groups/rows do not change evidence.

## Executed narrow evidence, not release qualification
After committing, the exact R474 helper source was reconstructed locally and verified by `git hash-object` as **`0a5da1d2b4e7ddc438de0b8544b2db306dbfbac2`**, identical to GitHub's committed blob SHA. Its actual functions (including the four legacy wrappers) executed in isolated Python 3.13.5 tests: **6/6** standard and **6/6** `python -OO -W error` (**12/12**). The fixed-seed 6,000-row randomized fixture found identical evidence dictionaries against the actual legacy helper, and other tests covered once-per-row classification, all four typed streams, empty IDs, empty inputs and no namespace collisions.

A separate precommit 40,000-row projection showed identical result dictionaries; timing was about 0.111s four-pass vs 0.115s bulk in one normal run, and 0.125s vs 0.117s in optimized mode. These measurements **do not establish a wall-clock speedup**. The measurable change is event classifier calls (two per source row to one). The tests above ran the exact committed helper module **in isolation**, not a complete checked-out application. The five newly committed end-to-end CSV methods, complete 37-method ProcureGuard integration suite and six-product matrix **have not been executed**.

## Mandatory holds
- Execute the **actual committed 37-method** ProcureGuard CSV integration file and the complete six-engine offline regression matrix on the exact R474 head in standard and optimized Python modes. Resolve regressions, not just inventory counts.
- Run both genuine Windows x64 internal packaging and Windows-installed smoke/accessibility tests with Defender/SmartScreen review and authentic SHA-256 checksum evidence.
- Verify protected premium entitlement and download access before sharing any GrantAudit Studio Pro or ProcureGuard Studio Pro executable. Do not claim availability of either free or premium EXEs until verified.
- Prior R473 source workflow [#43883198969](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43883198969) and Windows internal workflow [#43883198968](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43883198968) failed with all four jobs showing no steps. Cause unconfirmed: inspect job annotations, account billing/spending eligibility and runner assignment, restore execution, then examine exact R474 CI separately.
- Keep the branch and PR **draft**, release gate **HOLD**, production `main` and WordPress untouched. Independent QD review and explicit founder approval are required.

## Next highest-impact step
Restore GitHub Actions execution and obtain real exact-head six-app and Windows x64 test results. A passing isolated projection or a green synthetic count is not proof of shippable binaries.
