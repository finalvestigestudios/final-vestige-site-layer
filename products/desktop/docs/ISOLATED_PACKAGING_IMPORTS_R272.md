# R272 — Fix isolated Python packaging CLI imports (six Windows utilities)

**DRAFT; issue #73; independent QD + founder merge/release HARD HOLD.** This changes Python-only bootstrap behavior in the packaging verification chain. It does **not** make Windows binaries or authorize downloads.

## Root cause and correction

R269–R271 private runner executes helper scripts as `python -I <absolute-script> ...`. Under CPython, isolated mode `-I` omits the script directory from `sys.path`, even for an absolute script path. Three required desktop entrypoints (`build_inventory.py`, `release_gate.py`, and `report_attestation.py`) imported sibling modules without restoring this Git-owned directory. The first real inventory process would therefore abort on `ModuleNotFoundError: candidate_guard`; the latter two would similarly abort on `pe_image_guard` and `release_gate`. Simulated R269–R271 subprocesses had incorrectly masked this integration failure.

R272 gives each of those **three** entrypoints a minimal self-bootstrap using `Path(__file__).resolve().parent`. It does **not** add cwd, arbitrary environment paths or a user-controlled PYTHONPATH, remove `-I`, disable module custody or change the 40-stage candidate plan. The other three helper entrypoints already bootstrap explicit trusted directories.

## Regression coverage

New `products/desktop/tests/test_isolated_packaging_entrypoints_r272.py` launches **six actual packaging helper entrypoints** as child interpreters under `-I` and `-I -OO` (12 cases), from a separate untrusted working directory while pointing `PYTHONPATH` to shadow modules that would throw an exception if imported. Each invocation must return success and display `--help`; the test does not echo raw child error output. The direct import bootstrap is exercised without building EXEs, requiring privileged Windows GUI services, accessing client data or downloading anything.

Added explicit normal and optimized R272 regression gates to both the Linux source-test job and Windows packaging job before actual builds. These are additional to the full existing Python suite.

## Evidence and limits

On a Linux CPython interpreter, a local **synthetic minimal sibling-import fixture** reproduced **3/3 pre-fix failures** when invoked via `python -I <script> --help`. After adding the exact bootstrap pattern, the new dynamic test module passed **12/12 normal and 12/12 with `-OO` (24/24 fixture executions)**, with hostile shadow modules in cwd/PYTHONPATH. This fixture validates the test harness and specific interpreter behavior; **it does not verify the full committed repository modules**. The private GitHub repo's complete entrypoints and full test suite still require hosted CI or a trusted checkout. Hosted Ubuntu/Windows Actions were previously failing before runner assignment. There is still no genuine Windows 11 x64 candidate build, Windows GUI/accessibility pass, Defender scan, premium access-control verification or QD/founder authorization.

## Release gate and next highest-impact action

1. Restore GitHub-hosted runner access; run the R272 exact branch (including 12 isolated entrypoint checks in normal and optimized suite) and complete full Python regressions.
2. On a trusted Windows 11 x64 machine with preinstalled audited dependencies and restricted private workspace, run `py -3.12 -I products/desktop/scripts/offline_windows_candidate_r269.py --workspace <PRIVATE_LOCAL_DIRECTORY>`. Retain all evidence locally.
3. Independently verify six real portable EXEs, SHA-256 reports, Defender and accessibility checks; restrict both premium files with validated payment/entitlement controls. No site publication or production merge without independent QD and founder approval.
