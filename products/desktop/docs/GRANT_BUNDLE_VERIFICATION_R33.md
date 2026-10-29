# R33 — Offline GrantAudit evidence consistency verification

**Source-only draft. No Windows binaries built or approved.** This extends
R31 source-byte binding and R32 three-file publication with a separate
**read-only check after publication**.

A published GrantAudit directory can be copied or edited after its manifest
was written. R32 makes initial publication all-or-nothing, but does not check
whether a later copy still matches the inventory.

The new fvs_suite.grant_verify.verify_grant_bundle takes the original claims,
ledger and budgets CSV files, two exported report CSVs (located inside the
operator's bundle directory) and inventory text. It recalculates all **five**
SHA-256 entries using the existing bounded manifest_guard.inventory_text
implementation and compares the **exact inventory bytes**, including entry
order and escaped basenames. It enforces exactly three regular export files,
rejects symlinks/nonregular members and detects ordinary concurrent edits.

## Operator invocation — source checkout only

From the repository root on Linux:

    PYTHONPATH=products/desktop python -m fvs_suite.grant_verify /path/grant-evidence-dir /path/claims.csv /path/ledger.csv /path/budgets.csv

From the repository root in Windows PowerShell:

    $env:PYTHONPATH = "products/desktop"
    python -m fvs_suite.grant_verify "C:\Evidence\grant-evidence-dir" "C:\Source\claims.csv" "C:\Source\ledger.csv" "C:\Source\budgets.csv"

Exit code **0** means all five selected files currently match the plaintext
inventory, and the exact bundle layout passes verification. Exit code **1**
means missing, changed, malformed, ambiguous or unreadable evidence, or a
failed SHA-256 comparison. Messages omit private file paths and data.
The verifier does not create, modify, approve, upload or transmit anything.
It is **not** a released Windows executable. Packaging and GUI integration
require native Windows verification and QD approval.

Original **basenames** must be preserved; their folders may differ. The source
argument order is **claims, ledger, budgets**. Checking without all three
original source files is intentionally unsupported: the two exported CSVs
alone would not establish source/report consistency.

## Controls and limitations

- CSV sources: existing 64 MiB per-file inventory cap.
- Exported CSV reports: existing 256 MiB per-file inventory cap.
- Inventory text: separate **64 KiB** size cap from a stable descriptor.
- Offline only, no telemetry, account, license or premium download changes.
- Consistency is not **authenticity**. Inventory SHA-256 text is neither signed
  nor keyed: changing files and all hashes could manufacture a consistent
  bundle. A separately trusted checksum or signature is needed to authenticate.
- Passing is a **point-in-time observation**, not a filesystem lock or proof
  against privileged writers, later edits or storage faults. All financial
  findings still require human review.
- This check does not decrypt vaults or automatically locate original CSVs.

## Testing and outstanding release gates

23 synthetic tests in tests/test_grant_verify_r33.py cover current content,
both report tampering modes, same-length source mutation, altered inventory,
source ordering, preservation of original files, escaped control characters,
missing/extra files, links, hard-link aliases, oversized inventory, simulated
concurrent changes and CLI exit codes/privacy.

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_grant_verify_r33.py' -v

Full integrated repository regression, Windows x64 native build/smoke/AV/SHA-256
verification, premium access testing and QD approval remain mandatory. This
feature changes no Decimal money logic, compliance decisions or site content.
