# R424 — bounded identity normalization before Unicode expansion

**Scope:** Issue #73; six-app shared native financial identity normalization, source-only. Draft stacked on R423; hard release hold. This does not authorize publication, payment approval, a compliance determination, a premium download, or a Windows x64 executable.

## Defect and change

The reusable `fvs_suite.identity_inputs.normalize_key` direct Python API accepted any-size built-in `str` and immediately performed `.upper()` and a regular-expression substitution. Unlike the common 64 MiB financial CSV descriptor intake and the bounded SpendMap direct source cells, it had no per-identifier limit. A long supplied identity could allocate large uppercase and regex results; some Unicode case mappings expand, such as `ß` into `SS`, increasing memory and producing an oversized matching key. This is resource-control hardening; no real customer attack, fraud, or published application vulnerability has been demonstrated.

Require exact built-in text (preserved from R177), then reject source length above **1,048,576 characters before uppercasing**. Reject uppercase-expanded text above the same ceiling **before regex processing**. Reject without truncating, hashing, echoing the original identity, invoking user-defined type hooks, or changing the case/ASCII matching algorithm. Existing smaller identifiers, including lossy Unicode normalization, remain unchanged, with human review still necessary for collisions. `parse_date` unchanged. 64 MiB file-level constraints and Decimal-safe money logic remain separate and intact.

**Compatibility note:** previously accepted single identifiers longer than 1 Mi characters, or shorter Unicode identifiers whose uppercase expansion exceeds 1 Mi characters, now fail closed with a fixed `ValueError`; these are NOT silently shortened or treated as matching.

## Exact artifacts

- `products/desktop/fvs_suite/identity_inputs.py` (modified)
- `products/desktop/tests/test_identity_normalization_budget_r424.py` (14 new test methods)
- `products/desktop/tests/test_native_identity_date_r177.py` (unchanged inherited test, 30 test methods)
- `.github/workflows/desktop-source-evidence-r385.yml` (Windows/Ubuntu source test wiring, normal and optimized)

## Measured local evidence, bounded claim

Linux **Python 3.13.5**; an isolated three-file checkout reconstructed from the *actual GitHub source blobs*. The tested blobs were independently matched with `git hash-object`: updated `identity_inputs.py` **`89074c919a4f173079082b7ae1784ef005164b11`**, new R424 tests **`23f93c5b63dc746e45d8bc1135736ef6648e3d78`**, unchanged R177 tests **`9610d35f5788432cbadae4107f46bd74fdfa5917`**.

- `python -W error -m unittest discover -s tests -p test_identity_normalization_budget_r424.py`: **14/14 PASS**
- `python -OO -W error -m unittest discover -s tests -p test_identity_normalization_budget_r424.py`: **14/14 PASS**
- R177 in both modes: **30/30 PASS each**.
- Combined: **88/88 test-method executions PASS**, including exact ceiling, one-character-over, Unicode uppercase expansion, pre-regex refusal, no truncation, original short identity behavior, hostile `str` subclass hooks, date regressions and private-value-free errors.
- Modified source and tests: `python -m py_compile` PASS.

These tests execute the committed source and test contents, but the environment is a minimal Linux reconstruction, **not the full repository**, **not a native Windows run**, and **not an all-six-application integration test**. GitHub-hosted workflow execution remains essential.

## Blockers and gates

As observed on preceding R423 exact commit `05c703c6`, GitHub Actions source run [43583787534](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43583787534) and build run [43583787538](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43583787538) completed with failure while all four jobs lacked recorded steps/runner names. The underlying billing, runner or policy reason is **unconfirmed**; no green CI claim. Check the fresh R424 exact-commit runs independently.

**Next highest-impact step:** repository owner checks GitHub Actions account/org billing, spending limits, hosted-runner eligibility and any repository Actions policy, then reruns the source/build checks. On functioning Windows and Ubuntu runners, execute the exact R424+R177 tests and inherited six-engine financial, crypto, privacy and licensing suites; build real Windows x64 candidates, scan with Defender, perform GUI keyboard/accessibility checks, attest SHA-256 and verify premium access protections. Independent QD review and explicit founder release approval remain required; no merge, deployment or distribution here.
