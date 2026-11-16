# R470 — repeated credit-memo source IDs remain reviewable

**Status:** DRAFT / QD HARD HOLD. Stacked on R469, not production `main`.
This is an offline financial review safeguard, **not an approval** or fraud finding.

## Concrete ProcureGuard gap

A single PO/line could include the same credit memo twice. R469 counted repeated
*invoice* document IDs and repeated *receipt/return* IDs, but not repeated
credit-memo IDs. Because both credits reduce net quantity and value, a reviewer
could miss the specific duplicate document even though a generic
`credit_memo_review` status was already present.

R470 checks nonblank, normalized `document_id` values on `credit` rows,
scoped to the existing PO/line reconciliation group. Reuse of a normalized
credit ID adds `repeated_credit_document_id_review`. The flag **does not**
remove or combine a financial row, alter a calculated amount, infer intent, or
authorize a payment.

- `CM1` + `CM1`: repeat flagged.
- `C-M1` + `CM1`: normalized-key collision flagged, original spellings
  retained in exported source-document evidence.
- `CM1` + `CM2`: no repeat flag.
- Two blank credit IDs: existing `unlinked_credit_review` remains; blanks
  do not become a fabricated shared identity.
- Existing per-credit source physical rows and credit target-line evidence
  remain in the report. Source snapshots and SHA-256 evidence are untouched.

**Scope limit:** This guard checks reuse *within a PO/line*. It does not prove
global uniqueness across other PO lines or unrelated imported data. A human
must review underlying source documents and decide what action, if any, follows.

## Repeatable regression entrypoints (complete trusted checkout required)

From `products/desktop`:

```sh
python -W error -m unittest discover -s tests -p test_procurement_integration_r5.py -v
python -OO -W error -m unittest discover -s tests -p test_procurement_integration_r5.py -v
python offline_regression_gate_r459.py
```

Four new end-to-end CSV/export regressions cover same ID, normalized collision,
distinct IDs, and blank IDs. The existing six-app offline gate already includes
this module and fingerprints both engine and test inputs through the full
six-app import-root/source inventory. Passing these tests remains mandatory
before any release claim.

## Release hold and external dependencies

The parent R469 CI jobs failed before executing steps; no Windows x64
packaging/Defender/accessibility result or verified premium entitlement/download
exists for R470. Restore Actions runner eligibility/billing, run this exact
commit on native Windows and Ubuntu, inspect artifact checksums and installed
app behavior, then submit independent QD and founder approval. Do not merge,
publish download links, expose premium binaries, or bypass the QD workflow.
