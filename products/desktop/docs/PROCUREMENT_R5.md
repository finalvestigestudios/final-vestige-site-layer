# ProcureGuard Studio Pro — R5 typed movements and price review policy

**Development-only. Do not use pre-release outputs to approve invoices, certify grant spending, or conclude fraud.**

## What changed

R5 adds local, deterministic **partial invoice, credit memo and returned-goods** accounting to the three-way review. It does **not** infer credits from negative quantities. Input quantities must be nonnegative. Instead, optional `event_type` explicitly selects `invoice` or `credit` on invoice rows; `receipt` or `return` on receipt rows. If absent, legacy positive invoice/receipt behavior is preserved.

The report retains legacy fields (`invoiced_qty`, `received_qty`, `invoice_total`) as **net** totals and adds `gross_invoice_qty`, `credit_qty`, `gross_invoice_total`, `credit_value`, `gross_received_qty`, and `returned_qty`. A row with a credit or return **always receives a review flag**, even when the net arithmetic balances; these are never automatically approved.

### Input columns

- Purchase orders CSV: `po_number,line,quantity,unit_price`
- Invoice CSV: `po_number,line,quantity,unit_price`, optional `event_type,document_id,related_document`.
- Receipts CSV: `po_number,line,quantity`, optional `event_type,document_id,related_document`.
- For a credit, provide its unique `document_id` and the original invoice's `document_id` in `related_document`.
- For a return, provide its own `document_id` and the original receipt's `document_id` in `related_document`.
- All documents must use the same PO and line for matching. Case-only spelling differences are accepted; punctuation-normalization links are separately flagged. Missing, wrong, or reused references remain visible as review exceptions.

Only `invoice,credit,receipt,return` are recognized in their respective inputs. Unknown event types and negative numeric quantities are rejected before any report is saved.

### Safe examples

The `examples/procurement-r5` directory contains **synthetic** PO/invoice/receipt CSVs demonstrating a 10-unit order, 10 units invoiced, a two-unit credit memo linked to that invoice, and two units returned against the original receipt. The net quantity is eight units in both invoice and receipt ledgers. This is a review scenario, **not** an approved payment.

### Pricing policy JSON (optional)

The desktop app exposes an optional local JSON picker. Without a policy file, the program uses **$0.01 absolute or 2% relative, whichever is larger**, preserving prior behavior.

Example `strict-price-policy.json`:

```json
{
  "version": 1,
  "price_absolute": "0.00",
  "price_fraction": "0.005"
}
```

`price_fraction` means a **fraction**, so `0.005` is **0.5%**, not 5%. Values must be decimal strings or integers (JSON binary floats are rejected). Absolute tolerance must be between $0 and $100, and fraction between 0 and 0.10. Unknown/duplicate keys, nonfinite values, wrong version, files over 8 KiB and invalid Unicode are rejected. **A widened policy receives `widened_price_policy_review` regardless of whether the price variance is otherwise inside tolerance**. Configurable thresholds create review labels, never payment authorization.

The export records the applied absolute/percentage thresholds, a SHA-256 policy fingerprint, and source row numbers. The evidence manifest hashes original files, output and policy JSON when supplied. Hashes support provenance but **do not certify validity or completeness**.

## Explicit review findings

`partial_invoice_review`, `partial_receipt_review`, `credit_memo_review`, `return_review`, `unlinked_credit_review`, `unlinked_return_review`, `normalized_credit_link_review`, `normalized_return_link_review`, `repeated_invoice_document_id_review`, `possible_duplicate_invoice_line`, `price_variance_above_2pct` (built-in policy), `price_variance_above_policy` (custom policy), `widened_price_policy_review`, and pre-existing PO/line normalization and quantity/price discrepancies. More than one finding may apply to the same PO line.

## Validation and outstanding release gates

22 pure review-policy unit tests passed **locally** on Python 3.13.5; a further 10 end-to-end CSV/engine tests were committed for integration verification. They are not claimed as passed until executed against the complete repository. R4's hosted Windows job was blocked before steps; R5's full suite, PyInstaller binary smoke, clean Windows 11 desktop accessibility, malware scan, signing, premium entitlement and QD review remain required.

The application is intentionally **offline**, does not transmit sensitive financial data, and never writes source CSVs. Do not publish premium builds at unprotected URLs or merge without QD and production approval.
