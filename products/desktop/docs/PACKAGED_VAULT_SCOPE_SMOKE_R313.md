# R313 — exercise premium archive product scoping in the actual packaged smoke path

**Draft / QD and founder HOLD — not released.** Parent: R312 `feature/labs-r312-premium-vault-product-binding-20261109`, not `main`. Tracks issue #73.

## Missing acceptance behavior

R312 added `expected_product` to the authenticated premium archive restore API and to the review window, but the **packaged** `--smoke-test` used the backward-compatible **unscoped** restore call for both GrantAudit Studio Pro and ProcureGuard Studio Pro. Thus a Windows candidate could pass its premium vault smoke even if product binding regressed. R313 closes this smoke coverage gap; it does not change encryption, license enforcement or the proprietary audit engine.

## Proposed change

- `fvs_suite/smoke.py` now invokes a shared, synthetic, **product-scoped** roundtrip in both premium branches. The four free flows are unchanged.
- `fvs_suite/vault_smoke_scope.py` verifies successful matching-product restoration into a new directory, exact restored report and journal bytes, unchanged original ciphertext, and no additional root entries. It then retries the **same authenticated archive and passphrase** using the *other* premium product scope and requires the fixed product-mismatch exception, zero additional files/directories and unchanged ciphertext.
- The helper has no account/network dependence. It does not log or report private source paths/passphrases and uses synthetic evidence already prepared in the `TemporaryDirectory` smoke.
- `test_vault_smoke_scope_r313.py` provides 16 standalone stdlib regressions for both products, acceptance bypass, wrong denial reason, modified report/journal/ciphertext, leaked plaintext, unsafe root and unexpected outputs.
- Both Linux source and Windows build CI jobs invoke the focused suite with standard Python and `-OO`. The existing whole-source `test_safety_smoke.py` path will exercise actual cryptography once CI resumes.

## Verified locally — synthetic only

Linux CPython 3.13.5, with self-contained synthetic restore substitutes:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_smoke_scope_r313.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_smoke_scope_r313.py'
python -m py_compile products/desktop/fvs_suite/vault_smoke_scope.py products/desktop/tests/test_vault_smoke_scope_r313.py
```

Observed **16/16 PASS** standard, **16/16 PASS** `-OO` (**32/32 focused method executions**), Python compile PASS. Exact Git blob hashes of locally executed files: helper `15f64d126264f1b6527ff517a9d6634ea8fe2288`; tests `53e1f6732e009aca5f8750afc769e139e33f990f`. The temporary local test checkout contained a stub package `__init__.py` solely to import this dependency-free helper; it is **not** committed. This test proves helper behavior with stand-ins, **not a real AES-GCM restore, EXE smoke, native NTFS, Windows Defender or private distribution gate**.

## Release blockers and next acceptance

GitHub Actions on R312 (run #42690037156, 2026-11-09) previously had failed Windows and Ubuntu jobs with **no recorded steps**. Confirm R313 independently; if runner scheduling remains blocked, repository owner must check Actions billing/spending limits, runner availability and workflow policy. Then execute all source tests, real `test_safety_smoke.py` integration for **all six products**, the R312 AES-GCM integration, actual Windows 11 x64 packaged `--smoke-test` for all six, checksum/PE gates, Defender, accessibility, protected premium distribution, independent QD and founder approval.

**No merge into production, no WordPress update, no published EXEs, and no claim that all six applications are releasable.** Local-first privacy, Decimal money, deterministic audit evidence and human compliance review remain unchanged.
