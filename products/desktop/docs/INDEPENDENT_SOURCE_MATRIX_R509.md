# R509 — Restore the independent source-evidence workflow 8-KiB custody bound

Status: **DRAFT / HARD HOLD — NOT a Windows release or QD approval**. Issue #73.

## Specific problem and fix
R508 leaves `.github/workflows/desktop-source-evidence-r385.yml` at **60,506 bytes**, while inherited `test_independent_ci_r385.py` rejects bytes >=8,192. The source matrix comprises exactly **414 inherited Python commands** (410 unittest commands: **205 normal + 205 -OO**; plus 4 independent smoke/inventory commands). GitHub Actions has not run the matrix because jobs fail before runner assignment.

R509 moves the exact commands (original order, including duplicates) into a versioned plain-text inventory `products/desktop/ci/source_evidence_commands_r509.txt`. One **fail-closed** Python runner replaces 109 named run steps, retaining the pinned checkout, Python 3.12, pinned cryptography 46.0.4, no credentials persistence, read-only token, pull_request/workflow_dispatch trigger, Linux/Windows matrix, PYTHONPATH, sequential execution, and 20-minute job limit. Each child uses an argv array, not a shell. Private stdout/stderr are suppressed and error notices are fixed; nonzero exit/timeout/missing-file/malformed commands stop the job. The inventory's Git blob SHA-1 is pinned in the runner; the 414-command prefix is separately pinned to prevent accidental regressions. New R509 tests are appended in both Python modes (416 total).

No inherited command was removed, reordered or optimized away. This changes **observability and step granularity**: original named GitHub steps are now one checked runner step with deterministic command index. It does not prove all commands pass, and the hosted runner's 20-minute timeout could need review after actual execution; never raise the limit without review.

## Reviewable evidence
- Original R508 workflow Git blob: `362528686cc9ca70042d48b5853cca1571717967`, **60,506 bytes**
- Original 414 commands (newline terminated) Git blob: `cbebff514baf4244754125c6d73e429b74f6b4e1`
- New 416-command inventory Git blob: `a55a9b5bcbee5b9f075a39fc581ed5a4716eaca3`
- New workflow bytes: **1376** (<8192)
- Existing R385 custody tests retarget their test presence/count checks to the immutable manifest (16 methods retained).
- Added **11** R509 regression methods: original prefix identity, exact digest, all source tests present, two modes, invalid command injection rejection, missing files, truncated/modified inventory, fail-closed execution, redacted private errors, read-only workflow size/permissions, zero checks.
- Static JS preflight checked all **414** inherited lines against the allowlist; normal/optimized counts **205/205**; source runner/test syntax and hosted execution **not verified** on GitHub.

## Release custody / next verification
1. Run full `python -B -W error -m unittest discover -s products/desktop/tests -p test_independent_ci_r385.py` and `test_source_evidence_runner_r509.py` locally on a complete checkout, in both modes. This connected GitHub edit environment cannot execute Python in the private repository.
2. Repo owner confirms Actions billing, spending limit, runner eligibility and repository workflow policy. Retry this exact commit and inspect Linux/Windows logs: all 416 subprocesses must complete, no test skips incorrectly treated as release approval.
3. Perform native six-EXE package smoke, hashes, Defender, keyboard/accessibility and premium download entitlement tests. Independent QD review and explicit founder authorization are **still required**. No executable or premium file was published.
