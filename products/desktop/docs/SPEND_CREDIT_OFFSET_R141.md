# Labs R141 — SpendMap Lite gross-charge / credit offset evidence

**Status:** draft engineering candidate, not released. Applies only to the free SpendMap Lite engine; GrantAudit and ProcureGuard remain premium-gated, and no website/download changes are authorized.

## Reviewer problem and implemented rule

A vendor's net spend of $10.00 may represent one $10.00 charge or $150.00 in charges offset by $140.00 in credits. The R135 vendor-wide and category-wise net-baseline spike detectors cannot distinguish those situations. R141 adds three columns to each existing **vendor/month/category** CSV bucket:

| Column | Exact meaning |
| --- | --- |
| `gross_charges` | Sum of **strictly positive** validated source row amounts in the bucket, formatted to cents. |
| `gross_credits` | Sum of the **positive magnitudes** of strictly negative validated source row amounts in that bucket, formatted to cents. Not a negative number. |
| `credit_offset_review` | `review_mixed_sign_offset` only when *both* gross charges and gross credits are > 0 in the **same** bucket; otherwise blank. |

`amount` remains the exact signed **net** sum. `vendor_month_total`, vendor `flag`, net month/category baselines, `category_review_flag`, normalized-vendor collision markers, source physical row citations and source SHA-256 remain unchanged. Import, signed-zero handling, ASCII CSV schema, decimal context isolation, spreadsheet-safe labels, and atomic no-overwrite export remain in effect.

**Illustrative synthetic result:** two Parts rows from ACME at +150.00 and -140.00 in January produce `amount=10.00`, `gross_charges=150.00`, `gross_credits=140.00`, and `credit_offset_review=review_mixed_sign_offset`. These figures are not evidence of illegality or improper payment. All signals require human review of the original source rows, which are never edited or uploaded.

## Threat model and boundaries

- No credit-to-charge matching or refund legitimacy inference is attempted. Mixed signs can be completely ordinary for refunds, corrections, and accruals.
- Source data stays local. Inputs are read from the existing bounded, descriptor-verified CSV snapshot and identified with its SHA-256.
- The shared validated-input boundary rejects invalid amounts, non-finite decimals, unsupported exponent/precision, duplicate physical CSV positions, and unbounded lists before publishing output.
- Accumulators are exact `Decimal` values and the existing private 64-digit decimal context protects aggregation from a caller's precision, rounding or traps. Credit magnitude uses `Decimal.copy_negate()` without context rounding.
- Negative-zero, zero-only, credit-only, or charge-only buckets do not trigger a mixed-sign flag. Cross-vendor, cross-category and cross-month activity is never combined for this flag.
- Category spelling is not silently normalized. Existing lossy vendor normalization is explicitly flagged when it merges distinct original labels.
- Output contains only a review flag and explainable amounts; no automated compliance approval, fraud accusation, networking, AI decisions, premium unlock or public distribution.
- **CSV schema change:** three new columns are inserted immediately before `source_rows`. Consumers relying on column *position* must update to header-name lookup. Two earlier exact-schema regression tests were explicitly updated; no original columns were removed.

## Source and verification evidence

- Engine: `products/desktop/fvs_suite/spend_analysis.py` and `products/desktop/fvs_suite/engine.py`.
- Synthetic real-CSV tests: `products/desktop/tests/test_spend_credit_offsets_r141.py` (23 methods: offset/no-offset sign boundaries; zero net; grouping isolation; normalized collisions; preservation of R135 baseline signals; source row/sha; 1-trillion boundary; caller Decimal traps; malformed private inputs; deterministic export; formula labels; empty schema).
- Strict inventory/no-skip runner: `products/desktop/scripts/safe_unittest_r141.py`.
- CI: `.github/workflows/desktop-build.yml` requires the runner in normal and optimized (`python -OO`) modes on **Ubuntu and Windows**. The expected R141 targeted matrix is **23 × 2 modes × 2 OS = 92 executions**, counting each named test execution; no success is assumed until the exact-head jobs finish. Preexisting full source suites, six standalone Windows x64 packaging/native smoke, encrypted candidate-custody and premium-lock gates remain mandatory.

Local source-only check, from the repository root:

```bash
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r141.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r141.py
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests
```

## Release blockers (not bypassed)

Independent physical Windows 11 review of all 46 accessibility observations, trusted private six-executable receipt and independent R9 fingerprint pin, genuine Defender/EDR assessment, code signing, protected premium distribution, independent QD signoff, and explicit founder authorization. Do not publish untested artifacts or unrestricted premium downloads. No claim that source tests certify live Windows GUI access or installed-machine security.
