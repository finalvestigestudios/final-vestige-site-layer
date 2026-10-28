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


## Release gates

1. Independent sample and edge-case test suite (money, CSV injection, encoding, duplicates, malformed input).
2. Binary smoke test on a clean Windows 11 machine; accessible keyboard UI.
3. Privacy and security review, including local file handling, report CSV injection mitigation, log redaction.
4. Premium entitlement / purchase workflow and license agreement before sales.
5. SHA256 checksums, release notes, support address and verified live download links.
6. Human approval through the Final Vestige site-layer QD/production process.

See [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
