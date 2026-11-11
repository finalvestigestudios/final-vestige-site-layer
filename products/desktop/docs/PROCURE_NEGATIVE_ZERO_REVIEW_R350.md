# R350 — ProcureGuard negative-zero price reviewer evidence

**Status:** DRAFT / independent QD review + founder authorization required. All six Windows x64 applications remain unreleased. No site or premium delivery changes.

## Finding

R349 correctly preserved the original sign of Decimal negative-zero source prices. But `procurement.review_line` still relied on `price < 0` at **three** review sites: purchase-order price, invoice/credit price, and credit-specific negative-price flag. Since `Decimal("-0.00") < 0` is false, human reviewers could miss the source's explicit negative price sign despite intact source data. This is a review-visibility defect, **not** an assertion of an incorrect monetary total or an authorized payment.

An inherited R345 regression, `test_quantity_negative_zero_allowed`, also contradicted R349's deliberate fail-closed negative-zero quantity prohibition and would fail when CI resumes.

## Changes

- Add `negative_price_review_required`: require native finite `Decimal`, inspect `is_signed()` rather than numeric comparison; never coerce, round, print paths or authorize payments.
- Use the helper in **all three** price-review sites. Negative nonzero remains flagged; positive zero remains unflagged. Existing credit/return, evidence and provenance logic remains unchanged.
- Correct the inherited R345 test to assert negative-zero quantity rejection **before** calling the injected parser.
- Add **26 synthetic helper unit tests** and **12 genuine full-engine integration cases**. Gate both test files in both modes on Ubuntu and Windows. No desktop packages are published.

## Reproduction and executed local evidence (2026-11-11 UTC)

Native Python `Decimal("-0.00") < 0` is `False`, but `Decimal("-0.00").is_signed()` is `True`.
On Linux Python **3.13.5**, the isolated, exact new helper and unit-test source was run using:

```sh
python -W error -m unittest discover -s tests -p test_procurement_price_sign_r350.py
python -OO -W error -m unittest discover -s tests -p test_procurement_price_sign_r350.py
python -m py_compile fvs_suite/procurement_price_sign_r350.py tests/test_procurement_price_sign_r350.py
```

**26/26 PASS** standard, **26/26 PASS** optimized; **52/52 focused unit executions** total. These unit tests do not import or execute the complete private suite. The 12 integration cases and modified `review_line` were syntax-checked or reviewed but **not executed together** in a complete local checkout, and no native Windows binaries were run. Git blob identity and CI results must be checked against this branch. Do not infer release readiness.

## Hosted CI blocker and next gate

Prior R349 [Actions run #42983864007](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42983864007) failed in both `source-tests` and `windows-build` before any recorded steps. The check runs each contain one annotation; its content is inaccessible using the available GitHub connector. Cause is **unconfirmed**, not a demonstrated test failure. Owner should inspect Actions billing/spending limits, runner eligibility, workflow permission state and check-run annotations; restore runner provisioning. Then run the **complete private-suite** procurement regressions including R342–R350, 22 genuine AES-GCM integration cases, and Windows 11 x64 validation of all six EXEs.

Do not merge draft stacked PRs, alter production, publish unsigned/untested EXEs, or bypass premium access controls without independent QD and founder approval.
