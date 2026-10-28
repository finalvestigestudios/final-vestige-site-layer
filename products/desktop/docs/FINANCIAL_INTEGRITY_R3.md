# Financial integrity R3 — review-only behavior (October 2026)

**Status:** pre-release draft. This branch is stacked on draft PR #76, itself stacked on PR #74. No live executable distribution, premium activation, or site publication is authorized. QD review of the exact source and Windows binary remains mandatory.

## Fail-closed imports

The CSV importer recognizes documented column aliases, but now rejects multiple aliases for **the same logical field** in a single file. For example, both `amount` and `paid` in one table, or both `id` and `reference`, are ambiguous even if their contents happen to agree. Operators must remove one ambiguous column before importing. Header case/spacing duplicates remain rejected. No source file is changed.

## Exact financial computations

Transaction and claim amounts use `Decimal` and are rounded to cents by the existing statement-money policy. **Purchase-order and invoice unit costs preserve up to eight meaningful decimal places without cent rounding**; quantities and extended totals remain exact until the final two-decimal report display. Thus 1,000 units at $0.005 correctly yield a $5.00 extended total, not $10.00. Unit costs with more than eight nonzero decimal digits fail closed rather than truncating. This does **not** implement multi-currency conversion, tax rules, discount logic, credit memo semantics, partial fulfillment allocation or bank reconciliation.

## Ambiguous identifiers and provenance

Normalization removes punctuation to make potential matches visible. It is **not** evidence that two differently spelled IDs refer to the same transaction.

- `normalized_id_review`: source transaction or claim IDs collapse to one search key despite differing by more than case.
- `normalized_program_review`: claim and ledger program labels differ beyond case.
- `normalized_budget_program_review`: budget / claim / ledger labels collapse to a program key despite differing beyond case. The warning appears **before** `within_budget` in the output.
- `normalized_po_key_review`: purchase-order IDs differ beyond case.
- `normalized_line_key_review`: purchase-order line labels differ beyond case.
- `duplicate_id_review;variance`: duplicate transaction/claim rows and monetary disagreement are **both** retained, rather than the duplicate flag hiding the variance.
- `possible_duplicate_invoice_line`: multiple invoice rows with the same normalized purchase order/line, quantity and unit cost need review. They may be legitimate partial invoices; no fraud finding is asserted.
- `price_variance_above_2pct`: an invoice line **or its total** differs from the order unit rate/extended amount beyond the greater of 2% or $0.01. Offset high and low line prices cannot silently net out.
- `negative_unit_price_review`: negative order/invoice unit price needs human review; credits and reversals are not modeled as a separate workflow.

Reports retain source row indices and **raw original identifiers** alongside normalized search keys. These raw fields are CSV-injection neutralized on export. The app does not autoapprove discrepancies or disburse funds.

## Test evidence / limitations

`products/desktop/tests/test_financial_integrity_r3.py` adds **19 focused regression cases** for imports, ledger/grant/procurement key collisions, source IDs, duplicate/variance flag combinations, exact sub-cent unit costs, offsetting invoice prices and negative prices. The pure `fvs_suite.review` helper also passed 8 local standard-library tests in the engineering runner on October 27, 2026 PT. **The combined repository suite and six packaged Windows binaries still require a GitHub Actions run that actually executes steps**; latest PR #76 runner failed before step initialization with no usable job logs (cross-repository pre-step failures were observed), so do not mark CI green.

Run when Actions is restored:

    $env:PYTHONPATH = "products/desktop"
    python -m unittest discover -s products/desktop/tests -v

Then verify all six `.exe --smoke-test` commands, SHA256, Windows clean-machine and accessible GUI behavior, antimalware screening, premium authorization and license flow before any download links are published.

## Remaining design and commercialization risks

User-configurable matching columns, per-customer tolerance settings, purchase-order currency/fees/taxes, multi-document reimbursement line allocations, report encryption, protected licensing, support workflows and release signing are not yet implemented. Human buyer validation is required to verify operational fit and willingness to pay.
