# R143 — local report replay verifier (DRAFT / HARD RELEASE HOLD)

The four **free** standalone engines can now be checked offline against an existing exported report, its original files and the operator-selected settings. The verifier re-runs the current engine in an owner-private temporary directory and compares the **exact report SHA-256 bytes**; it also verifies original report and source file metadata and hashes before and after the run. Nothing uploads, edits original inputs, overwrites saved reports, signs a document, or makes a fraud/compliance determination. Premium engines and access gates are deliberately excluded.

## Invocation (source tree, private workstation)

From the repository root, with Python 3.12 and PYTHONPATH set to products/desktop:

    python -m fvs_suite.replay_verify --kind ledger-diff --report "report.csv" --source "left.csv" --source "right.csv"
    python -m fvs_suite.replay_verify --kind invoice-twins --report "review.csv" --source "invoices.csv" --window-days 7
    python -m fvs_suite.replay_verify --kind spend-map --report "report.csv" --source "spend.csv"
    python -m fvs_suite.replay_verify --kind policy-delta --report "changes.txt" --source "old.txt" --source "new.txt"

LedgerDiff accepts its original --left-match-column, --right-match-column, --left-amount-column and --right-amount-column arguments. **Column selections and invoice windows must match those used to create the report.** Exact comparison depends on using the same source bytes and compatible/current engine revision; future engine upgrades may legitimately change report serialization. No executable is shipped or released by this branch.

A successful command prints only the selected free-product identifier, report SHA-256 and source count. Failed checks print a generic HOLD message without customer paths or CSV cells; no partial output is left in the output folder.

## Safety contract and limitations

- SHA-256 comparisons and exact deterministic replays detect changes relative to **selected** sources and **current local code**, but do **not** authenticate who created the sources, establish correctness of source transactions, certify a historical engine version, or replace digital signing.
- Header-only financial CSVs deliberately fail closed: their empty report rows contain no embedded source SHA-256 and could otherwise accidentally replay byte-identically from unrelated input files. An empty-result user must keep their original files and manually review custody until a future explicitly source-bound empty-result receipt is implemented. Policy Delta's text header always includes both source fingerprints and is eligible for replay.
- Source and report paths must be stable regular files; source size guards are 64 MiB for financial CSV and 10 MiB for policy TXT/MD/CSV; report hash guard is 256 MiB. Filesystem metadata checks are not protection against a privileged attacker or a successful cryptographic collision.
- Replays use tempfile.TemporaryDirectory, existing atomic writers and no network calls; source byte fingerprints are local and never automatically transmitted. This is a **developer/source-tree verification utility**, not a marketed GUI feature or a substitute for physical Windows 11 tests.
- 23 synthetic regression methods exercise valid replays, per-product tampering, changed source files, wrong settings, zero-result HOLD, redacted CLI errors, and no overwrite. Required CI is Ubuntu + Windows, each Python normal and -OO, **23 × 2 × 2 = 92 named executions** in addition to existing full suite/native Windows/crypto gates. A CI failure is a HOLD.

**Release unchanged:** all six EXEs remain UNRELEASED. No premium executable, public download, code signing claim or WordPress deployment; physical Win11 46 hands-on accessibility checks, real Defender/EDR, protected premium distribution, independent QD approval and founder authorization are required.
