# Labs R133 — LedgerDiff 400% native Tk reflow (DRAFT / RELEASE HOLD)

## Reproduced Windows CI blocker (2026-11-02 UTC)

[R132 exact-head CI #41419512396](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41419512396), SHA `08fbce714092d32568a3802bac5ce2b30372ccc7`, ended **FAILURE**, not success. Ubuntu source gate passed; Windows passed source tests, internal six-candidate x64 builds/smokes, sealed-transfer checks, R105 and R106. Native R107 failed with the bounded, customer-safe observation **`app=ledger, zoom=400%, check=unmapped`**. R108 was not reached.

Root cause: the LedgerDiff 3-column form puts a left label beside a fixed `ttk.Entry(width=65)`; with `tk scaling 4.0` and the enforced 600×390 window, this pushes entry widgets **horizontally outside the viewport**. A local *synthetic Tk/Xvfb reproduction* with the same layout measured a 585px canvas and entry x=771px, showing every LedgerDiff input `winfo_ismapped() == False`. Those reproduction measurements are **not** from GitHub Windows runner or a physical Windows 11 machine.

## Implemented source fix

- Only LedgerDiff's free GUI uses a permanent, single-column stacked layout, avoiding fragile DPI cutoffs: each label, corresponding editable input and Browse button occupies a dedicated sequential row; the two optional match-key entries and output folder are likewise stacked.
- Entries use `width=1` **plus `sticky="ew"` in an expanding grid column** so user-entered financial source paths remain editable across narrow widths without demanding 65 characters of horizontal space. No values are read, truncated, rewritten or exported by this layout change.
- The untouched five other application layouts, six engine functions, precision/Decimal, user source files, offline privacy, signed-entitlement premium lock, and human-review safeguards are preserved. Widget **creation order** remains the R132 native keyboard Tab contract (two source inputs/Browse, two match headers, output/Browse, Generate).
- A second local synthetic Tk/Xvfb reproduction of the stacked grid at 400% measured all five entries mapped and resized within the same 585px viewport (entry x=24px, width=537px); it is **not** a replacement for actual Windows native CI or independent physical accessibility acceptance.

## Test contracts and acceptance evidence

- Ten deterministic headless source-owned tests in [`test_ledger_responsive_layout_r133.py`](../tests/test_ledger_responsive_layout_r133.py) check exact 20-row plan, unique noncolliding rows, logical reading/Tab order, unchanged free/premium inventory, and invalid input counts including Boolean/float rejection.
- [`safe_unittest_r133.py`](../scripts/safe_unittest_r133.py) enforces the precise ten method names, zero skips and redacts all private exceptions and test stdout/stderr. Both Linux and Windows workflows must pass normal **and `-OO`** (target **40 named executions**).
- Existing **actual Windows native R105 / R106 / R107 / R108** CI gates remain enabled and unchanged; R107 must now prove the real built UI's 200%/400% mapping, scroll travel, focus reveal, label wrapping and no phantom focus targets. A green synthetic suite alone is explicitly insufficient.
- The CI artifact allowlist remains limited to internal evidence. No public executable, signing key, protected premium package or user input is committed or uploaded.

## Release HOLD

Do **not** merge this draft directly to main, publish the site, claim a Windows 11 physical acceptance pass, or distribute binaries. After exact-final-SHA **both-OS CI passes**, the next release checkpoint remains QD-authorized private six-EXE/R9 custody transfer, **46 independent physical Windows 11 accessibility checks**, real Defender/EDR assessment, signing, authenticated premium fulfillment, independent QD and founder authorization. All six products are unreleased.
