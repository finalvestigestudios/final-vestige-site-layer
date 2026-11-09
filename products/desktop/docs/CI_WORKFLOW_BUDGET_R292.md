# Labs R292 — restore bounded CI preflight for the six-app workflow

**Status: draft / NOT a build or release.** Tracks issue #73. This branch
is stacked on R291 (commit `624ccf32180ad383e69487a6531da8b18a3fd20d`),
not the protected `main` branch. Independent QD and founder approval remain
mandatory before merge, website publication, or executable distribution.

## Verified failure mechanism (not the hosted runner failure)

At R291, the committed `.github/workflows/desktop-build.yml` contained
**152,122 characters (ASCII)**, exceeding an independent **131,072-byte**
preflight ceiling in all four security validators:
`ci_artifact_policy.py`, `ci_action_key_guard_r164.py`,
`ci_action_pin_guard.py` and `ci_source_contract.py`.

This is a reproducible **static source-level contradiction**: once runner
execution becomes possible, all four preflight checks reject that unchanged
workflow before validating the intended six-app gates. It is **not** proof that
this contradiction caused the earlier GitHub Actions jobs to fail; those jobs
recorded no steps, and the runner infrastructure cause remains unconfirmed.

## R292 change

- Four existing security preflights import one reviewed
  `MAX_WORKFLOW_BYTES = 192 * 1024` from
  `ci_workflow_budget_r292.py`, retaining finite UTF-8 byte limits.
- All previous **allowlists and fail-closed rules** remain unchanged:
  six immutable GitHub Actions source SHA pins, canonical action-bearing YAML
  keys, exactly two allowlisted uploads excluding EXEs and premium files,
  mandatory unconditional normal/-OO source suites preceding any Windows build.
- Ten new regression methods operate on the **real checked-out workflow**,
  including its original >128 KiB size, four-validator agreement, previous-cap
  negative controls, exact 192 KiB boundary, one-byte and Unicode overflow,
  malicious action substitution, executable upload expansion, required source
  gate removal and NUL byte rejection.
- Ubuntu and Windows workflow jobs explicitly execute these tests in both
  standard and optimized Python and fail on nonzero returns. No binary
  artifact, release URL, premium entitlement or production path changed.

## Reproduce after checking out this branch

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_ci_workflow_budget_r292.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_ci_workflow_budget_r292.py' -v
python -m py_compile products/desktop/ci_workflow_budget_r292.py products/desktop/tests/test_ci_workflow_budget_r292.py
python products/desktop/ci_artifact_policy.py .github/workflows/desktop-build.yml
python products/desktop/ci_action_pin_guard.py .github/workflows/desktop-build.yml
python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
```

## Evidence, limits and next action

- The R291 pre-change workflow size, four distinct 128 KiB limits, and
  both CI job structures were read from exact GitHub branch files.
- This patch changes only the limit imports and adds regression/test wiring;
  it does **not** suppress action provenance, broaden artifact uploads,
  skip any source suite or authorize release.
- The local working environment cannot clone the private GitHub repository
  (network name resolution disabled). Source-level/static checks can be
  inspected, but the **committed full-checkout R292 Python regression,
  complete inherited tests, Ubuntu hosted job and Windows native build must
  not be claimed passed** until executed with their exact GitHub blobs.
- Earlier [R291 Actions run #42533232774](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42533232774)
  completed failure with both job records showing `steps:null`; infrastructure
  cause is not known. Owner must inspect Actions billing/spend restrictions,
  workflow policies and runner availability, then rerun R292 unchanged.
- Follow with all-six Windows 11 x64 private build, PE/SHA-256/Defender and
  real smoke tests, accessibility, and verified protected premium distribution.
  **No executables/downloads, production updates, automated compliance
  approvals or QD/founder release approval are delivered here.**
