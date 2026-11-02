# R137 — GrantAudit Studio Pro budget provenance (private draft / release HOLD)

Premium reviewer workflows need to locate the exact claim and authorized budget source cells that underpin a per-program exception. Earlier linked-mode budget reports exposed claim rows but not budget source lines, while legacy-mode budget reports exposed neither. The SHA-256 evidence manifest proves three overall inputs but forces a reviewer to search for the program manually.

## New per-program columns

Both legacy and linked allocation modes append `claim_rows`, `budget_rows`, `claim_source_sha256`, `ledger_source_sha256`, and `budget_source_sha256` to the **grant-budget-check** CSV as applicable. Linked mode already had `claim_rows`; its original position and semantics remain unchanged, and the four other fields are appended. No existing column is removed or renamed.

- `claim_rows`: semicolon-separated **physical starting line numbers** of contributing claim CSV records (including credits in linked mode), in original source order. Blank for a budget-only program.
- `budget_rows`: the physical starting line of that normalized program's budget CSV record; blank for a missing budget. This is **not** a claim of appropriations eligibility or authorization.
- The three `*_source_sha256` fields: lowercase byte-exact SHA-256 digests captured during the same validated source snapshots used by the reconciler and independently rechecked by the manifest writer. They are repeated even when a program has no budget row, to identify the reviewed source file, **not** to invent a missing source record.

All money remains Decimal-safe and original amount/status logic is unchanged. Physical lines are not CSV logical record ordinals: quoted embedded newlines can make lines skip. Program identity is normalized according to existing suite policy; collision flags continue to require human review. Use the original input CSV plus its digest to interpret each cited line. If original files change after parsing, manifest publication still fails closed.

## Test and release contract

`products/desktop/tests/test_grant_budget_custody_r137.py` contains **18 synthetic real-CSV integration tests**: legacy/linked report fields, quoted multiline/BOM physical citations, missing/extra budget programs, credit lineage, cross-program row isolation, deterministic exports, immutable sources, exact SHA/manifest agreement, direct linked API, normalized-program review, low-precision Decimal stress, duplicate-budget no-output failure, and report no-overwrite. The strict zero-skip method-inventory runner is `products/desktop/scripts/safe_unittest_r137.py`.

Workflow `.github/workflows/desktop-build.yml` requires these 18 methods in Python normal and optimized `-OO` modes on Ubuntu and Windows (72 targeted method executions only **after** both OS jobs complete). Existing six-app package, premium lock, private artifact, encryption, accessibility, and QD protections remain unchanged.

**No customer data, network transmission, unlocked premium app, public executable, live-site publication, compliance approval or payment authorization is part of this change.** All six Windows x64 applications remain **UNRELEASED** pending independent protected binary custody, authenticated R9 report, 46 physical Windows 11 checks, genuine Defender/EDR scan, code signing, authenticated premium distribution, QD review and founder authorization.
