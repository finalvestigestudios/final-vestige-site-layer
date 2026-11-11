# R348 — ProcureGuard signed-zero source and callback custody

**Issue #73 · DRAFT engineering only · QD/founder HARD HOLD.** This branch is stacked on R347 draft PR #2005 at immutable base `cfd80898da43a0eb143a27cc5cc1eb7f2666eb1e`; it does not target or modify production `main`.

## Reproduced source-integrity gap

The R347 `checked_quantity` accepted textual and native Decimal **negative zero quantities** (for example `-0`, `-.0`, `Decimal("-0")`) because `Decimal("-0") < 0` is false. The suite's standard CSV `engine.qty` regex rejects negative sign quantities. An injected callback could also flip `+0` ↔ `-0` while preserving numeric equality, including accounting negative-zero unit prices `($0.00)`. The monetary totals did not change, but the direct API disagreed with CSV quantity grammar, and parser-produced sign evidence was silently discarded. A second gap was that the real review engine used `price < 0` for PO, invoice and credit flags, so a genuinely signed negative-zero accounting price never triggered `negative_unit_price_review` or `negative_credit_price_review`.

**R348 source patch:** The existing source preflight rejects *any signed* quantity (including negative zero) before calling supplied parsers. Callback validation rejects signed quantities and requires **zero-sign parity** between independent source interpretation and returned native Decimal. The genuine `procurement.review_line` engine now uses native `Decimal.is_signed()` for negative-price review flags, so both ordinary negative prices and accounting negative-zero prices are visible to human reviewers. Positive zero prices remain unflagged. Ordinary nonzero equality, eight-place Decimal precision, source bounds, accounting negative-zero prices, strict native types, and redacted errors remain. **No automated payment or compliance approval**.

This is an intentional direct-API compatibility tightening only for signed-zero quantities and zero-sign-flipping injected callbacks. QD must assess plugins using signed-zero inputs. No original files, provenance hashes, reports, licensing or WordPress content were changed. The new negative-zero review flag is a deliberate warning-only change, not a policy decision.

## Evidence — verified locally

- The **exact R347 Git blob** `a4a85721c99c376795dc269333f36b54339dc2cd` was recreated locally and verified using `git hash-object`.
- Before the patch, the same 29 R348 helper tests produced **17 failures / 29 tests** on original R347 behavior. After patch: **29/29 PASS** on Linux CPython standard `-W error`, **29/29 PASS** under `-OO -W error`; total **58 passing focused test executions**. Python `compileall` PASS.
- The tested updated helper matches the GitHub committed Git blob **`d56de27fc28a307932f4a0d3e556e1939e8edcff`**. The 29-test file matches **`806f4dce8cf91cfa5755a3c218a5e89ed73bd19d`** exactly.
- **13 additional genuine `review_line` integration tests** compiled successfully and were committed byte-identically (`320b27851c54bef644b845f445a33b2a9d92200d`), but **NOT executed locally**: complete private dependency tree unavailable in the isolated Linux runtime.
- Existing procurement suites, 22 real AES-GCM cases, six Windows x64 executables, Windows Defender, screen-reader/accessibility, and entitlement-gated premium distribution were **not validated** in this sprint.

## Required CI gates

`.github/workflows/desktop-build.yml` adds two explicit R348 jobs steps (Ubuntu source and Windows package runner), each running the 29 helper and 13 real-engine cases in standard and `-OO` Python, with Windows exit-code enforcement. Once true runners execute, expected R348 total across both OS and modes is **168 method executions**, subject to actual results; this is NOT a claimed pass.

For trusted complete-checkout validation:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_signed_zero_custody_r348.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_signed_zero_custody_r348.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_signed_zero_integration_r348.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_signed_zero_integration_r348.py'
```

As of R347 [Actions run #42970283465](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42970283465), both Ubuntu and Windows jobs failed approximately two seconds after start with `steps=null` and `logs_url=null`. Each check has one annotation, but this connection rejects the annotation API path; the root cause remains **unconfirmed**. This is NOT evidence that test code ran or failed. Owner should inspect Actions check annotations, billing/spending limits, hosted runner provisioning, and repo Actions permissions; then rerun the R348 PR checks. Do not bypass gates by marking failures green.

## Next highest impact / release constraints

After hosted CI executes, reconcile any real-engine integration failures (including inherited R343–R347 tests) and run the complete desktop suite and 22 genuine AES-GCM integration cases. Then produce *private* Windows 11 x64 six-app candidate executables, independently smoke/Defender/SHA-256/accessibility test, and verify premium files are entitlement-gated. **No merge, public download, privileged QD override, production-site update, compliance determination, or payment authorization** is approved here.
