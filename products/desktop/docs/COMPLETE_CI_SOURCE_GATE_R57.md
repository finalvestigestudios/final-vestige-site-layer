# R57 — complete desktop CI source provenance (development only)

R52 introduced a runner-independent source gate, but the repository's hosted CI still used a mixture of a normal full test run, a manually maintained selection of optimized test modules, and a separate six-engine smoke. New test modules could slip past the optimized selection until someone amended the workflow.

## What this change enforces

Both `source-tests` (Ubuntu 24.04) and `windows-build` (Windows x64 hosted) now execute `products/desktop/scripts/offline_source_gate.py` **before** any Windows executable packaging. That gate inventories all desktop test and runtime Python source, executes the **complete discovered suite under normal Python and under `-OO`**, compares exact active/skipped test identities, and runs all six deterministic synthetic source smokes. File identity and SHA-256 inventories are checked before and after. The Linux job creates a private `fvs-offline-source-suite-v1` JSON source evidence report, uploaded through the existing strict seven-day source-only artifact action. The new JSON replaces the narrower earlier source-smoke-only report.

The `ci_artifact_policy.py` allowlist now permits the **exact single** `offline-source-suite.json` evidence path and continues to prohibit EXE uploads, wildcard paths and premium binaries. The `ci_source_contract.py` preflight checks that both named jobs retain the complete source gate, that the Windows gate is before packaging and checks its process exit status, and that no CI job has a fail-open condition. Fifteen synthetic regressions exercise these invariants (one additionally checks the real workflow when a full checkout is available).

## Verification on a trusted checkout

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p test_ci_source_contract_r57.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_ci_source_contract_r57.py -v
python -m unittest discover -s products/desktop/tests -p test_ci_artifact_policy_r41.py -v
python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
python products/desktop/ci_artifact_policy.py .github/workflows/desktop-build.yml
python products/desktop/scripts/offline_source_gate.py
```

Run the full `verify-windows-candidate.ps1 -Build` procedure afterward on native Windows 11 x64, never on a production server. On a green Actions runner, download and independently examine **evidence only**, not unreviewed EXEs.

## Boundaries and release controls

This does **not** fix GitHub Actions runner allocation. If a run dies with empty job steps and `BlobNotFound`, none of these tests ran. Even a successful full source gate is **not** evidence of a working Windows executable, a GUI accessibility test, signed dependencies, an antivirus scan, or premium gated distribution. Real six-EXE packaging, clean Windows install/launch/exit and encrypted-premium/entitlement review are still mandatory, followed by independent QD and founder approval. No source changes here authorize public software downloads or deployment.
