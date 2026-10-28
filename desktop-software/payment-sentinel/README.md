# Payment Sentinel — pre-release manual QA and data contract

**Status:** Offline Python prototype; not a signed or licensed Windows release. No checkout and no public download are enabled.

Payment Sentinel checks accounts-payable CSV exports for *possible* repeated invoices, payments of the same amount near the same date, inconsistent vendor account identifiers, and unusual vendor amounts. Flags are review prompts, **not allegations of fraud** and not a substitute for ledger approval or bank controls.

## Quick start (development only)

Python 3.11 or later, standard library only:

    python desktop-software/payment-sentinel/payment_sentinel.py \
      desktop-software/payment-sentinel/samples/fictional-payments.csv \
      --report payment-review.html

For Windows, use one command line rather than the shown Unix-style continuation. Run the script without arguments to open the desktop GUI.

Choose a new report filename. Existing files are never overwritten. Supported export formats are HTML, spreadsheet CSV, and structured JSON. The application does not upload financial records or use the network.

## Required data

Provide a UTF-8 / UTF-8 BOM CSV with one header row and at least these logical fields:

| Logical field | Accepted examples | Rules |
| --- | --- | --- |
| Vendor | Vendor, Vendor Name, Supplier, Payee | Required, nonempty searchable identifier |
| Invoice | Invoice, Invoice Number, Bill Number | Required, nonempty searchable identifier |
| Amount | Amount, Payment Amount, Paid Amount, Total | Required finite amount, up to 2 decimal places |
| Date | Date, Payment Date, Paid Date | YYYY-MM-DD or MM/DD/YYYY |
| Account | Bank Account, Vendor Account, Account Number | Optional; used to flag possible inconsistencies |

A file must have **exactly one** recognizable column for each logical field. For example, both \`Amount\` and \`Payment Amount\` in one file are ambiguous and will be rejected. Blank and duplicate column headings are rejected. Unrecognized extra columns are ignored. Unicode vendor names are retained in candidate-matching keys instead of collapsing to the same empty identifier.

Input limits are 80 MiB per file and 200,000 payment rows. These are protection limits, not validated capacity claims. A full SHA-256 digest is recorded before and after import; a source change during processing aborts the report. The digest is included in review exports to identify which input was analyzed. **Bank account numbers are not exported.**

## Result states and exit codes

- \`NO_FLAGS\` — at least one valid payment was reviewed and no configured rule produced a flag. This does **not** mean all payments are correct or authorized.
- \`REVIEW\` — at least one exception was found, including any excluded invalid rows. The report identifies the physical starting CSV line of each flagged row, including records with quoted multiline fields.
- \`INCOMPLETE\` — no valid payment records were available; do **not** interpret this as a clean result.
- CLI exit \`0\`: reviewed records with no configured flags.
- CLI exit \`1\`: review findings require attention.
- CLI exit \`2\`: incomplete input, validation or I/O error, including a refused overwrite.

## Test data

The included \`samples/fictional-payments.csv\` is **fictional** and should trigger repeated-invoice review, same-amount-near-date review, multiple-account review, and a rejected nonfinite amount. The amount and vendor patterns are illustrative and do not represent real misconduct.

## Manual acceptance checklist

1. Run unit tests: \`python -m unittest discover -s desktop-software/payment-sentinel -p "test_*.py" -v\`.
2. Open the GUI and review the fictional sample. Check that no network connection is required and that all input files remain unchanged.
3. Export HTML, CSV and JSON to three *new* filenames; confirm source SHA-256 and review status are visible and spreadsheet data is safe.
4. Attempt export to an existing report filename or to the original input filename: operation must fail without modifying either file.
5. Change the input file after review, then try exporting from the GUI: the application must reject stale output and require a fresh review.
6. Test headers with duplicate or competing aliases; incomplete/corrupt CSV; UTF-8 vendor names; quoted newlines; zero valid rows; and a file modified mid-scan.
7. Build the Windows executable, install and uninstall on a **clean Windows machine**, check Start-menu shortcuts and CLI/GUI behavior, and record SHA-256 of the actual installer.
8. Before public release: independent code review, malware scanning, code signing, payment entitlement validation, support policy, and reproducible release notes.

## Known limitations

No automated invoice-image parsing, bank feed connection, tax validation, purchase-order matching, or vendor identity verification. Candidate matching may produce false positives; the review must be adjudicated by a human. The CSV exporter neutralizes spreadsheet-formula prefixes in report fields; it does not export original vendor bank details. This is a local review utility rather than a comprehensive fraud detection system.
