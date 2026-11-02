# SpendMap Lite category-specific spike evidence — R135 (DRAFT / RELEASE HOLD)

## What changes

Before R135, SpendMap's `review_spike` compares each vendor's **total** spend for an observed month to the median of the prior observed vendor months. When a vendor reallocates spending between categories without changing its total, a category-specific surge can be invisible.

R135 adds **three separate, human-review-only CSV columns** for each `vendor_key + month + category` bucket:

- `category_history_months`: number of **previous observed months** for this exact normalized vendor **and exact source category label**, excluding the current month. Calendar gaps do not create imaginary zero-spend months.
- `category_baseline_median`: exact Decimal median of prior observed monthly spend **for that vendor/category**, populated only after at least three previous observed months. Even-sized medians can have half-cent precision, which is not rounded away.
- `category_review_flag`: `review_category_spike` when the category has at least three prior observed months, its historical median is **strictly positive**, and the current month's amount is **greater than or equal to 2x** that median. Otherwise blank.

**Crucial distinction:** the existing `flag`, `vendor_month_total`, `baseline_median`, `history_months`, source physical rows, original vendor labels, collision indicators and imported-input SHA-256 remain unchanged. Category spike evidence is intentionally a **different field**, not appended to legacy vendor-wide flags, so existing filters continue to mean the same thing.

Category labels are treated as exact source labels, not normalized. `Parts` and `parts` remain separate until a human explicitly reconciles them; auto-merging would silently assert a supplier/category identity. A vendor normalization collision still requires review. If the prior median is zero or negative (credits/returns), this simple upward-spike rule remains blank rather than dividing by zero or implying fraud.

## Reproduction with synthetic CSV (never customer documents)

Write `vendor,amount,date,category` rows with ACME spending 10 in Parts and 90 in Services in each January, February and March of 2026; then 30 in Parts and 70 in Services in April. Generate using the free SpendMap UI. On the April Parts row: `flag` is blank (vendor total stayed 100), while `category_baseline_median=10.00`, `category_history_months=3`, `category_review_flag=review_category_spike`. April Services is not a category spike. Source hashes and physical row references are preserved.

## Verification

- Source: `fvs_suite/spend_analysis.py`, `fvs_suite/engine.py`.
- Real synthetic CSV regression suite: `tests/test_spend_category_baselines_r135.py` (17 named tests), including half-cent exact threshold, one-cent below boundary, missing-category history, case-sensitive categories, credits, vendor/category isolation, original SHA-256, physical rows, duplicate execution, malformed money and hostile Decimal context.
- Exact-inventory, privacy-redacted, zero-skip source gate: `scripts/safe_unittest_r135.py`, mandatory on Ubuntu and Windows in both normal and optimized (`python -OO`) modes; target 17 × 2 × 2 = **68 method executions**, not a claim of pass until CI actually completes.
- Existing R59 report-header contract is deliberately updated for the three additive fields. Existing vendor-wide R59/R60/R74/R85 tests still run unchanged. Six candidate Windows x64 builds, native UI checks, protected-artifact evidence and R9 custody remain mandatory under the inherited workflow.

## Risk and release boundary

This deterministic **review signal is not evidence of fraud, noncompliance, invoice validity or payment authorization**. An unexpected increase can be legitimate (seasonality, large equipment purchases, classification changes, missing months). All processing remains local-first, finite Decimal-safe, bounded by the existing importer and independent of ambient Decimal precision. No network telemetry, originals rewritten, premium entitlement changes, public EXE downloads or site publication. CI automation is not a substitute for the 46 physical Win11 acceptance checks, real Defender/EDR examination, signing, protected premium distribution, independent QD and founder approval. **All six utilities remain UNRELEASED.**
