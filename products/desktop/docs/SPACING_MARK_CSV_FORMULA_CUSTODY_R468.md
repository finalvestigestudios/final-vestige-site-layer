# R468 — spacing combining mark CSV formula safety (DRAFT / QD HOLD)

**Scope:** LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. Shared CSV output only; no binary, catalog, entitlement, payment, telemetry, or compliance-decision changes.

## Reproducible defect

Unicode category **Mc** (spacing combining marks) was absent from the shared CSV formula guard's leading-mark inspection and from `engine.safe_cell`'s leading ambiguous-mark policy. For example, synthetic `U+093E + "=2+2"` previously escaped neither boundary, despite the explicit conservative treatment of `Mn` and `Me`. The raw source is legitimate data, but spreadsheet importers differ in their interpretation of leading marks. This is a precaution against formula-like material being interpreted as active syntax, not a claim of demonstrated exploitation in Excel.

## Implemented behavior

- `csv_formula_guard.has_unescaped_formula_prefix` now scans past **Mc** when inspecting leading formula operators, just as it already did for **Mn/Me**. This is inspection only: no NFKC rewrite and no alteration to original evidence.
- `engine.safe_cell` now prefixes an apostrophe for any **leading Mc** mark, including benign text. The original mark and every following codepoint remain exactly recoverable after the single escape. Nonleading marks, already-apostrophe-escaped values, ordinary source labels, and canonical ASCII negative Decimal values retain their prior behavior.
- Shared CSV evidence writer still independently rejects raw formula-like values from callbacks which bypass `safe_cell`. The new direct-writer regressions confirm refusal before staging on synthetic Mc-prefixed formulas.
- `offline_regression_gate_r459.py` now descriptor-fingerprints `fvs_suite/csv_formula_guard.py`, which was previously absent from the short source inventory. Its existing R456 module is mandatory in both normal and optimized modes; R468 adds four methods there without changing the required fourteen-module / 28-child matrix.

## Test evidence (separate proven and unproven scopes)

**Executed locally on Linux:** an independent pure-Python reconstruction of the modified prefix/sanitizer logic passed **12/12 focused unit tests in standard mode, 12/12 in `-OO -W error`**, including **10,000 seeded mixed-mark/operator cases per mode**. This is a **policy projection**, not tests against a complete checkout or a native Windows binary. No user financial data was used.

**Committed but awaiting execution:** four R456 sanitizer tests, three R215 direct-writer tests, and two R459 source-fingerprint gate tests — **nine new methods in existing repository test modules**. The R456 and R459 additions are in the mandatory offline matrix; the R215 additions require broad discovery/CI or direct invocation.

When an authorized complete checkout and runner are available:

```bash
python -B -W error -m unittest discover -s products/desktop/tests -p test_csv_safe_cell_zero_copy_r456.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_csv_safe_cell_zero_copy_r456.py
python -B -W error -m unittest discover -s products/desktop/tests -p test_atomic_formula_prefix_r215.py
python -B -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -B products/desktop/offline_regression_gate_r459.py
```

## HOLD and next highest-impact step

Previous GitHub Actions PR runs for both Windows build and cross-platform source evidence failed before any job step ran. The root cause remains unverified; see PR #2716 exact-commit runs. An authorized GitHub maintainer should examine Actions job annotations, billing/spending and runner eligibility, restore execution, then run this PR's actual exact-commit tests and Windows x64 build/Defender/accessibility/installed smoke checks. No release unless QD independence and explicit founder approval are recorded, all six binaries are really validated, and premium binaries have protected entitlement-gated distribution.

**Never publish this synthetic fixture as executable evidence. No premium files or URLs are introduced.**
