# Labs R278 — private Windows candidate subprocess environment custody

**Issue:** #73. **Branch:** `feature/labs-r278-private-child-env-20261108` stacked only on R277 draft #1561. **Release posture:** DRAFT; QD and founder HOLD. No merge or publication authorization.

## Concrete defect

The existing `offline_windows_candidate_r269.py::_run_child` used `os.environ.copy()` before launching the source gate, toolchain checks, PyInstaller for six standalone Windows applications, and native evidence gates. That forwards inherited `GITHUB_TOKEN`, `GH_TOKEN`, cloud tokens, premium-license secrets, proxy settings and Python/PyInstaller override variables to every child. This is avoidable exposure, particularly when running a private financial-data workflow under a credentialed development account. The original subprocess path did redirect stdin/stdout/stderr and disable shell; those defenses do **not** prevent environment inheritance.

## Delivered code

- New `scripts/candidate_child_environment_r278.py` builds a minimal, case-insensitive allowlisted environment: PATH, PATHEXT, SystemRoot, WINDIR and TEMP/TMP/TMPDIR, plus explicit no-PyPI, no-user-site and no-bytecode controls.
- Valid, lowercase 40/64-hex `GITHUB_SHA` may flow as **untrusted optional source metadata**, never an approval token. Other GitHub, cloud, premium-license, profile, proxy, pip-index, Python-injection and PyInstaller-overrides are not inherited.
- Production `scripts/offline_windows_candidate_r269.py::_run_child` now calls this fresh environment builder. Original stdout/stderr/stdio isolation, `shell=False`, subprocess timeout, all six named application build stages, same-run source/evidence checksum custody, and release holds are unchanged.
- New `tests/test_candidate_child_environment_r278.py` has **15 methods** including real isolated Python child witnesses and tests compiled from the actual Git-owned `_run_child` AST. Workflow runs these on Ubuntu and Windows in normal and optimized `-OO` Python modes.

## Test evidence and limits

**Executed locally, Linux CPython (not a Windows candidate build):** 15/15 methods PASS with `-W error`, 15/15 PASS with `-OO -W error`; `compileall` PASS. The new helper and new test file have byte-for-byte Git blob identities `4f3fe8f3d82f81579032c4d198c62c22bfa996f4` and `23a14989677b42c0e1c329bb8e3a0ba297083d44` matching the locally executed bytes. Local source-contract checks used a **minimal test-only** runner file containing the exact `_run_child` function, not the full GitHub runner. The AST tests in the committed test module will compile the `_run_child` function directly from the complete GitHub runner when CI is available. Full repository regression, hosted Actions and genuine Windows 11 x64 PyInstaller acceptance were **not** executed locally.

The minimal environment is **not an OS sandbox or network denial**. Native Windows packaging may need additional explicitly justified platform launch keys; obtain actual Windows build evidence before relaxing the allowlist, and never reintroduce full environment inheritance. The optional commit marker is not bound to git HEAD by this change. The premium apps remain private and unreleased.

## QD and release decision

Hosted workflow pre-start failure on the R277 parent: [Actions #42465800725](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42465800725), Ubuntu and Windows jobs `failure` with no steps recorded; infrastructure reason unknown. Recheck R278 Actions when triggered. **Smallest owner unblock:** resolve GitHub Actions billing/runner provisioning/workflow policy, or run the preexisting R269 private build pipeline on a trusted Windows 11 x64 workstation in an access-controlled directory.

**Next milestone:** full source suite and Windows native build/smoke/Defender/PE-checksum/accessibility verification for all six binaries, then premium entitlement/distribution controls, independent QD, and founder approval. No production merge, binaries, downloads or premium releases from this sprint.
