# R508 — restore reviewed desktop-build workflow byte ceiling (QD HARD HOLD)

**Tracking:** [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Feature branch `feature/labs-r508-ci-budget-restoration-20261117`, stacked only on R507 draft #2920. Not production `main`. No build, distribution, premium entitlement or founder/QD approval is claimed.

## Actual change and regression boundary

The six-application Windows x64 internal-build GitHub Actions workflow had grown to **242,075 UTF-8 bytes**, exceeding the existing reviewed `224 * 1024 = 229,376` byte policy ceiling by **12,699 bytes**. The repository's `test_ci_workflow_budget_r292.py` therefore could not pass on the inherited workflow, even after runners are restored.

R508 restores the existing ceiling **without changing the ceiling** or removing any step, PowerShell exit-check, Python test command, six-application packaging operation, artifact allowlist, signing/entitlement behavior or Windows smoke check. It shortens **521 redundant Windows *test* exception descriptions** to fixed `R### test FAILED` messages. The original test and security-gate step names still supply context, and critical distribution/premium/release-HOLD exception descriptions remain intact.

An exact in-memory before/after comparison on the checked-out GitHub blobs confirmed that **only** 521 strings inside otherwise identical `if ($LASTEXITCODE -ne 0) { throw ... }` statements changed. In particular:

| Invariant | Before | R508 |
| --- | ---: | ---: |
| Workflow UTF-8 bytes | 242,075 | **228,330** |
| Reviewed maximum | 229,376 | **229,376** |
| Total lines | 3,302 | **3,302** |
| GitHub step labels | 492 | **492** |
| Python unittest-discover invocations | 816 | **816** |
| PowerShell nonzero-exit checks | 566 | **566** |
| New compact fixed test exceptions | 0 | **521** |
| Existing source/Windows jobs and action pins | retained | **retained** |

The new `test_ci_step_compaction_r508.py` checks these reviewed lower bounds and release/HOLD markers against the actual workflow, rather than silently raising the size limit. The read-only R507 Linux/Windows identity workflow also schedules the new static regression in normal and optimized Python modes.

## Evidence, limitations and next blocker

Exact GitHub-connector in-memory source parity assertions passed: 521 changed lines only, non-error text and command/run structure identical, full Python invocation inventory unchanged, all 566 fail-closed status checks intact, UTF-8 ceiling satisfied. These are **static checks**, not a hosted Python suite or executable smoke. Native Windows x64, Defender, accessibility, premium entitlements, cryptographic signatures, complete six-app regression, and approval remain **unverified**.

The separate independent `.github/workflows/desktop-source-evidence-r385.yml` remains **60,506 bytes** while its existing `test_independent_ci_r385.py` requires **strictly under 8,192 bytes**. This second deterministic size test still fails; it was not bypassed or weakened. Next engineering sprint should extract its complete two-mode source-test list into a checked-in strict runner/manifest, with a verified test inventory so that no required coverage disappears. Preserve its independent read-only job and restore the 8-KiB bound rather than relaxing the test.

Separately, the R507 baseline [internal build #44189087625](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44189087625), [source evidence #44189087546](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44189087546), and [identity preflight #44189087740](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44189087740) all completed failure **before any executable step** (six jobs `steps=null`; no runner identified). The account/runner cause has not been established. Check Actions eligibility, policies and billing; then rerun exact R508 head. Do not describe source-only checks as release certification.

**Release remains HOLD:** no production branch mutation, merges, WordPress edits, EXE uploads, public premium URLs, payment changes, or QD/founder approvals. Local-only customer financial processing, Decimal money rules, deterministic source/audit records and mandatory human compliance review are untouched.
