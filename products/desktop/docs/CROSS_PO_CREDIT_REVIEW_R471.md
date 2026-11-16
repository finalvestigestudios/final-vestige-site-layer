# R471 — cross-PO credit memo reuse with source-row custody

**Status: DRAFT / QD HARD HOLD.** This is source-only review functionality,
not fraud detection, a payment authorization, a customer release, or evidence
that Windows x64 builds work. Stacked on R470 draft #2734, not production main.

## Why this change exists

R470 flags the same credit memo within a single normalized PO/line, but a credit
identifier occurring once in PO P1 and again in PO P2 escaped that flag. Such
offsets can reduce both balances. It can also be legitimate for one credit
document to reference more than one order. Never deduplicate financial rows
or equate a source-label collision with misconduct.

## Implemented behavior

- Before per-line review, build an index of **typed credit** events over the
  invoice CSV already parsed from a verified source snapshot.
- Use the same normalized document identity policy and normalized PO keys as
  ProcureGuard; ignore missing/blank credit identifiers.
- When a nonblank normalized credit ID occurs in **at least two distinct POs**,
  add `credit_document_cross_po_review` to every affected PO/line.
- Add `cross_po_credit_source_rows` containing candidate **physical invoice CSV
  row numbers** in stable numeric order, separated by semicolons. The existing
  source SHA-256 and local source CSV identify which actual records to inspect;
  this new column contains no additional private document labels.
- The same credit memo legitimately spanning multiple lines of **one PO** does
  not trigger this cross-PO flag. R470's same-PO/line repeated-ID guard remains.
- Preserve every movement, source row, exact Decimal gross/net/credit amount,
  pre-existing exception flag, source digest, and human compliance decision.
  The report never approves a credit, changes an amount, or validates identity.

## Artifacts

- `fvs_suite/procurement_cross_po_r471.py`: isolated pure candidate-row index.
- `fvs_suite/procurement.py`: invoke before per-line review; add status and
  per-line candidate evidence to private CSV output.
- `tests/test_procurement_integration_r5.py`: **five** new actual CSV-output
  regressions: normalized cross-PO collision, legitimate same-PO multiple
  lines, distinct IDs, blank IDs and non-credit classification.
- `offline_regression_gate_r459.py` and its test: descriptor-verified source
  custody for the new helper, plus an explicit tamper-sensitive assertion.

## Reproduction / honest evidence

A local Python 3.13 execution of the helper source whose Git blob SHA matches
the committed GitHub blob can run:

```sh
python -m unittest -v test_cross_po
python -OO -W error -m unittest -v test_cross_po
```

The isolated local harness has eight focused helper tests per mode (16 method
executions), exercising normalization, distinct-order scoping, same-order
multi-line cases, blank IDs, non-credit labels, numeric physical-row ordering,
and multiple collision groups. These **are not** executions of the five newly
committed CSV integration tests or the complete repository.

**Still required** before any release: run the full ProcureGuard CSV suite on
the exact branch; run the complete six-app regression/source-check matrix in
both modes, genuine Windows x64 builds and installed-app smoke/accessibility,
Defender, signed/unsigned release disclosures, SHA-256 checksums, and verified
premium entitlement + access-controlled delivery. Exact-head GitHub CI must
actually execute tests; a job with `steps=null` is not evidence of passing.

## Approval boundaries

Four free products and two premium products stay distinct. No customer CSVs,
optional network processing, telemetry, public installers, licenses or
unguarded premium download links are introduced. Independent QD review and
explicit founder approval are required before merger, site edits or publishing.
