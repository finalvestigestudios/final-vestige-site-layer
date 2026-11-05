# Final Vestige Labs R204 — Policy Delta Windows symlink witness without silent skip

**Status: DRAFT / HARD RELEASE HOLD.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R203 draft [#1052](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1052) at immutable parent `840b615505a2696c21bc2742b941e5abe8946ede`. No edits to `main`, WordPress, release assets, payment/license gates, or financial engines.

## Problem reproduced

The R197 Policy Delta real-file acceptance test `test_source_symlink_cannot_be_published` called `skipTest` if Windows rejected `Path.symlink_to` (notably with insufficient symlink privileges). The R202 strict audit matrix correctly treats **any** skip as a HOLD, so this otherwise working Windows test environment could never pass the 148-case full suite.

## Patch and fidelity boundary

- The original test first attempts a **real native filesystem symlink**. If permitted, it executes the unchanged production `policy_diff.compare_policy_files` rejection path, verifies no report, and verifies the target bytes are untouched.
- When `Path.symlink_to` raises `OSError` or `NotImplementedError`, the test creates a **regular stand-in file** and patches only its `Path.lstat` result to report a symlink `st_mode`. The actual production reader still runs, including its real `csv_snapshot._metadata` `stat.S_ISREG` rejection path, while every other pathname retains real metadata. The test no longer skips.
- The case explicitly records `_native_link_verified = True` only when native link creation succeeded. The fallback sets it to `False`; an R204 regression checks that denied/unimplemented paths are **never counted as native coverage**.
- Four additional R204 tests cover simulated permission-denied, unavailable symlink API, exact-one-path metadata marking, and native-or-simulated end-to-end rejection. No new skip or expected-failure is allowed.
- Both Ubuntu and Windows workflow definitions invoke the four-case R204 suite in normal and optimized `-OO` Python before the strict 148-case inherited matrix; PowerShell checks each exit status.

**Important:** a PASS in a simulated fallback verifies the security guard's handling of link metadata, **not** native Windows reparse-point, junction, symlink, race, packaged-EXE, or Windows 11 accessibility acceptance. Those remain separate mandatory, native release gates. No policy text is treated as legal interpretation; humans review compliance decisions. No customer data or money arithmetic changed.

## Actual execution evidence and limitations

- Local Linux CPython 3.13.5 on 2026-11-05 UTC: **4/4 R204 tests normal + 4/4 `-OO` PASS**, no skips; focused R197 symlink method **1/1 PASS**; Python `compileall` PASS.
- **Scope of local execution:** a disposable isolated harness that reproduced the patched R197 symlink method and R204 test logic against a minimal `fvs_suite.policy_diff` / `csv_snapshot` guard stub with the same link rejection semantics. This was **not** a checkout of the private GitHub repository, **not** the exact committed production modules, and **not** the complete 21-case R197 or 148-case inherited matrix. Never present the harness results as full app integration.
- On both OSes, workflow invocation is configured but **GitHub-hosted execution remains unverified**. Earlier [R203 run #41984648218](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41984648218) failed with two failed jobs and no exposed execution steps.
- No Windows x64 executable was produced, tested, or made available. All six applications remain unreleased.

## Next highest-impact steps

1. Repository owner: inspect the GitHub Actions failed-run banner, Actions billing/allowance, permissions, and runner allocation; unblock jobs and rerun this branch's unchanged head on Windows and Ubuntu. Do not assume billing is the cause without evidence.
2. Run the **real inherited 148-case matrix per Python mode** and the new four-case witness suite. Capture private proof of whether native Windows links were actually supported; where not, keep native link/reparse-point validation as a distinct release HOLD.
3. Privately package all six Windows x64 candidates; checksum, Defender-scan, open and smoke-test on Windows 11; perform keyboard and screen-reader accessibility testing and protect premium files behind real access controls.
4. Require independent QD review and founder authorization before any production merge or release; do not create unrestricted premium downloads.

**HARD HOLD:** No production deployment, published binaries, approval bypass, or premium asset exposure.
