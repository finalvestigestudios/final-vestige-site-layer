# R270 — Private Windows candidate source-suite receipt custody

**Status: DRAFT only — issue #73; independent QD and founder HARD HOLD.** This increment closes an evidence gap in the R269 local Windows x64 six-EXE fallback. A successful source test process exit alone did not preserve the source regression/test-coverage record. The old candidate runner could thus retain a binary smoke report without an inspectable receipt for its normal/-OO test passes and six synthetic source-engine smokes.

## Engineering change

The R269 candidate runner now passes `--report <private-session>/source-suite-evidence.json` to the existing `offline_source_gate.py` as stage 1 of its 40-stage plan. This source gate exclusively publishes an offline JSON report after its **full normal and optimized test suite plus all six source smokes** pass. Before any packaging, the parent independently requires a regular, single-link, bounded (1 MiB) report; opens a descriptor with `O_NOFOLLOW` where available; compares descriptor and path identities before/after reading; validates the exact source-only schema, explicit non-release flags, test provenance/counts/digests, and the expected **six distinct ordered app IDs** all passing. It computes a SHA-256 pin of those bytes.

At the end of the real PE, six-executable smoke, independent Windows evidence attestation, and source/toolchain custody checks, the parent re-reads and revalidates the source report and compares it with the in-memory pin. A missing, invalid, duplicated, modified, mislabeled, or linked report **fails closed**. The receipt remains in the private operator run folder for independent QD review. It does **not** certify historical execution against a hostile operator; it is an internal consistency and evidence-retention control, not cryptographic signing or an independent Windows build attestation.

The two premium products remain private: `GrantAuditStudioPro` and `ProcureGuardStudioPro`. Nothing changes the Decimal-safe engines, local-first handling, human approval obligations, executable distribution permissions, or production/site approval workflow. The same existing 40 commands run; the first one now has `--report`. No network calls or public uploads are added by this patch.

## Measured local verification (2026-11-08 UTC)

- Linux CPython 3.13.5; normal `-W error`: **34/34 methods PASS** across the R269 regression suite (18) and R270 new suite (16).
- Optimized `-OO -W error`: **34/34 methods PASS**, total **68/68 focused executions PASS**. Python compilation: **PASS**.
- New R270 tests exercise exact-six receipt, source/optimized provenance constraints, fail-before-build on missing receipt, invalid JSON/size/link types, false release flags, incomplete/duplicated/failed source smokes, unknown keys, simulated 40-stage plan, and final-byte modification detection.
- Actual non-Windows command invocation exits **1**, writes **zero stdout bytes**, and emits only the fixed generic rejection diagnostic.
- The exact three committed Git blob IDs were checked against the locally tested source: runner `de8eccb9bb50d73ac713260dc9f3cb8fb4ec1872`; original R269 tests adapted `efe3658fb9a7167e070e8f86c44e3fa186239af6`; new R270 tests `e21c663f502bf28e53355f41dc56279f29fc373b`.
- These tests simulate subprocess success and private report creation: **NO actual Windows EXEs or native Windows GUI/Defender tests were run.** This is focused verification, not the entire repository-wide regression suite.

## Owner Windows 11 x64 validation and release blockers

On a trusted, access-controlled workstation with audited preinstalled Python 3.12, cryptography, and PyInstaller dependencies, check out this draft branch and follow R269's [private operator instructions](PRIVATE_WINDOWS_CANDIDATE_RUNNER_R269.md). Run the documented `py -3.12 -I products/desktop/scripts/offline_windows_candidate_r269.py --workspace "C:\\FVS_Private_Candidates"` procedure. Keep the workspace, source-suite receipt, checksum inventory, source/toolchain manifests and Windows release-gate evidence **private**. Do not upload the premium EXEs. Confirm actual provenance and test details with independent QD; the source receipt is **not** proof of Windows executables passing or of commercial entitlement.

Hosted GitHub Actions run [#42432524681](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42432524681) on R269 failed on **2026-11-08 UTC**: Ubuntu source-tests and Windows build jobs each had zero recorded steps and no runner. Owner action remains to check Actions billing/usage limits, workflow permissions and runner provisioning, then rerun an unchanged draft head.

**Next highest-impact action:** obtain private, genuine Windows 11 x64 six-EXE build+smoke evidence on a trusted machine, review the source-suite receipt and PE/attestation outputs, run Defender/accessibility tests, verify premium gated delivery, and obtain independent QD + founder approval before any merge or distribution.