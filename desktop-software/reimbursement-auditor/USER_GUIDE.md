# Reimbursement Auditor 0.2 — review guide (development build)

**Status:** Premium prototype; not approved for sale or public download. The
Windows installer is currently unsigned. Checkout, licensing, and independent
Windows acceptance have not passed release gates.

## What it does

Compare a **claims CSV** to a human-verified **support index CSV** and a local
folder of supporting attachments. It identifies ambiguous, missing, duplicated,
or inconsistent references and produces HTML/JSON review reports.

It **does not read or authenticate PDF/receipt contents**, prove that a vendor
was paid, determine eligibility, or certify compliance with program rules.
A zero-exception result means only that these *specified automated checks*
found no exceptions in the provided files.

## Required inputs

Claims CSV: vendor, invoice, amount. Support index CSV: vendor, invoice,
amount, file. Supported synonyms include "vendor name", "invoice number",
"claimed amount", and "evidence file"; two aliases for the same required
column are rejected rather than being arbitrarily selected.

Use decimal dollars, e.g. 1250.00, not accounting formulas. Each support
index row should reference a regular file beneath the chosen attachment
folder using a forward-slash relative path, such as receipts/invoice-1.pdf.
References to parent directories, symlinks or absolute paths are rejected or
flagged. If invoice support spans multiple index rows, review the
DUPLICATE_SUPPORT_REFERENCE warning; the engine does not decide allocations.

CSV import is limited to 32 MiB per source. Packet scans are limited to
5,000 evidence files and 2 GiB aggregate evidence size; exceeding either
limit aborts the audit instead of silently dropping entries. No network
requests or telemetry are necessary.

## Interpreting statuses

- NO_FILE_OR_INDEX_EXCEPTIONS: no exceptions in these limited checks.
- REVIEW: findings require a human reviewer (for example, amount
  discrepancies, reused support, missing or unindexed attachments).
- INCOMPLETE: no reliable clean verdict is possible; examples include
  unreadable entries, invalid rows, or empty input datasets. Resolve the
  errors and rerun.

The JSON report includes SHA-256 digests and byte lengths of source CSVs
and evidence files. These fingerprints establish **byte identity for later
comparison**, not authenticity of the original evidence. Store exported
reports securely because they can expose names and review findings.

## Running

Windows graphical version: choose the claims CSV, support index CSV, and
attachment folder. Select Audit packet, inspect findings, and export a report
**outside** the evidence folder.

Python CLI (Python 3.11+):

    python reimbursement_auditor.py claims.csv support.csv attachments --report review.json

Or use review.html for an HTML review report. Exit codes: 0 = checks found
no exceptions; 1 = findings; 2 = input, scan, or export failure.

An export is blocked if any source or evidence file has changed since the
audit. An existing report is never overwritten. The GUI also requires
re-auditing after changing selected input paths.

## Windows release acceptance — must pass before sales

1. Run all tests: python -m unittest discover -s desktop-software/reimbursement-auditor -p "test_*.py" -v
2. On Windows, build with PyInstaller and Inno Setup, install, launch GUI,
   run CLI against representative realistic files, export JSON/HTML, uninstall.
3. Confirm errors for changed files, symbolic links, inaccessible folders,
   malformed data, mixed-case filenames, long paths, and Unicode vendor names.
4. Verify code-signing, malware scanning, SHA-256 installer checksum and
   actual downloaded-installer byte equivalence.
5. Verify offline operation. Obtain customer interviews before finalizing
   premium pricing, claims, or policy-specific rules.
6. Implement secure payment, entitlement, and gated fulfillment before
   activating a premium download button.

## Safe handling

The program never intentionally edits its source CSVs or attachment files.
Reports are written exclusively to new filenames outside the evidence folder.
The file list in an unsigned report is not tamper-proof against an attacker
who can replace the entire report; keep trusted copies in a controlled
location. Never upload real client documents into example fixtures or CI.
