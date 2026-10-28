# Final Vestige Labs — Desktop Utilities

**Pre-release engineering branch. Not production-ready.** Four free utilities and two premium product prototypes share a local-only deterministic engine. Nothing uploads user documents, calls an LLM, or makes an automated compliance decision.

| Executable name | Tier | Inputs | Output |
| --- | --- | --- | --- |
| LedgerDiffLite.exe | Free | left and right transaction CSV | matched, missing, duplicate-ID, variance report |
| InvoiceTwinScout.exe | Free | invoice CSV | exact/review duplicate candidates |
| SpendMapLite.exe | Free | vendor spend CSV | monthly spend by normalized vendor/category and spike flags |
| PolicyDeltaDesk.exe | Free | old and new TXT/MD/CSV | unified text diff |
| GrantAuditStudioPro.exe | Premium (internal preview) | claims, ledger, budget CSV | reconciliation, budget exceptions, evidence SHA256 manifest |
| ProcureGuardStudioPro.exe | Premium (internal preview) | PO, invoice, receipt CSV | three-way matching exceptions and SHA256 manifest |

## CSV headers

Headers are case-insensitive; spaces are accepted in place of underscores. The importer also recognizes common synonyms listed in fvs_suite/engine.py.

- LedgerDiff: transaction_id, amount
- InvoiceTwin: vendor, invoice_number, amount, date
- SpendMap: vendor, amount, date, optional category
- GrantAudit: claims (transaction_id, amount, program); ledger (transaction_id, amount, program); budgets (program, budget)
- ProcureGuard: purchase orders (po_number, line, quantity, unit_price); invoices (same); receipts (po_number, line, quantity)

Dates: YYYY-MM-DD or MM/DD/YYYY. Amounts: decimal strings; currency symbols, comma thousands separators and accounting parentheses accepted. Currency conversion, multi-currency, complex split allocations, fuzzy name matching, and OCR are **not** supported in v0.1. Financial flags require human review.

## Local development

Python 3.12+ with Tkinter. From repository root:

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
    PYTHONPATH=products/desktop python -m fvs_suite.demo ledger

The six GUI entrypoints live under products/desktop/launchers. Windows CI uses PyInstaller and uploads **internal build artifacts only**; do not distribute or publish until tests, malware scan, clean-machine acceptance, release versioning, SHA256 and (preferably) code signing are complete.

## Invoice Twin Scout R4 candidate safety and scale

- Invoice exports with more than 200 transactions for one normalized vendor and amount are now supported when report density is manageable. Near candidates use a chronological seven-day inclusive sliding window, rather than comparing all rows across all dates.
- Exact normalized invoice-key occurrences are anchored to the first source row regardless of dates; same-vendor, same-amount near candidates use a seven-day window. No label implies a duplicate *payment* or fraud determination.
- Original vendor names, invoice numbers, dates, and CSV source row references are all exported. Independent review flags indicate normalized-key collisions, exact-invoice amount mismatches, or distant dates; all need human confirmation.
- A dense input producing more than 100,000 candidate review pairs is explicitly rejected **before saving any report**. Narrow the input by vendor/date; reports are never silently truncated.
- See [Invoice Scale R4 specification](docs/INVOICE_SCALE_R4.md) for complexity, test cases, scope and limitations.

## Packaged-executable smoke verification (internal CI)

Each portable Windows executable accepts `--smoke-test`. It runs its actual core workflow against disposable **synthetic test fixtures** under the system's temporary directory, validates a known exception or diff, deletes temporary data, and exits with status 0 only if all checks pass. GUI is never initialized and no network connection is used.

    .\dist\LedgerDiffLite.exe --smoke-test
    .\dist\InvoiceTwinScout.exe --smoke-test

CI launches **all six** EXEs as real processes after packaging, checks their exit codes and SHA256 fingerprints independently of the packaging step, and only then uploads a private short-retention artifact. This is a **packaging smoke check**, not yet a substitute for Windows 11 clean-machine/GUI testing or a malware scan.

## Import integrity and review policy

- Duplicate or blank normalized CSV column headers are rejected rather than arbitrarily choosing a column.
- A transaction/grant ID pair equal only after punctuation normalization (for example, `INV-100` versus `INV100`) receives `normalized_id_review` instead of `matched`; any simultaneous amount variance is separately retained. This protects against incorrect automated reconciliation.
- Case-only ID differences are treated as equivalent, but punctuation is **not** silently asserted to be the same real-world identifier.
- Amount parsing uses Python `Decimal`, not floating point; invalid and nonfinite amounts are rejected.
- CSV report cells beginning with spreadsheet formulas are neutralized to reduce formula-injection risk when opened in spreadsheet software.
- Duplicate IDs, ambiguous matches and all policy/audit flags require human judgment; the software does not authorize payments or certify compliance.


## ProcureGuard Studio Pro R5 — credits, returns, partial deliveries and reviewed tolerances

- Explicit positive `invoice` versus reversing `credit` and positive `receipt` versus reversing `return` events; negative numeric quantities are rejected. Untyped legacy inputs remain positive transactions.
- Optional invoice/receipt `event_type`, `document_id`, and `related_document` columns provide document-level review. Unlinked credits/returns, amount deviations, repeated invoice IDs and normalized-reference collisions remain visible as exceptions.
- Legitimate identical partial invoice amounts with **different, explicit invoice document IDs** are not automatically misclassified as duplicate entries. When document IDs are absent, conservative duplicate review stays enabled.
- Gross and net quantities and invoice values are reported separately, preserving audit trails. All credit memos and returns remain explicitly flagged for a human reviewer, even if arithmetic balances.
- Optional local price policy JSON is accessible from the **ProcureGuard Studio Pro** desktop GUI. Values are bounded, schema-checked, Decimal-exact and fingerprinted in the report/evidence manifest. Looser tolerances always produce a visible review flag.
- A complete synthetic pilot scenario, documentation, and source samples are in [PROCUREMENT_R5.md](docs/PROCUREMENT_R5.md). This is a **development prototype**, not an entitlement-protected commercial edition.


## GrantAudit Studio Pro R6 — linked split allocations and credit memos

- Optional claim-ledger source links enable **many claim lines across grant programs to reconcile to one ledger transaction**. This avoids incorrectly treating legitimate split reimbursements as missing records. Splits always remain flagged for human review.
- Use claims CSV headers `claim_id,amount,program,ledger_reference`; optional `claim_type` and `related_claim` support explicit credits (positive amount with linked original claim). The original three-file output and legacy single-ID matching remain supported.
- Claims are totaled per source ledger reference and program budgets per claim program, with gross/credit/net amounts, original row references, and source identities in the output. Ambiguous source links, repeated claim IDs, unlinked/cross-program/excessive credits, negative values and missing budgets are visibly reviewed or rejected.
- A credit-related column without a source ledger_reference is a fail-closed import error, preventing silent positive-credit accounting in legacy mode.
- Includes a synthetic two-program split + claim credit scenario in [R6 documentation](docs/GRANT_ALLOCATIONS_R6.md), 24 additional repository regressions, and a linked-mode packaged-executable smoke check. The R6 code has **not** passed full repository or Windows packaged-executable validation yet. Premium licensing remains unimplemented.

## Release gates

1. Independent sample and edge-case test suite (money, CSV injection, encoding, duplicates, malformed input).
2. Binary smoke test on a clean Windows 11 machine; accessible keyboard UI.
3. Privacy and security review, including local file handling, report CSV injection mitigation, log redaction.
4. Premium entitlement / purchase workflow and license agreement before sales.
5. SHA256 checksums, release notes, support address and verified live download links.
6. Human approval through the Final Vestige site-layer QD/production process.

See [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
