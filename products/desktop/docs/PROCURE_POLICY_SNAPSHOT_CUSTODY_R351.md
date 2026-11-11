# R351 — ProcureGuard native price-policy snapshot custody

**Status:** DRAFT ONLY, no QD/founder release authorization. Issue #73. This change is stacked on R350 draft PR #2026 (commit `2f6994d4f9d50adf20695fbecbf53c0af8763396`), not on production `main`.

## Why this sprint
`review_line(..., policy=...)` previously used the caller-owned `PricePolicy` throughout review. Although JSON-file thresholds were bounded by `load_price_policy`, the direct Python API accepted fabricated/subclass policy objects, malformed source fingerprints, and even a legitimate frozen dataclass that an injected numeric parser could mutate via `object.__setattr__` after review began. That can cause threshold/evidence-fingerprint drift between the first comparison and the exported report. The intended policy is reviewer guidance only and never a payment approval.

## Code changed
- `fvs_suite/procurement_policy_custody_r351.py`: accepts **only the exact native policy class** and its native stored three-field dictionary. Checks finite unsigned exact Decimal thresholds (absolute <= 100; fraction <= 0.10; <=8 fractional places and bounded coefficient/exponent), a lowercase 64-character SHA-256 source marker, and does not call arbitrary foreign conversion/getter hooks. Failures use one private-data-free error.
- `fvs_suite/procurement.py`: snapshots and rebuilds a fresh `PricePolicy` **before any parsing callback** in `review_line`; subsequent comparison, widened-policy label and exported SHA-256 use that isolated snapshot, not callback-mutable source state. Original rows and input snapshots are untouched.
- `tests/test_procurement_policy_custody_r351.py`: 37 standard-library focused tests, including native primitive validation, nonfinite/signed-zero, exponent/coefficient bounds, forged subclasses, hostile dictionaries, Unicode and private-path hash replacements, context independence and snapshot semantics.
- `tests/test_procurement_policy_integration_r351.py`: 12 full `review_line` integration test methods for real review flags, legitimate widened thresholds, invalid policies, callback mutation of absolute/fraction/hash and repeatability.
- `.github/workflows/desktop-build.yml`: normal + `-OO` unit and full-engine integration in both Ubuntu and Windows jobs; Windows steps fail closed using PowerShell exit checks.

## Executed evidence and scope
Local Linux Python 3.13.5 isolated package mirror using exact remote-committed SHA-1 Git blobs:
- Helper blob `0632f08469d71d77eb6096a6e0f659a12366f79d`; unit test blob `80fbcdbe715425e4366b25518cf854dbc36c0e60`.
- `PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_procurement_policy_custody_r351.py'` — **37/37 PASS**.
- `PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_procurement_policy_custody_r351.py'` — **37/37 PASS**, **74** focused method executions total.
- `py_compile` helper, unit and integration files — **PASS**.
- Integration source blob `c3932cdf67cd7495cbe44b641671c322af21f9b4` matches syntax-checked local copy.

**Not executed:** the 12 real procurement-engine integration methods, inherited suites, genuine AES-GCM tests, full private-repository checkout and Windows 11 x64 binaries. The isolated test Policy dataclass models the three field structure; only the integration tests use the actual `PricePolicy`. Hosted CI is not a substitute until jobs genuinely execute. Test counts must not be called a release pass.

## Remaining gates and owner unblock
The preceding [R350 GitHub Actions run](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42992589850) failed within seconds in Ubuntu and Windows **with zero recorded steps**. The root cause is not confirmed; check-runs have annotations inaccessible through this connector. Owner should open the failed check annotations in the GitHub UI and verify Actions spending/billing, runner provisioning, Actions permissions and org policies. Re-run the exact R351 branch when infrastructure is restored.

Next highest impact: execute all R342–R351 engine tests and 22 genuine AES-GCM cases on the full private checkout, resolve any inherited policy-contract failures, then perform real Windows 11 x64 executable/six-app smoke tests, checksums, Defender and accessibility acceptance. Premium binaries must remain access-controlled; no site release before independent QD and founder approval. No financial data upload, telemetry, payment authorization, or public download change in R351.
