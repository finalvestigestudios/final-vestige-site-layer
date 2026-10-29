# R36 — independent ProcureGuard evidence verification

**Development-only / offline / review-only.** This utility verifies current
file consistency for R35 ProcureGuard evidence directories. It does not
authorize purchases or payments, decide compliance, validate the truth of
financial records, establish legal chain of custody, or prove a review was
performed. No Windows executable, premium download, or site release is added.

## Scope and operator workflow

The R35 publisher creates a procurement-evidence-.../ directory with **two**
files: one procurement-three-way-YYYYMMDD-HHMMSS-ffffff.csv review report
and one evidence-manifest-YYYYMMDD-HHMMSS-ffffff.txt SHA-256 inventory.
Keep the original purchase orders, invoices and receipts CSVs. A review using
a custom price policy must also retain the exact original JSON file.

From the repository root, with a locally installed Python 3.12+ environment:

    PYTHONPATH=products/desktop python -m fvs_suite.procurement_verify \
      /private/procurement-evidence-example /private/po.csv \
      /private/invoices.csv /private/receipts.csv

If the review used a custom policy, provide it explicitly:

    PYTHONPATH=products/desktop python -m fvs_suite.procurement_verify \
      --price-policy /private/rules.json \
      /private/procurement-evidence-example /private/po.csv \
      /private/invoices.csv /private/receipts.csv

To detect a **coordinated rewrite** of the report, sources and editable
inventory, independently retain the SHA-256 digest of the original inventory
**at publication time** in a separately controlled system. On a trusted
Windows workstation, obtain the lowercase digest using PowerShell:

    (Get-FileHash -Algorithm SHA256 'C:\Private\procurement-evidence-...\evidence-manifest-....txt').Hash.ToLower()

Provide that independently retained 64-character lowercase value as the
--expected-inventory-sha256 <trustedhex> option during later verification.
Never calculate the trusted value from the potentially modified package you
are about to verify.

The command exits **0** for CONSISTENT (UNPINNED) or CONSISTENT (PINNED);
it exits **1** for INVALID. An unpinned check establishes only that supplied
current files match an editable manifest. Even a valid external pin proves
only agreement with the pinned inventory, not a digital signature or the
correctness of any procurement decision.

## Defensive validation

- Strict two-file layout and exact generated filename patterns. Unexpected
  files or missing files fail closed.
- Purchase order, invoice, receipt, then optional JSON policy must be
  supplied in the original order with the original basenames.
- Inventory is read through one checked descriptor, capped at **64 KiB**.
  Policy JSON is capped at **8 KiB**; original financial files are bounded by
  shared **64 MiB** inventory checks and reports by **256 MiB** checks.
- Symlinks, nonregular files and hard-link aliases among selected files are
  rejected. Detected replacements and concurrent modifications fail closed.
- Source, optional policy, and report SHA-256 values are independently
  recomputed in the exact inventory order and compared byte-for-byte.
- No source or report is modified; no network, telemetry, account or
  entitlement is required. CLI messages omit private paths, financial
  values, and SHA-256 pins.

**Limitations:** An actor who controls the input files and unhashed manifest
can produce a different self-consistent package. Without an independently
saved pin that coordinated modification cannot be identified. This tool
does not promise immutability after verification, defeat privileged writers,
prove cryptographic authorship, encrypt records, or approve compliance.
Keep evidence private; all exceptions require human review.

## Tests and release gate

    PYTHONPATH=products/desktop PYTHONWARNINGS=error \
      python -m unittest discover -s products/desktop/tests \
      -p 'test_procurement_verify_r36.py' -v
    PYTHONPATH=products/desktop PYTHONWARNINGS=error \
      python -OO -m unittest discover -s products/desktop/tests \
      -p 'test_procurement_verify_r36.py' -v

R36 helper tests passed on Linux Python 3.13.5, **32/32** normally and
**32/32** under -OO, against byte-for-byte copies of committed shared
snapshot, manifest, anchor and R35 publisher dependencies. Full repository
tests, Windows builds and smoke tests, premium entitlement checks, malware
scan, checksum and QD approval **remain unverified**. No publication of a
binary or premium download is permitted by this change.
