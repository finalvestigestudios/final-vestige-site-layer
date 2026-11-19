# Labs R536 — Invoice Twin Scout day-window preflight before private CSV access

**DRAFT / independent QD + explicit founder HARD HOLD.** Stacked only on the R535 draft branch ([PR #3073](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3073)) at parent `1634c1a9d058fb6b2fffbc7a885e31b7d988549b`; not production `main`.

## Problem and deterministic change

`engine.invoice_twins(source, folder, window_days=...)` previously imported, opened, decoded and parsed the entire private CSV through `table()` **before** `candidate_pairs()` checked whether the day window was a native integer in `0..365`. A malformed API argument (including `True`, `7.0`, a forged integer subclass or `366`) needlessly touched private data and could trigger an unrelated import error first. No report was saved, but this violated fail-fast source handling.

R536 introduces one strict, bounded `require_invoice_review_window` helper and calls it *before* the CSV read in `engine.invoice_twins`. `candidate_pairs` uses the same helper for direct iterator consumers, preserving its historical input contract and error message. The existing user-facing `invoice_window_days` text parser, legitimate 0/7/365-day windows, candidate matching, Decimal amounts, source fingerprints, report formatting, review flags and human compliance decisions remain unchanged.

## Changed paths

1. `products/desktop/fvs_suite/invoice_window_policy_r536.py` — exact built-in int validation; no coercion, file I/O or customer-data echo.
2. `products/desktop/fvs_suite/engine.py` — validate before accessing `table` or the source CSV.
3. `products/desktop/fvs_suite/invoice_match.py` — reuse identical validation before consuming a direct iterator.
4. `products/desktop/tests/test_invoice_window_preflight_r536.py` — 15 committed unittest methods: boundaries and hostile types; privacy of errors; no private `table`/save/iterator access on invalid input; empty valid candidate behavior; valid end-to-end routing through mocked report I/O; unchanged strict GUI text parser.
5. This runbook.

## Evidence boundaries

Local Linux CPython isolated source check executed the **same standalone policy helper body** with three unittest methods (17 individual accepted/rejected subtest cases) in standard and optimized (`-OO`) Python: **3/3 PASS in each mode (6 method executions)**. The local check does NOT import the committed `engine` or `invoice_match` modules and cannot substitute for the full committed 15-method regression module, the repository matrix, or Windows tests. All 15 committed test methods must run on the actual branch before QD acceptance.

Suggested exact-checkout commands from `products/desktop/`:

```sh
python -m unittest discover -s tests -p test_invoice_window_preflight_r536.py -v
python -OO -m unittest discover -s tests -p test_invoice_window_preflight_r536.py -v
python scripts/offline_source_gate.py
```

Test with synthetic CSV only and verify no file opens on rejected windows. Later run the full source-matrix, native Windows x64 packaging, accessibility, Defender, checksum verification and premium access checks.

GitHub Actions has repeatedly returned failed jobs with `steps=null` before any test or build steps, tracked in [#75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75). This is **not** a test failure or a verified runner root cause. Do not merge/publish based on the isolated helper test or static source checks alone.

**Next highest-impact step:** Restore one runner with a real step log (inspect Actions billing, spending limit, policies, runner allocation), run the committed test module in both modes, and complete the six-product release gates. No site publish, deployment, premium file exposure, untested executable distribution, production merge, or QD approval is authorized by this draft.
