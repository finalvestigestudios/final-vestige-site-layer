# R347 — ProcureGuard accounting-source custody before numeric callbacks

**Engineering draft; Issue #73; independent QD and founder HARD HOLD.** Stacked exclusively on R346 draft #2000, never on production `main`. All six desktop utilities remain **unreleased**.

## Scope and reproduced weakness

R346 independently bound plain numeric source strings, but legitimate grouped, dollar-prefixed or parenthesized accounting values (for example `$1,234.50`, `1,234.5`, `($1,234.50)`) returned `None` for original-value custody. An injected Python parser callback could convert a negative invoice price into a positive amount, or silently rewrite a grouped quantity. R347 independently interprets the ordinary ASCII financial-source grammar **before** callbacks and requires the output to be numerically identical. Malformed grouping, Unicode numerals, underscores, unbalanced parentheses and conflicting signs fail *before* callbacks execute; no raw financial text is exposed in error messages.

The valid grouped/currency/parentheses forms mirror `engine._exact_amount` and `engine.qty`. Plain scientific notation remains supported by the helper for legacy direct-API compatibility, although default CSV import parsers are stricter. Unsupported custom/locale formats now fail closed rather than relying on arbitrary callback interpretations; this intentional tightening requires QD compatibility review. Negative unit prices remain allowed as flagged human-review evidence. Quantity remains nonnegative. Eight-place exact Decimal precision, bounded context, original source data, hashes and review/approval authority are unchanged.

## Measured verification and limits

- Local Linux Python, synthetic helper-only harness; **25/25** new R347 unit methods passed under both `-W error` and `-OO -W error` (**50 passing executions**). No skips.
- A pre-R347 behavioral reconstruction of R346's `None` fallback, replayed with the exact 25 R347 tests, produced **14 failures**, demonstrating the missing custody checks.
- Module and new unit file syntax compiled. No access to the private full checkout in the local Python sandbox: real ProcureGuard `review_line`, inherited R345–R346 suites, AES-GCM tests, packaged native Windows binaries and the full six-app regression suite were **not executed locally**. CI must validate the actual committed module and full-engine behavior.
- Neither Windows native acceptance, Defender/EDR, SHA-256 executable manifests, 46-observation accessibility review, signing, nor protected premium entitlement was verified. No software is approved for distribution.

## CI and release block

Existing `.github/workflows/desktop-build.yml` source and Windows jobs run `unittest discover` and must include `test_procurement_formatted_source_r347.py` under both normal and optimized Python. The previous R346 workflow run [#42962736340](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42962736340) failed before either job recorded steps; root cause remains unconfirmed. Check GitHub Actions billing/spend caps, runner eligibility, permission settings and failed-job annotations; then run exact-head tests from the draft PR.

Run from a complete trusted repository checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_formatted_source_r347.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_formatted_source_r347.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_numeric_source_integration_r346.py'
```

**Next highest-impact:** restore hosted Ubuntu/Windows CI, execute inherited procurement integration and 22 genuine AES-GCM tests, then conduct isolated Windows 11 x64 executable smoke/Defender/SHA256/accessibility validation and protected premium distribution. QD and founder must separately approve any merge, WordPress publication or public binary link. There is no automated payment/compliance decision, telemetry, network transfer, production change or executable publication in R347.
