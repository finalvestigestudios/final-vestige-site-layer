# R187 — put the catalog release guard on BOTH CI runner jobs (DRAFT / HARD HOLD)

Tracks issue #73. Stacked directly on R186 draft PR #947 (SHA d7daf235), **not production/main**.

## Reproduced CI contract defect

R186's desktop-build.yml accidentally placed **two** R186 catalog-gate steps under the source-tests Ubuntu job: one normal Unix script and one PowerShell script. The separate windows-build job had **no R186 catalog gate**. An Ubuntu green result could not establish that Windows executed the mandatory gate. GitHub Actions also currently fails **before** allocating either runner; no hosted execution is claimed.

## Correction

- Move the existing R186 PowerShell three-command gate into windows-build, directly after the R185 source gate and **before** Windows dependency/package stages. Keep Ubuntu's original three-command gate inside source-tests. Each job must run the R186 tests in normal and optimized (-OO) Python, and validate the actual Gutenberg draft.
- Preserve PowerShell immediate $LASTEXITCODE failure checks after each individual Windows Python invocation and the Windows PYTHONPATH; Ubuntu uses the job-scoped environment.
- Add products/desktop/tests/test_catalog_ci_placement_r187.py, a standard-library structural contract test that fails on a missing, duplicate, misplaced or degraded per-job gate; wrong OS/shell/environment; missing -OO or preflight invocation; and unguarded Windows command failures.
- Both independent CI jobs now execute this 16-case contract in normal and optimized Python before later build activities. This contract does not evaluate arbitrary YAML expressions and does **not** replace Actions' own YAML parsing or physical Windows execution.

## Verification — 2026-11-04

- Local isolated Linux Python **3.13.5**: **16/16 normal PASS; 16/16 -OO PASS (32/32 focused executions)** on a synthetic two-job workflow fixture; zero skips.
- Exact new test file matched committed GitHub blob **8d2ca2f79fe84b7447083ee756821e7d1acc6cde**. Python compilation passed.
- GitHub source-level old/new structural inspection: **before** = Ubuntu two R186 steps, Windows zero; **after** = Ubuntu one, Windows one. New R187 source-contract steps appear once in each job. Scope anchors and exact PowerShell failure checks inspected.
- **Not verified**: running this new Python test against the complete GitHub checkout on a hosted runner, full inherited application suites, physical Windows x64 builds, accessibility, malware/EDR, signing, protected premium distribution, actual premium entitlements, QD/founder approval, or live WordPress release.
- Production site, premium binaries and finance/compliance engines **unchanged**. All six products **UNRELEASED**.

## QD and next highest-impact action

**HARD HOLD; no merge/publication.** Repository owner: open the latest GitHub Actions run's pre-job failure banner and check billing, available Actions minutes, usage limits, runner provisioning and permissions. Restore both Ubuntu and Windows allocation and rerun the exact R187 draft head. Only then claim hosted test/build evidence. Continue pending 14 Policy Delta real-file integrations, private six-candidate Windows 11 smoke/accessibility checks, Defender/EDR, signing, premium access control, independent QD review and founder authorization. This repair is a genuine workflow placement fix, **not** software-release approval.
