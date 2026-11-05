# R200 — Audit CI matrix catch-up (DRAFT / HARD RELEASE HOLD)

Tracking: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73

Parent: R199 draft PR #1029 at immutable SHA d0ee6b2be3abcbc9b2435201f577fb54203a847a, NOT main.

## Defect and implementation

The existing Ubuntu and Windows desktop workflow explicitly ran R191–R193, but omitted the six newer R194–R199 regression modules. Ordinary unittest discovery can exit 0 when it finds zero tests. This creates a false-green regression gate if a test filename is mistyped, removed or renamed.

Added products/desktop/scripts/safe_recent_regressions_r200.py, a standard-library-only runner that validates exactly named and present, non-symlinked test files; refuses wildcard, duplicate and traversing selectors; requires at least audited test counts; fails closed on test errors, failures, empty/all-skipped modules; and visibly reports individual platform-specific skips. Counts: R194 28, R195 29, R196 22, R197 21, R198 26, R199 22 = **148 inherited test methods per mode**.

Added products/desktop/tests/test_recent_regression_gate_r200.py with 16 synthetic acceptance tests of the runner. Added R200 self-test and audit-matrix steps to both independent Ubuntu and Windows jobs, each in normal and optimized -OO Python. Windows checks the process exit code after each command, before executable packaging. No extra artifact uploads or public downloads.

## Measured verification

Locally executed on Linux CPython 3.13.5 using isolated, matching R200 Git blobs:
- 16/16 synthetic runner tests PASS normal.
- 16/16 PASS optimized (-OO).
- 32/32 focused self-test executions total; zero skipped in these self-tests.
- py_compile PASS.
- GitHub inspected source runner blob bee36143c2519f560edc955c81922894be6b8a32 and self-test blob e79f598f91e05d5a964029c721faa81b6d5ddefb; these match locally tested git hash-object values.
- GitHub workflow blob 0b227595a9b74778a03581c09ecf14a882f8c920: BOTH jobs contain four R200 Python commands, and Windows has four explicit nonzero exit checks. Existing six inherited modules exist, with 28/29/22/21/26/22 test_ methods confirmed.

The inherited 148-test matrix was NOT executed in a complete local checkout. The 296 inherited tests per job (148 × two modes) are planned CI executions, NOT observed passes.

## Blocking gates

Hosted R199 Actions #41959176543 (https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41959176543) recorded failed Ubuntu/Windows jobs with no runner steps. Check Actions billing/usage, workflow permissions and runner allocation; rerun the exact R200 head after the runner problem is fixed. Before release: full inherited suite, privately built/checksummed/scanned/launched six Windows x64 candidates, real Windows 11 accessibility testing, signing, premium delivery entitlement protection, independent QD and founder authorization. Nothing public or production has been published.

R197 may skip an OS-restricted symlink test on Windows; that skip is disclosed and does not count as passing Windows symlink coverage. No telemetry, customer financial data, automated compliance decisions or money arithmetic were changed.
