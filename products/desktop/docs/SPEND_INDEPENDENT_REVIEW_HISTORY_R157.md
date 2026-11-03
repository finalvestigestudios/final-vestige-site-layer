# R157 — independent historical review-evidence verification (DRAFT / HOLD)

## Risk addressed

R156 independently rechecked source membership and eight exact financial totals/offset warnings, but a copied SpendMap report could still **silently erase a high-spend history spike, category spike or normalized-vendor collision warning** without modifying the source-line hash or financial sums. R157 closes that specific integrity gap. This is *not* independent verification of every report column, a compliance opinion, or a release authorization.

## Additional independently checked CSV columns

The read-only SpendMap verifier now rejects deviations in seven exported fields:

1. `history_months`: number of earlier observed vendor months (no blank-month fabrication).
2. `baseline_median`: exact median of earlier observed vendor-month net amounts, preserved to half cents if applicable.
3. `flag`: required `review_spike` and/or `normalized_vendor_collision_review` in canonical order.
4. `category_history_months`: prior observed vendor+category months only.
5. `category_baseline_median`: independent prior vendor/category month median, no rounding.
6. `category_review_flag`: required `review_category_spike` at threshold or empty.
7. `vendor_label_variants`: source-label diversity under *ASCII-case-only* equivalence; Unicode case folding is intentionally not used.

Spikes require at least **three prior observed months**, a **positive** baseline, and current net amount **at least twice** that baseline. Colliding normalized vendor names remain review items even when their balances match.

The isolated `spend_review_verify.py` implementation does not import production `summarize_spend`, `RunningDecimalMedian`, or review-flag helpers. It independently accumulates fixed-point Decimal cents and uses a two-heap O(log n) running median, keeping up to 200,000 source records practical. A private Decimal context prevents low-precision caller settings or Inexact traps from suppressing findings.

It continues the R155/R156 pinned offline source snapshot, exact CSV physical row/source hash checks and privacy-safe `HOLD` output. Originals are not edited. Vendor collision detection is evidence of potentially lossy normalization, **not** a finding that any vendor committed fraud. Human review remains required.

## Local verification (Python 3.12, from repository root)

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r157.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r157.py
PYTHONPATH=products/desktop python -m fvs_suite.spend_evidence_verify --source "original.csv" --report "spend-map.csv"
```

The strict runner enumerates exactly **29 synthetic test methods** with no skipped/expected-failure tolerance. GitHub Actions installs the checks in both Ubuntu and native Windows source/build jobs, normal and optimized Python, for **116 planned test-method executions**. Check the actual exact-head Actions results before describing any as successful. Tests cover missing months, half-cent medians, cross-category hidden spikes, compound review flags, vendor-label variants, tampering of all seven fields, private CLI errors, hostile ambient Decimal contexts, and multiline physical CSV rows.

## Remaining limitations and hard release holds

The verifier shares the strict importer, vendor normalization, category spreadsheet-escaping, and Decimal parser with the generator: this is **not** a fully separate source decoder. It does not independently reproduce the display-only `source_vendor_labels`, validate the original source's external authenticity, sign evidence, or approve a payment. Use existing exact report replay for whole-export reproduction, subject to its separate limits; neither tool is a digital signature.

All four free and two premium apps remain **UNRELEASED**; no production merge, public executable, unrestricted premium transfer, or WordPress catalog publication. Native Win11 46-check human accessibility acceptance, genuine EDR/Defender candidate assessment, signing, protected premium distribution, independent QD review and founder authorization remain release prerequisites.
