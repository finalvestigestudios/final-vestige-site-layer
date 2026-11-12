# R385 — Independent six-engine source CI and runner triage

Issue: [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This is **source-only evidence**, not executable verification or production/QD authorization.

## Why this change exists

At R384 HEAD `4c812d97a68ca6d69f800790e9982078bae32974`, the existing `.github/workflows/desktop-build.yml` has **225,491 bytes**, and [run 43286845742](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43286845742) failed before any steps on both `ubuntu-24.04` and `windows-latest`. GitHub job records show `runner_id=0`, `steps=[]`. This does **not** identify the underlying cause; billing/runner access and workflow-specific problems are both still hypotheses.

## R385 implementation

- Added an independent, small, read-only, pinned-action `desktop-source-evidence-r385.yml` workflow. It uses an Ubuntu/Windows matrix, avoids the R384 workflow's large step graph, and creates **no artifacts** or releases.
- Executes the **existing** source-inventory gate (SHA-256 before/after six real synthetic engine smokes) in standard and `-OO` modes.
- Requires existing six-app financial safety tests, 22-case genuine AES-GCM gate, real Ed25519 verifier/issuer, SQLite registry, and latest R384 entitlement privacy tests in both modes. These are **configured**, not yet proved to have executed in GitHub Actions.
- Added 16 fail-closed, standard-library workflow-custody tests covering read-only permissions, restricted triggers, immutable action refs, both hosted platforms, non-publishing/no-binary behavior, fixed six-engine coverage, crypto and issuer/registry expectations.

## Evidence and interpretation

Local Python 3.13.5: **16/16 PASS** standard with `-W error`; **16/16 PASS** with `-OO -W error`, **32 passing test executions** total. PyYAML BaseLoader parsed the matrix with two platforms and nine steps. GitHub blobs for new workflow and tests matched the locally executed files using `git hash-object`. This checks workflow *structure* only, not runtime source integration or Windows execution.

When the draft PR is opened, compare the **new** R385 workflow run with the **old** desktop-build run:
- If R385 receives actual runners while the old workflow fails before step 1, inspect the older workflow's constraints, size and job setup.
- If **both** fail with `runner_id=0` and `steps=[]`, investigate repository/organization Actions billing and spending, hosted-runner eligibility, restrictions and the check annotations. Do **not** claim that one cause is proved.
- If R385 reaches actual steps, inspect **real failures**; no green claims until all gates pass in the checked-out code.

## Hard release hold

No executable build, malware scan, Win11 GUI/keyboard acceptance, license distribution, or paid download is authorized by this workflow. No customer data, signing keys, live entitlements, premium files, or credentials are used. Production `main` and the site's independent QD/founder approval process remain untouched.

**Next highest-impact action:** restore GitHub hosted-runner allocation (or isolate a real step failure), run the complete source suite and genuine crypto integration on exact HEAD, then perform native six-EXE Windows x64 smoke/Defender/accessibility verification and controlled premium distribution review.
