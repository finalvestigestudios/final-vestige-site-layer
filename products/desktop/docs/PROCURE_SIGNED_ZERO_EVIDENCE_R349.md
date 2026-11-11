# R349 — ProcureGuard signed-zero evidence custody (draft; issue #73)

**Status:** feature branch only. Independent QD and founder hold; no merge, site write, executable release or premium distribution.

## Defect and decision boundary

The R348 numeric boundary correctly rejected ordinary nonfinite or rounded numbers and isolated callback Decimal contexts. It nonetheless used Decimal numeric equality to compare parser output with the original source, and Decimal("-0") == Decimal("0"). A custom quantity parser could silently convert an explicit negative-zero source quantity to positive zero, or a unit-price parser could remove or introduce a minus sign on zero (including "($0.00)", "-$0.00", "$-0.00"). Numeric totals are still zero, but financial input *identity* and reviewer-visible credit/return sign evidence were not preserved.

**R349 change (two predicates in the existing strict helper):**
1. Reject negative-zero **source quantities** before running any caller-provided parser. Negative quantities must be explicit credit/return events; even a mathematically zero negative quantity must not bypass evidence custody.
2. For any zero **parser result**, require its Decimal sign bit to equal the independently parsed source sign bit, for both price and quantity. Preserve documented negative-zero unit prices as signed evidence, without classifying them as actual credits or authorizing payments.

Existing bounds, ASCII grammar, Decimal exact equality, acceptable price signs, explicit event typing, SHA-256 physical-row provenance, redaction and human review are unchanged. Nonzero numeric normalization may still change *scale* (e.g. 3.000 to 3); R349 intentionally controls the **zero sign bit**, not display formatting.

## Executed and reproducible test evidence

Synthetic-only test file: `products/desktop/tests/test_procurement_signed_zero_r349.py`, **32 unittest methods**, covering source negative zeros, attempted source-to-result sign flips, accounting/currency spellings, native Decimal and integer sources, positive controls, context isolation, privacy-safe errors and nonfinite regressions.

The previous **exact R348 Git blob** `aee0f7e48c06587392dd7045ea7c7781a2827b3d` was replayed locally against the 32 corrected tests on Linux CPython **3.13.5**: **17/32 failed**, demonstrating the signed-zero custody gap. The R349 patched helper blob `4ca7797aba8f5f7a373a4a800ad443da5dbb4785` and tests blob `8b9f5f72487f5ee07fbfcd1240189696ecccca77` matched the exact committed Git blobs. The corrected files were executed locally with `PYTHONPATH` pointing to an isolated exact-file copy:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_signed_zero_r349.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_signed_zero_r349.py'
```

**Results: 32/32 PASS (normal), 32/32 PASS (optimized), 64/64 focused executions, 0 skips.** `py_compile` PASS for patched helper and test. The two commands are mandatory gates in both Ubuntu and Windows jobs in `.github/workflows/desktop-build.yml`, with explicit PowerShell exit checks on Windows.

**Limits:** locally executed only the source-identical helper plus R349 unit tests, **not** a full private-repository checkout, engine `review_line` integration, previous R342–R348 suites, 22 genuine AES-GCM integration cases, native Windows binaries, Defender scan, accessibility or entitlement acceptance. Hosted runners have historically failed before any steps; until jobs execute commands, workflow failure cannot be classified as a code regression or a pass.

## Release and follow-up gates

- Check current PR Ubuntu and Windows jobs for actual step logs and passing commands. If steps are missing, inspect GitHub Actions billing/spend limit, runner eligibility, check annotations and workflow permissions; restore hosted runner provisioning.
- Execute real ProcureGuard engine and all inherited R342–R349 regression tests on trusted checkout, plus all 22 genuine AES-GCM cases.
- Perform private Windows 11 x64 six-app build/smoke/PE digest/Defender and screen-reader/keyboard accessibility acceptance. Verify locked premium entitlements before any restricted distribution.
- Obtain independent QD review and founder signoff before merging, publishing the site, or announcing executable availability.

The software remains **UNRELEASED**. This patch neither interprets compliance nor approves payments.
