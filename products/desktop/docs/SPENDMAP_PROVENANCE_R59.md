# SpendMap Lite R59 — auditable vendor normalization and explainable spend spikes

**Status: developer preview only; all six Windows x64 applications remain unreleased.** R59 changes only the free SpendMap Lite source engine, its synthetic packaged smoke, tests, and documentation. It does not authorize publication or change premium entitlements.

## Why this matters

The existing SpendMap report collapses vendor labels into an uppercase alphanumeric key. This is convenient for grouping but **not evidence that two entities are identical**: `A-CME` and `ACME` both become `ACME`. The earlier report silently pooled their spend, discarded original labels and source line numbers, and supplied a `review_spike` flag without revealing the prior-month baseline. R59 retains deterministic grouping but makes that ambiguity and the basis for spike flags visible.

## Updated exported CSV contract

The first five columns are unchanged: `vendor_key`, `month`, `category`, `amount`, `flag`. Six appended columns are:

| Column | Meaning |
| --- | --- |
| `vendor_month_total` | All categories for this vendor key and month, using exact Decimal cents. Repeats across categories in that month. |
| `baseline_median` | Median of **all prior observed month totals** for the vendor key, available after at least three previous months. Preserves exact half-cent precision (e.g., `10.005`) rather than displaying a rounded value that could misrepresent the threshold. |
| `history_months` | Count of prior **observed** months, not intervening calendar months. |
| `source_rows` | Semicolon-separated source **physical CSV line numbers** for this vendor/month/category bucket, in original import order; quoted embedded line breaks are accounted for by the existing reader. |
| `source_vendor_labels` | Distinct original vendor labels for the **current bucket**, deterministically ordered. Values that resemble spreadsheet formulas are protected by the existing CSV writer. |
| `vendor_label_variants` | Count of distinct case-insensitive vendor spellings **across the entire file** that collapse to this normalized vendor key. |

`normalized_vendor_collision_review` appears in **every bucket sharing a vendor key** if spellings differ beyond case, even when they occur in different months. `review_spike` is preserved and coexists with the collision flag, separated by a semicolon. It requires at least three previous observed monthly totals, a strictly positive historical median, and the current vendor-month total **at least twice** that median. These are review prompts, **not evidence of fraud, purchasing errors, or compliance findings**. Negative spend/refunds affect totals but are never silently recategorized.

Report rows remain sorted by normalized key, month, and the original category text. `category` is intentionally not rekeyed or recategorized. Financial inputs are still parsed by the existing validated, descriptor-snapshotted CSV importer; row-level amounts are rounded to cents under the existing HALF_UP policy. Originals are never changed, and the existing atomic non-overwriting, formula-safe CSV writer remains mandatory. No data is uploaded, no model is called, and no compliance decision is automated.

## Synthetic verification

Run in a complete, trusted checkout:

```bash
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p 'test_spend_*_r59.py' -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p 'test_spend_*_r59.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
PYTHONPATH=products/desktop python -m fvs_suite.demo spend
```

The full R52+ two-mode source gate, six synthetic source smokes and clean Windows 11 x64 executable build/smokes must additionally pass. This source-level enhancement cannot substitute for native Windows GUI, security, premium-access, distribution, and independent QD acceptance.

## Known limits

Normalization is ASCII alphanumeric only and intentionally lossy; source labels and flags require human verification. Source-row references are local to the CSV actually read and are **not globally unique evidence identifiers**. The spike baseline is descriptive and may be misleading when observations are sparse, seasonal, distorted by refunds, or affected by vendor collisions. No claim of statistical anomaly significance is made. Reports contain vendor labels and provenance by design: keep CSVs in an appropriately protected local folder.
