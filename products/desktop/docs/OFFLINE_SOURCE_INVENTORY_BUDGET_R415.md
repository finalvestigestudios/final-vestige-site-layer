# R415 — Finite offline source inventory (INTERNAL / NO RELEASE)

Tracked by [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73), stacked on R414 draft #2411, not production main.

## Measurable improvement

R414 checks launcher routing and SHA-256 custody, but places no overall bound on import-root file count, nested directories or aggregate bytes. An enormous collection of small source/assets can cause runaway directory walking and repeated hashing across twelve source-only tests.

R415 rejects imports before rglob hash inventory creation or any child subprocess when either required source root exceeds the **combined** limits of 512 files, 128 directories including two roots, 16,000,000 bytes total, or 2,000,000 bytes per file. Empty assets fail closed, consistent with the existing hash pass. The fixed rejection does not disclose names, paths or private data. The budget is rechecked before/after every child.

Limits apply to all six entrypoints and all import-root assets. This is engineering source custody, not a restriction on customer CSV data. os.walk still enumerates an immediate directory before the code can reject its entry count, so this is not a comprehensive filesystem-resource sandbox.

## Evidence and limitations

The new committed regression module covers 12 cases: 6 × 2 valid synthetic launchers; file limits across both roots; nested/empty directories; aggregate 16 MB limit; oversize and zero-length assets; data-safe error text; reset after rejection; stable source hash. A separate local Linux *reconstruction* of the new preflight passed corresponding 12/12 normal and 12/12 optimized tests (24/24); Python syntax compilation passed. **These were not executions of the committed full checkout or exact committed regression module.** Hosted Windows and Ubuntu CI must run the committed file to establish integration evidence.

Run on a trusted full checkout, with the existing desktop dependencies installed:

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_source_inventory_budget_r415.py
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_source_inventory_budget_r415.py
    python -I products/desktop/offline_source_smoke_r408.py

On Windows PowerShell set $env:PYTHONPATH='products/desktop' before the first two commands. If trusted checkout inventory exceeds bounds, review the files and justification before changing them.

## Hard hold

All six products remain unreleased. No financial rules, original customer inputs, Decimal semantics, audit approval, premium licensing, executable, download URL, WordPress content or production branch changed. Next: restore GitHub Actions runner allocation, run complete Windows/Ubuntu regressions on the exact SHA and genuine Windows x64 builds, Defender/NVDA checks, SHA-256 release digests and premium access-denial tests. Independent QD and explicit founder approval remain prerequisites for merge/release.
