# Labs R475 — bounded ProcureGuard cross-PO evidence (DRAFT / QD HOLD)

## Why this change is necessary

The R471–R474 ProcureGuard review indexes turn one repeated document ID into an
all-to-all set of physical CSV row citations for each affected purchase-order
line. A 1,001-row invoice import containing the same valid ID on 1,001 distinct
POs can require **1,002,001** repeated references, despite having only 1,001
input rows. A 2,000-order case would exceed 4 million references. The existing
per-input source-size and row-count caps do not bound this report expansion.
Before R475, evidence materialization used an unbounded set update per PO/line.

## Change, exact contract and safety

In `fvs_suite/procurement_cross_po_r471.py` an internal `_bounded_index`
performs a source-row and affected-PO/line cardinality preflight **before**
materializing each document's repeated citations. It has a fixed budget of
**1,000,000 expanded citations**, shared across invoice, credit, receipt and
return in the production bulk scan. The four retained direct typed wrappers
apply the same cap independently.

- Distinct *PO IDs* remain mandatory for a cross-PO alert. The same document
  repeated over lines of one PO does not cause a false positive or consume
  expansion budget.
- Only same-kind source events can match. Cross-kind ID reuse does not collide.
- Empty normalized document IDs are ignored, and physical row labels remain
  sorted numerically, with no mutation of originals, amounts or evidence.
- The budget is conservative: overlapping document sets may count the same
  eventual output citation more than once. This deliberately fails closed
  rather than emitting partial audit evidence.
- Exceeded budget raises a fixed `ValueError` with **no** private identifier,
  filename, PO key or financial content. The procurement engine indexes before
  writing its CSV/report bundle; the new real-CSV regression checks that no
  completed report is published on rejection.
- Reviewers must resolve exceptionally large cases, or engineering must
  design/test a bounded streaming report. Do **not** partition inputs merely
  to evade cross-PO identity checks. No automatic compliance, fraud or payment
  determination is made.

This is a cap on *materialized reference expansion*, not a guarantee on total
process RSS, CSV byte size or latency. The inherited import/serializer limits
are separate safeguards.

## Commit-scoped test evidence

The exact committed source module, Git blob
`ffaccbecdaa02106139f8baddb2ac033f435acaa`, and new test module,
Git blob `ae5e2343f8660cfb3fc231bacd7ecb617aa93e9f`,
were reconstructed as local source files. `git hash-object` on both local
files matched the GitHub object hashes. The **actual 8 committed test methods**
ran on those exact bytes under Linux in both modes:

```sh
PYTHONPATH=/mnt/data/labs_r475 PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover -s /mnt/data/labs_r475/tests -p test_procurement_cross_po_budget_r475.py -v
PYTHONPATH=/mnt/data/labs_r475 PYTHONDONTWRITEBYTECODE=1 python -OO -W error -m unittest discover -s /mnt/data/labs_r475/tests -p test_procurement_cross_po_budget_r475.py -v
```

**8/8 PASS** normal, **8/8 PASS** optimized, **16/16 executions**; `py_compile`
PASS for both exact files. The tests cover actual one-million budget rejection,
one-PO non-alerts, independent IDs, full typed parity, a global shared budget,
conservative overlap and numeric row order. These are *isolated exact-source*
tests, not a complete checkout. No real customer data was used.

A new `test_r475_cross_order_fanout_fails_before_csv_publication` method
in `test_procurement_integration_r5.py` takes that 1,001-order case through
the real CSV importer and requires no published report. This newly committed
full-engine test **has not yet run**; it raises the declared ProcureGuard
integration method inventory from 37 to 38. The independent Windows/Ubuntu
source workflow now explicitly invokes both the eight-method test and full
ProcureGuard CSV integration file under normal Python and `-OO -W error`.
Full repository, genuine Windows EXE, Defender, installed-app accessibility,
release checksum and premium entitlement/distribution tests remain **NOT RUN**.

## Exact-head acceptance / release hold

1. CI operator: investigate GitHub Actions runner eligibility, Actions account
   spending/billing limits, repository workflow restrictions and job failure
   annotations. R474 source run
   https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43894478143
   and Windows internal build
   https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43894478076
   both failed before recorded steps; the root cause is **not confirmed**.
2. Obtain an executed full checkout on the R475 exact head. Run the 38-method
   ProcureGuard CSV integration suite and all six apps' regression suite in
   normal and optimized modes; investigate any failures, do not waive them.
3. Independently review the 1,000,000-reference ceiling against real operational
   size distributions and future streaming-output requirements.
4. Only then perform real Windows 11 x64 build/install/smoke, Defender,
   keyboard/screen-reader, SHA-256 and secure premium download/license checks.
5. Keep this PR draft, stacked on R474, away from `main` and WordPress until
   independent QD review and explicit founder approval. No binary/download,
   license, entitlement or release-publication work is authorized by this PR.
