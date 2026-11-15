# R445 — premium inventory private exception-chain custody (DRAFT / RELEASE HOLD)

Issue: #73. Stack: this feature branch sits above the R444 draft branch, **not** production main.

## Scope and actual change

Both **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** use the shared premium_manifest_completion verifier to check their local evidence reports and source-hash inventory before reporting successful export. The old verifier raised sanitized ValueError messages **inside** OSError, UnicodeError, or JSONDecodeError handlers. Python retained the original exception in the public error's __context__ even with suppressed traceback chaining. An OS error may carry a private client pathname; UnicodeDecodeError.object may contain a full manifest; JSONDecodeError.doc may contain a private file label. Ordinary traceback rendering suppresses context, but integrations that serialize exception objects could still inspect it.

R445 defers **five** refusals until **after** their handlers terminate, preserving existing public messages:
1. Bounded manifest descriptor/read/ASCII decode failure (including absent or replaced private paths).
2. Evidence package directory-listing error.
3. Malformed JSON-escaped inventory label.
4. Report hardlink-custody inspection error.
5. Post-hash report/package recheck OS error.

This does **not** bypass single-link checks, pathname/descriptor comparisons, report SHA-256 verification, exact product report counts, or the no-extra-files rule. Hashes are evidence locators, **not** signatures or compliance findings. No source CSV bytes leave the local computer. No financial amount, rounding, license or compliance decision logic changes.

## Verification inventory

- Source: products/desktop/fvs_suite/premium_manifest_completion.py
- Nine new regression methods: products/desktop/tests/test_premium_manifest_private_chains_r445.py; covering valid grants/procurement packages, corrupt ASCII inventories, private OS errors, invalid JSON, directory errors, report inspections, post-hash rechecks, and no report modification on refusal
- Ubuntu and Windows normal/optimized CI registration: .github/workflows/desktop-source-evidence-r385.yml; inherited R254 and R255 inventory integrity suites run alongside the new tests
- Local assessment (Linux): **9/9 PASS** standard, **9/9 PASS** optimized with warnings as errors, compileall pass. Tests exercised a reconstructed full R445 verifier with synthetic real files and **local stand-ins** for three imported storage/hash helpers; this is **not** proof of full-repository or native Windows compatibility
- Required pending evidence: exact-commit GitHub CI must execute (not merely register jobs) on Ubuntu and Windows, run full six-engine financial/entitlement tests, package and smoke real Windows x64 executables, run Defender/accessibility checks, and verify SHA-256 and premium download gating

## Release invariants

**HARD HOLD:** release_authorized=false. No merge to production main, installer, EXE, public link, issued license, premium download exposure, WordPress publication or financial auto-approval was performed. Independent QD review and explicit founder approval still govern eventual release. If GitHub Actions jobs fail before runner assignment, inspect failure annotations in the Actions UI and account billing/spending limits, Actions policy, and hosted-runner eligibility; do not describe a non-running job as a test regression.
