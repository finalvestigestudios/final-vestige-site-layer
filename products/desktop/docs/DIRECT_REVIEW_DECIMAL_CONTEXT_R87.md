# R87 — Direct-call financial review and linked-grant Decimal integrity

**Scope:** Draft engineering change for issue #73. No release, publication, licensing, payment approval, or claim of full-checkout/Windows verification.

## Why the previous boundary was insufficient

R84–R86 protect main entrypoints, yet the reusable functions `fvs_suite.review.price_exceeds_tolerance`, `procurement.PricePolicy.outside`, and `grant_allocations.reconcile_allocations` remain independently callable.

An ambient Decimal context with precision 2 can round a real variance away:

- **Expected unit price:** `100.01`
- **Observed unit price:** `102.02`
- **Exact variance:** `2.01`
- **2% review threshold:** `2.0002` => **review required**.
- Under an unguarded two-digit Decimal context, both round to `2.0` => **false negative**.

Linked grant source claims of `999999999999.99` plus `999999999999.99` can likewise lose cents or raise `Inexact` if `reconcile_allocations` is called directly under low precision.

These are financial-review observations, **never** declarations that a transaction is fraudulent, eligible, compliant or approved.

## R87 changes

1. Centralize direct price variance comparisons in `review.price_outside_tolerance`, requiring finite Decimal operands, nonnegative bounded thresholds and a fixed private `Context(prec=64)`. Both the legacy 2%-or-cent helper and `PricePolicy.outside` reuse the same comparison. The review maximum (`1e27`) accommodates documented *aggregated procurement* totals, not merely individual unit prices (<= `1e12`).
2. Wrap direct `grant_allocations.reconcile_allocations` in a fresh private 64-digit Decimal context, preserving all input fields, budget, credit, lineage and evidence-manifest semantics. The main `engine.grant_audit` route already has its own independent context; nested local contexts are intentional.
3. Preserve caller precision/traps/flags, audit provenance, source snapshots, CSV fields, deterministic ordering, and human judgment. Validate and fail closed rather than coerce floats or nonfinite numbers into audit decisions.

64 digits exceeds the bounded 200,000-record fixed-point aggregation envelope (up to approximately 2e26, plus eight-place source precision). This does **not** authorize arbitrary-precision external numeric inputs; direct price operands outside the review domain fail with non-sensitive errors.

## Regression coverage

`tests/test_direct_review_context_r87.py` defines **12 focused methods**: exact threshold inside/outside, hostile precision/rounding, direct `PricePolicy` calls and custom thresholds, negative values, aggregated totals, trapped rounding, validation, direct linked grant multirow amounts, credit offsets, normal engine route and invalid source non-publication.

The normal full-checkout test command is:

```shell
cd products/desktop
python -m unittest discover -s tests -p 'test_*.py' -v
python -OO -m unittest discover -s tests -p 'test_*.py' -v
```

This committed suite is not evidence of execution until the run has been performed and logs inspected. All Windows x64 builds must also be installed/smoke-tested and scanned; QD and founder approvals and premium entitlement security remain mandatory before distribution.

## CI and release hold

The predecessor [R86 draft PR #314](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/314) CI [run 41212576547](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41212576547) failed with no recorded Linux or Windows job steps and no runner name. See [issue #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75).

**Next gate:** Restore hosted runner dispatch, execute the R87 full checkout and the complete desktop regression suite, then build and smoke all six Windows 11 x64 programs. Do not merge any stacked draft PR or publish binaries until independent QD review and explicit founder approval.
