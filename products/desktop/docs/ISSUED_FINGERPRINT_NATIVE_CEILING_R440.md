# R440 — premium issued-entitlement fingerprint ceiling (DRAFT / HARD RELEASE HOLD)

Tracking: [Final Vestige Labs #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
Stacked only on [R439 draft #2554](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2554), parent `cbeab94457cd1b7dc2e205953c2dcfd69e1c7af2`; not production `main`.

## Defect and source correction

The operator-side `fingerprint_issued_entitlement(path, max_bytes, error_type)` function enforced its caller-supplied size threshold, but **no intrinsic cap** existed for callers passing a bound above 8192 bytes, `float("inf")`, or other nonnative values. The protected registry currently passes a literal 8192, so this is direct-API defense in depth, **not a claim of a bypass through the existing normal CLI**.

The helper now refuses any bound unless `type(max_bytes) is int` and `1 <= max_bytes <= 8192`, before any file/path inspection. It rejects booleans, float infinity/NaN, equal-valued floats, and int subclasses with custom comparisons; refusing to invoke user-defined comparisons or inspect customer paths for invalid controls. A genuine single-link <=8192-byte file still produces the same deterministic SHA-256; source bytes remain unchanged. Existing registry reservation, signature checks, access controls and human approval are untouched.

## Evidence and reproducibility

- Direct source artifact: `products/desktop/issued_entitlement_guard.py` (base Git blob `e3b5a22f3191bbafd583275779e33157604686ca`).
- New executable regression file: `products/desktop/tests/test_issued_fingerprint_limit_r440.py`, **16 test methods**, with multiple table-driven subcases and a deliberately hostile `int` subclass.
- Exact source reconstructed from R439 Git blob before the patch (verified local `git hash-object`). Linux Python **3.13.5** with the patched full module and new tests: `python -W error -m unittest discover -s tests -p test_issued_fingerprint_limit_r440.py` **16/16 PASS**; `python -OO -W error` **16/16 PASS**; `compileall` PASS.
- Controlled pre-fix reproduction: restored original Git blob, ran the same 16 test methods; **22 subcase failures** (expected red). The failures include excessive and nonnative limits reaching path inspection rather than failing closed.
- The new source-evidence workflow includes both modes on Ubuntu and Windows and reruns inherited R378 fingerprint and R13 registry suites; those inherited tests were **not run locally**. No full checkout, Windows native executable, signature, Defender scan or protected distribution was tested.

## Release controls and next action

The preceding R439 source workflow [#43666015111](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43666015111) and Windows build workflow [#43666015175](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43666015175) failed with zero job steps / no assigned runners. Failure before execution is not a failed code test, and underlying billing, policy or eligibility cause is unconfirmed.

Repository owner: inspect hosted Actions billing/spend limits, runner permissions and Actions policy; once jobs start, run new/inherited tests and the full six-app source suite, then Windows x64 smoke, accessibility, Defender, binary checksums, and authenticated premium-download validation. Do not infer publication readiness. Keep `release_authorized=false`, independent QD review and explicit founder approval. No product distribution, actual license issuance, website change or deployment is authorized by this PR.
