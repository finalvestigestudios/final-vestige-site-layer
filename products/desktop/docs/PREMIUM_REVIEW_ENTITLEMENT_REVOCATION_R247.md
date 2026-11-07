# R247 — Premium review entitlement revocation and post-dialog authorization custody

**Issue #73 | Draft only | Independent QD + founder HARD HOLD.**

## Defect and scope

In the existing human-review workbench for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**, failed entitlement revalidation produced a warning but left the previous customer's exception queue, report path, reviewer identity and drafted rationale visible. A license could also expire or be replaced while an operator kept a folder/password picker open: the initial authorization check occurred *before* that modal interaction, not immediately before writing a review, exporting a register, or sealing/restoring evidence.

## Implementation

- `fvs_suite.review_target.revalidate_or_revoke`: checks the existing authoritative offline signed-license callback again; expected denial exceptions or an explicit `False` result cause a fail-closed local screen-clear callback. No remote lookup, license printing, file changes or implicit approvals.
- `fvs_suite.review_ui`: upon denial, clear the loaded batch, visible exception table, displayed report path, reviewer field, outcome selection and drafted rationale **before** showing a generic error. Reports/journals on disk remain untouched and can only be reopened after a fresh entitlement verification.
- A second license recheck is placed immediately before `append_review`, `export_register`, `seal_evidence` and `restore_evidence`, including **after** modal source, destination and passphrase dialogs. This limits the stale-entitlement interval; it is not an atomic OS-enforced authorization lease.
- The suite's existing source gate and Windows packaging restrictions are unchanged. No premium distribution keys or executable output added.

## Tests / evidence

`products/desktop/tests/test_review_revocation_r247.py` contains **15 tests**: nine behavior tests of the standalone guard using synthetic callbacks and six displayless AST inspection tests of the actual GUI source wiring/operation ordering. Hosted CI is instructed to run normal and `-OO -W error` modes on Ubuntu and Windows **before** the full source-suite gates.

Local Linux CPython 3.13.5: guard behavior **9/9 PASS** normal and **9/9 PASS** optimized (18 test executions); `py_compile` PASS for guard and regression test. These runs used local reconstructed source; the full GitHub repository, GUI integration, AST wiring tests and Windows-native behavior were not executed in that initial local environment. The committed GUI wiring was additionally checked against the GitHub source text. Do not describe this as 15/15 or native Windows verified before CI evidence exists.

## QD acceptance on Windows 11 x64, synthetic-only

1. With a test entitlement, load synthetic exceptions and type a reviewer/rationale. Change the test license to expired/revoked and try Record, Export, Seal and Restore separately. **No side-effect**, no visible source path/cases/reviewer/rationale after denial.
2. Reopen a valid test entitlement and verify the operator must explicitly browse/reload the report; historical journal bytes unchanged.
3. Open a folder/password picker while the license is still valid, make the signed test license invalid, then complete the picker: no write/export/encryption/restore and queue cleared. Repeat with keyboard, screen reader and high-DPI scaling.
4. Repeat under both products; confirm never a payment authorization or automated audit decision. Run full 281+ module source gate, private six-app builds, SHA-256, malware scan, protected premium-access validation and independent QD/founder release review.

## Blockers / release state

Hosted GitHub Actions [R246 #42327109687](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42327109687) reported both Ubuntu and Windows jobs failed with **zero execution steps**. Check Actions billing/spending availability, workflow permissions and runner allocation; then rerun the unchanged R247 head. Root cause remains unconfirmed. **All six applications remain unreleased.** No production branch/WordPress changes, no uploaded binaries, no published premium files or signing secrets.
