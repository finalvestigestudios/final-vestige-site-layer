# Labs R145 — hash-bound private source snapshots for offline replay (DRAFT / HARD RELEASE HOLD)

**Scope:** Four free report-verifier engines only: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite and Policy Delta Desk. The premium GrantAudit Studio Pro / ProcureGuard Studio Pro engines, activation, download and authorization paths are not touched. Nothing publishes a Windows binary, modifies WordPress or changes the main branch.

## Threat model and change

R143's independent local verifier hashed originals first, then reopened the **mutable original pathnames** when regenerating the output. It rehashed originals afterwards, catching ordinary in-place edits and path replacements; however it unnecessarily trusted a second pathname read for the actual engine input. R145 strengthens that boundary without claiming that filesystem metadata checks defeat a privileged attacker.

The verifier now:

1. Hashes each selected **regular** source via the existing descriptor/identity-checked SHA-256 guard. Rejects links, missing files and oversized files.
2. Reads a separate, descriptor-owned bounded snapshot (financial CSV <= 64 MiB; policy TXT/MD/CSV <= 10 MiB) and **requires its exact SHA-256 to equal the previously observed original digest**. Any divergence is a HOLD before an engine starts.
3. Places each verified snapshot in a distinct, randomly named private working directory, using a **source-index subdirectory plus its original basename**. This preserves the source labels in Policy Delta reports and avoids collisions for equal basenames from different original directories.
4. Hashes each private copy again and demands equality before replay. The four engines receive **only private, hash-bound copies**, not the mutable user-selected pathname. Reports are regenerated in the same temporary directory, then byte-for-byte compared with the original report.
5. Rehashes **the original path and report**, including metadata/identity checks, after replay. Both the pre/post source evidence and pre/post original report evidence must match. A normal source modification during replay still causes HOLD. The private working directory is removed on success and exceptions.

Financial formulas, Decimal rounding, mappings, invoice windows, original source row references, report schema, Unicode visibility, SHA-256 reports and human-review labels remain unchanged. The CLI still emits only a generic redacted HOLD on exceptions and a minimal digest/scope line on success. Source file contents and temporary locations are not printed or uploaded.

**Limitations:** These are reproducibility/custody checks, not digital signatures, historical authenticity proof, regulatory approval or protection from a privileged attacker tampering with source paths and timestamps or accessing local RAM/disk. Snapshot copies require temporary storage proportional to bounded source sizes; if there is insufficient disk or permissions, verification HOLDS rather than bypassing copies. Existing financial header-only replay remains HOLD. The verifier is a **source-tree helper**; it is not a newly distributed or marketed GUI capability. Physical Windows review remains necessary.

## Local development verification (synthetic files only)

From repo root, Python 3.12, with `PYTHONPATH=products/desktop`:

```sh
python products/desktop/scripts/safe_unittest_r145.py
python -OO products/desktop/scripts/safe_unittest_r145.py
```

The source-owned runner requires exactly **23 distinct named test methods**, zero skips/errors/failures, and a passing exit status. Mandatory CI: **23 × 2 Python modes × 2 operating systems = 92 executions**, plus the entire inherited normal/optimized suite, all six synthetic app smokes, Windows candidate builds and existing pre-release gates. Regression cases explicitly cover each of the four free engines using private copies, Policy Delta original basenames and BOM, equal basenames from distinct directories, old-to-snapshot hash mismatch, post-write private-copy corruption, original mutation during replay, source/report nonmutation, private-temp cleanup, Decimal/mapping compatibility, invoice-window options, header-only HOLD, premium denial and private CLI failure redaction.

**Review & release:** The R145 draft must pass its exact-head Ubuntu/Windows CI and independent QD review; neither local-source reproducibility nor green CI authorizes publishing. All six desktop utilities remain **UNRELEASED** pending independent physical Windows 11 evaluation including 46 keyboard/scale/accessibility observations, actual Defender/EDR, code signing, protected premium distribution, QD approval and founder authorization.
