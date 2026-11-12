# R371 — Isolate six-app release-smoke child environments (DRAFT / HARD HOLD)

## Defect and mitigation

The shared `smoke_runner_r336.run_smoke_checked` used `subprocess.run` **without an explicit `env`**. A real packaged Windows candidate therefore inherited the entire operator or GitHub Actions parent environment during pre-release smoke tests. This included possible GitHub Actions runtime credentials, cloud secrets, premium license/entitlement variables, proxy configuration, Python overrides, and local profile paths. The application's later Python offline audit hook cannot guarantee that these values stay unobserved by the bootloader or any code running before the hook.

**R371 passes `env=private_child_environment()` to every native or injected smoke runner**, reusing the existing R278 allowlist already used by the separate Windows candidate builder. It forwards only essential OS launch fields (PATH, PATHEXT, SYSTEMROOT, WINDIR, TEMP/TMP/TMPDIR), an optionally validated lowercase 40/64-character GITHUB_SHA, and forced PYTHONNOUSERSITE/PYTHONDONTWRITEBYTECODE/PIP_NO_INDEX safety controls. Parent environment is unchanged. Subprocess stdout, stderr and stdin remain DEVNULL; timeout, exact-exit and private-error handling are unchanged. No child is authorized to make network calls, receive private financial records, or publish any report.

This is **credential-inheritance reduction, not a Windows sandbox**. A candidate process may still access files or network through non-Python mechanisms, and inherited PATH or temporary-directory values must be trustworthy. Operate only on a controlled, preferably disconnected Windows host, with least-privilege runner credentials.

## Reproduced and tested

- Exact prior smoke-runner source from R370 Git blob `7f98ced387071016fb17c409cae72cb0289d2d0b`; exact reused R278 environment builder Git blob `4f3fe8f3d82f81579032c4d198c62c22bfa996f4`.
- On the original smoke runner, the new suite exposed the missing `env` boundary: **15 tests, failed** (1 assertion failure + 17 errors, including subtests), intentionally reproduced before patch. No real EXE or secret was involved.
- Exact updated smoke-runner blob `d899816b95ea1395c9262894777789d6da359dfc`; 15-test source blob `50fa092c4580878368f3b1dd8754675bae6852bf`. These independently match the files executed on Linux Python 3.13.5 and published to GitHub.
- `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_smoke_child_environment_r371.py'`: **15/15 PASS** in the equivalent isolated source tree with `PYTHONPATH=.`.
- `PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_smoke_child_environment_r371.py'`: **15/15 PASS** in equivalent isolated source tree; **30 passing focused method executions**.
- Source compilation `compileall`: **PASS**. A real local Python child invoked by the injected runner was denied the **synthetic canary** inherited by the parent, while a second real child could use a temporary file. Other tests cover case-insensitive secret names, profiles/proxies/license tokens, Windows boot fields, forced safe environment controls, commit identity, errors, exit status, injected runner parity and zero parent mutation.
- The existing R336/R278 inherited modules and **all other full-repository tests were not executed together**. No native Win11 x64 PyInstaller process has yet been tested with the new environment.

## CI, release controls and next gate

The exact feature-head workflow adds **four explicit invocations**: Ubuntu and Windows, each normal and optimized `-OO`, before source provenance and Windows packaging. The inherited full source tests and 22 genuine AES-GCM cases remain release blockers. Previous R370 [Actions run #43159250032](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43159250032) had two `failure` jobs with `steps=null` (no recorded execution). Failed-check annotations / billing and runner eligibility require owner inspection before any hosted source or Windows result can be claimed.

**Next highest-impact:** restore hosted job-step execution and run exact-head full tests (including R278, R336, R371 and 22 authentic AES-GCM cases); then smoke all six genuine PyInstaller EXEs on native Win11 x64 under the restricted child environment, inspect PE layouts and SHA256 checksums, complete Defender/accessibility and premium entitlement delivery checks. Do not weaken credential isolation solely to force a passing build.

**Release state:** All four free and both premium apps are **UNRELEASED**. This is a feature-branch draft stacked on R370, **not `main`**. No executables, site downloads, premium entitlement changes, telemetry, real financial records or production files are distributed. Independent QD + founder approval remain a hard requirement.
