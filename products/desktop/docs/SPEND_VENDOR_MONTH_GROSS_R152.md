# Labs R152 — SpendMap vendor-month gross flow review (DRAFT / RELEASE HOLD)

A vendor with a +150.00 Parts charge and -140.00 Services credit has a 10.00 net month. Category-level R141 flags are blank in both categories, despite significant gross flow.

The new vendor_month_gross_charges and vendor_month_gross_credits columns aggregate positive charges and magnitudes of negative credits across **all categories for each normalized vendor and month**, using exact Decimal arithmetic. vendor_month_offset_review is review_vendor_month_mixed_sign_offset only if both are positive. The three new columns are included on every corresponding category bucket: do not sum them across rows. No existing fields were removed, and the old per-category credit_offset_review stays unchanged.

These are human-review cues, **not** matches between refunds and purchases, compliance judgments or approval to pay. The original source SHA-256, physical source rows, local snapshot import, isolated Decimal context, privacy, no-overwrite output, normalized-vendor collision warnings, and net-spike thresholds remain unchanged. Premium access logic is untouched.

Schema migration: three new fields appear after credit_offset_review and before source_rows; consumers must select by header name. Three inherited schema tests were updated.

Code: products/desktop/fvs_suite/spend_analysis.py and products/desktop/fvs_suite/engine.py. Twenty-five synthetic end-to-end regressions: products/desktop/tests/test_spend_vendor_month_r152.py; strict no-skip runner: products/desktop/scripts/safe_unittest_r152.py; Ubuntu and Windows workflow requires ordinary and -OO runs (25 x 2 x 2 = 100 planned targeted executions). All passing outcomes require exact-head CI evidence; CI is not physical Windows validation.

From repo root, with PYTHONPATH=products/desktop, run python products/desktop/scripts/safe_unittest_r152.py and python -OO products/desktop/scripts/safe_unittest_r152.py.

HARD HOLD: independent physical Windows 11 46-check accessibility, genuine Defender/EDR, code signing, protected premium distribution, independent QD and founder authorization. All six apps unreleased; no public binaries or production merge.
