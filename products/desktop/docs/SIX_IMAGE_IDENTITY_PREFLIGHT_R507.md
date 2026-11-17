# R507 — fail closed on duplicate six-product Windows candidate images

**Issue:** [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). **Status:** feature branch / draft PR / QD and founder HARD HOLD. Stacked on R506 draft #2914, not production `main`.

## Risk and implemented boundary

The six-app release gate validates six filenames, a canonical SHA256SUMS inventory, PE32+ shape, and the SHA256 of each already-open descriptor. These checks do not by themselves prove that a packaging mistake did not copy the *same valid executable* to two different product filenames. This is especially important across the four free apps and two premium apps.

R507 introduces `require_distinct_candidate_images()` in `products/desktop/candidate_identity_r507.py` and binds it to `release_gate.verify()` **before any native Windows smoke process can launch**. The preflight requires six ordered expected product names, six native lowercase SHA-256 values, and **six distinct digest values**. All fifteen possible duplicate pairs are exercised. Failures have a fixed path-free diagnostic; they do not disclose local candidate or customer file paths.

The check is invoked only when trusted `classify_smoke()` selects `windows_smoke_passed` for genuine native Windows x64 testing. Existing Linux integrity-only and injected-runner synthetic fixtures may use identical inert PE bytes and retain explicitly **non-native** evidence. Source-only checks and mocked classifications do not certify native packaging. An image with a different digest may still be the wrong product: this is a duplicate-payload safeguard, **not runtime product identity attestation**, code signing, AV certification, entitlement validation, or approval to distribute.

## Verification evidence from this sprint

- Linux CPython 3.13.5, exact helper/test files as committed: `PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_candidate_identity_r507.py`: **18/18 PASS**.
- Same command under `python -OO -B -W error`: **18/18 PASS**, totaling **36 focused test-method executions**.
- `py_compile`: **PASS** for helper, 18-test unit module and four-method gate-binding module.
- Exact matching Git blob identities for locally executed files: helper `84161c0fa0b743ade4d697095bc9d00620a1aec1` and unit tests `0b7521e2fa43e070160945aa446f9cf1c28bc286`. Gate-binding test blob `911283f4521f119644bdfcdb87e44bd5095ecb43` was syntax-checked only, **not executed against the full repository locally**.
- R507 adds a separate read-only, artifact-free, SHA-pinned Ubuntu + Windows Actions workflow for both normal and optimized Python. This avoids enlarging the already oversized existing CI workflows. Hosted results are **not** equivalent to a successful test until actual jobs run.

## CI blockers detected while inspecting the exact R506 base

The existing `.github/workflows/desktop-build.yml` is **242,075 UTF-8 bytes** against its shared `ci_workflow_budget_r292.py` ceiling of **229,376** (12,699 bytes over). The existing `.github/workflows/desktop-source-evidence-r385.yml` is **60,506 bytes** while `test_independent_ci_r385.py` still insists on **8,192** (52,314 over). Even after runners become available, those particular self-checks cannot pass unchanged. **Do not loosen the reviewed 224-KiB safety ceiling or silently disable tests.** Next sprint should extract repeated test invocations into versioned checked-in manifests/runner scripts with explicit test-count and coverage checks, then restore budget compliance without dropping any gate.

R506 [build #44175772938](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44175772938) and [source #44175773067](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44175773067) both had jobs finish **failure with `steps=null`**, so GitHub Actions runner/billing/policy eligibility is a separate unresolved account-level blocker. Check the repository Actions UI, billing/spending limits and runner policies; then rerun exact HEAD.

## Release and privacy custody

No production merge, deployment, WordPress edit, EXE publication, open premium link, or QD/founder approval. Existing local-first financial processing, Decimal money math, deterministic audit records, immutable source files, compliance human review, and genuine premium entitlements remain untouched. Full six-engine tests, live native Windows x64 smoke, physical keyboard/a11y review, Defender/EDR, code signing and protected premium delivery remain required.
