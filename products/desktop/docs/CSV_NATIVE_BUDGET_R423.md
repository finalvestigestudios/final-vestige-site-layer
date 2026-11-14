# Labs R423 — bounded native CSV snapshot budgets (source-only; RELEASE HOLD)

Issue #73 · R423 is stacked on the exact R422 draft head `72e0d34d6bd27f16ea566cd710aed251df853d33` (PR #2454), **not** production `main`. No binaries, downloads, website content, financial decisions, signing keys, license issuance, or release approval changed.

## Defect and severity boundary

The shared financial CSV descriptor reader `read_csv_snapshot(path, maximum)` only checked `maximum < 0`. Python `float('nan')`, `float('inf')` and an arbitrarily large integer could bypass that caller-budget check; malformed types raised inconsistent errors, and hostile integer subclasses could execute comparison hooks. A NaN budget allowed reading a small synthetic CSV rather than rejecting the invalid limit; an infinite or huge limit effectively removed the claimed 64 MiB bound **for direct API callers**. This is a hardening gap in a local helper, **not evidence that the standard GUI/engine path shipped unbounded data**, because the current engine passes its fixed `MAX_IMPORT_BYTES = 64 * 1024 * 1024`.

The reader now checks **before path conversion or stat/open** that the budget is an exact built-in `int`, from zero through 64 MiB inclusive. It rejects booleans, floats, nonfinite numbers, Decimal/Fraction, arbitrary objects, integer subclasses, negatives and oversized integers with one fixed error and no private file inspection. The existing bounded descriptor, symlink, race and error-redaction logic remains unchanged. Normal exact 64 MiB engine calls remain valid; financial Decimal money arithmetic and output/audit rules were untouched.

## Precise changed artifacts

- `products/desktop/fvs_suite/csv_snapshot.py`: native budget check and module ceiling.
- `products/desktop/tests/test_csv_snapshot_native_budget_r423.py`: 18 real-file and adversarial regression methods; no customer data.
- `.github/workflows/desktop-source-evidence-r385.yml`: explicit Windows/Ubuntu Python 3.12 normal and optimized runs for R423 plus inherited R30, R258, R296.
- This release-hold document.

## Reproducible local test evidence (2026-11-14)

The **actual** original `csv_snapshot.py` was reconstructed byte-for-byte from GitHub blob `a695123f1adc133dfac2cc38726540fe373618fe`; `git hash-object` matched it. The exact amended source blob is `b0d7dc324800f0d335a17812512b76470eb336ca`. The exact new test blob is `58600108323e01856f672b5ccd9f0bacf3010a51`. The untouched inherited R30 test blob is `db7e752fb04ef6a2419f22898c258f7732779042`; each local `git hash-object` matched the corresponding GitHub blob. Temporary data and test calls were real on-disk CSV reads, not a rewritten helper.

On Linux, Python 3.13.5, `PYTHONPATH=products/desktop PYTHONDONTWRITEBYTECODE=1`:

```bash
python -W error -m unittest discover -s products/desktop/tests -p test_csv_snapshot_native_budget_r423.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_csv_snapshot_native_budget_r423.py
python -W error -m unittest discover -s products/desktop/tests -p test_csv_snapshot_r30.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_csv_snapshot_r30.py
```

- R423: **18/18 PASS** normal, **18/18 PASS** optimized.
- Inherited R30: **14/14 PASS** normal, **14/14 PASS** optimized.
- **64/64** focused actual-source test method executions PASS.
- Pre-patch R423 suite failed on the genuine original module (15 assertion failures and 7 errors across 18 methods/subtests), so tests detect the defect.
- The new tests also validate no file stat/open occurs with invalid budgets, exact BOM/raw-byte conservation by R30, zero-byte files, oversized sparse files, file replacement and mutation rejection.

**Limitations:** Only the exact source files and exact R30/R423 tests above were executed locally, in a minimal import-root checkout reconstructed from the pinned GitHub blobs. R258/R296 and all other inherited financial, cryptographic, premium, UI, installer and full Windows tests are wired or inherited but **not executed here**. This does **not** qualify a packaged executable or establish that the six engines pass integration.

## Blocker and next acceptance step

At prior R422 head, source CI [#43579077709](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43579077709) and Windows build [#43579077717](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43579077717) failed before any recorded job steps (four job `steps=null`). Cause unconfirmed. R423 fresh-head runs must be inspected independently. Repository owner should examine GitHub Actions billing/spending caps, runner eligibility/allocation and run annotations, restore runnable CI and rerun **exact** R423 HEAD on Windows and Ubuntu including R30/R258/R296, all finance engines, signature/encryption/entitlement tests. Follow with real Windows x64 EXE smoke, Defender, accessibility, SHA-256, no-telemetry and authenticated/denied premium-download receipts.

**STRICT HOLD:** Feature branch + draft PR only. No merge, deploy, release, CMS change, premium-access exposure or payment/compliance decision. Independent QD review and explicit founder approval remain mandatory.
