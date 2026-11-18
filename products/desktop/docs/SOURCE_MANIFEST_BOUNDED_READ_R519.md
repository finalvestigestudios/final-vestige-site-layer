# Final Vestige Labs R519 — bounded immutable-source manifest read

**Status: DRAFT; independent QD + founder HARD HOLD.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked exclusively on R518 draft [#2982](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2982), not production `main`.

## Verified problem and change

The R509 source runner validated the 416-command manifest's 64-KiB maximum **after** calling `Path.read_bytes()`. Although the SHA-1 Git blob pin correctly rejected altered manifest content, an arbitrarily enlarged regular manifest could be fully allocated in memory before that rejection.

The runner now calls `read_manifest_bounded(MANIFEST)`: one `Path.open("rb")` and a single `read(65_537)`. It rejects more than 65,536 bytes **before** SHA pin validation, retains exact original bytes for the existing `load_commands` hash/count/allowlist checks and converts read failures into an exception without private `__context__` or `__cause__`. The `main()` path still preflights the unlinked manifest location and uses `verify_source_snapshots=True` for all subprocesses. The original manifest content, 416 commands, and CI workflow are unchanged.

The change bounds the read request, not an atomic file-open race or a universal OS memory budget. It does **not** authorize a release.

## Test coverage and evidence (2026-11-18)

Nine regression methods were committed to the **existing SHA-pinned source-matrix test module** `products/desktop/tests/test_source_evidence_runner_r509.py`. They cover the real 43,737-byte, 416-command manifest; exact ordinary bytes; acceptance at 65,536 bytes (digest validation remains separate); rejection of a 1,000,000-byte file; the exact 65,537-byte read request; missing private paths; read errors with no chained private exceptions; invalid stream result types; and `main()` calling the bounded helper before the pinned command validator.

**Executed locally:** six isolated Linux CPython representative tests of the exact R519 bounded-reader implementation passed under standard `python -B -W error` and optimized `python -OO -B -W error`: **6/6 + 6/6 PASS**. They covered regular, exact-size, oversized, private missing path, bounded read request and invalid stream results. This was a standalone probe, **not** an execution of the full newly committed nine-method regression class. GitHub-connected file reads and 416-command inventory metadata were inspected; the complete repository suite and native Windows tests remain unexecuted.

## Blocker and next highest-impact step

At the inherited exact R518 commit `ed80d3246da7d2e2bd7937fa5e13c85f899c0b86`, all three workflow runs failed **before any test step**: [source #44272465582](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44272465582), [identity #44272465464](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44272465464), [build #44272465515](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44272465515). All six job payloads returned `steps=null`; root cause still unknown. Restore runner eligibility by having the GitHub repository/account administrator check Actions billing/spend limit, organization workflow policy and runner availability, then rerun source/Windows checks on the exact R519 commit.

Before publication, independently execute the entire 416-command source matrix and Windows x64 release matrix, smoke-test each distinct utility (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro), verify Windows Defender and accessibility, produce and check SHA-256/identity receipts, and validate private premium entitlements and download access.

**Release hold:** No merge, deployment, CMS publication, public untested executable, unrestricted premium binary, payment/compliance auto-approval or bypass of independent QD review and explicit founder authorization. Local-first financial privacy, Decimal-safe money calculations, deterministic audit evidence and human review remain intact.
