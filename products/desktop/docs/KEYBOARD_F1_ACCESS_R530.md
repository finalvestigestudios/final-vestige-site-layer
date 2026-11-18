# R530 — F1 keyboard-help access across all six standalone desktop apps

**Date:** 2026-11-18. **Issue:** #73. **Status:** source-only DRAFT; independent QD and founder HARD HOLD. Based on R529 draft PR #3038 at `afb236cbee7454c469f81a4dd8775b2b3aa4b64c`, not production `main`.

## User-facing accessibility gap

Every app displayed a static shortcut legend beneath its input and report controls. At high-DPI scaling and on small screens, that text can be far below the current scroll position. Users navigating by keyboard cannot reliably discover commands without reaching the bottom of the form.

R530 binds **F1** to a standard local Tk help dialog showing the same product-specific shortcut legend. It works in LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro because their common launcher passes the optional help action. The existing keyboard legend also mentions F1.

The callback is not registered at all for existing callers that omit `help_action`, preserving the earlier exact shortcut inventories. Invalid noncallable help actions fail *before* registering any key. As with existing action registrations, F1 remains inert until the complete additive binding sequence is accepted. An uncertain callback acknowledgement leaves any orphan callback inactive.

F1 cannot trigger Generate, Browse, or premium Review. The dialog contains static application help text, no file paths, source data, entitlement contents, amounts, reports, or telemetry. The existing premium entitlement and human-review gates remain unchanged.

## Changed source and regression inventory

- `products/desktop/fvs_suite/keyboard_access.py`: optional `help_action`, fail-closed type validation, additive F1 key registration with existing staged activation and rollback.
- `products/desktop/fvs_suite/app.py`: on-demand product-specific help dialog for all six launchers; bottom legend documents F1.
- `products/desktop/tests/test_keyboard_access_r44.py`: eight synthetic headless regression methods covering legacy compatibility, invalid callbacks, no eager execution, F1 dispatch, premium review isolation, one/two/three-input geometry, deterministic order, and uncertain acknowledgement.
- No new package/test modules, no changes to the 416-command approved source matrix, no payment/compliance logic changes.

## Evidence and required validation

Commit writes are recorded in GitHub; source files were patched on the feature branch only. **No actual committed Python test execution is claimed in this sprint unless a corresponding runnable receipt is attached.** GitHub Actions has repeatedly failed before runner steps start (#75), so a failed hosted job is *not* an application-test failure. F1 and screen-reader behavior on native Windows 11 remain unverified.

To reproduce the focused test locally:

```shell
cd products/desktop
python -m unittest discover -s tests -p 'test_keyboard_access_r44.py' -v
python -OO -m unittest discover -s tests -p 'test_keyboard_access_r44.py' -v
```

Also run the full pinned source gate from repository root:

```shell
python -B -W error products/desktop/scripts/source_evidence_runner_r509.py
```

Then run native Windows 11 accessibility acceptance (F1 on every one of six forms at 100%, 200% and 400% scaling, dialog focus and dismissal, screen-reader announcements, unchanged Generate/Browse/Review bindings), Windows x64 packaging, AV/Defender, six-distinct-image SHA256 checks, smoke and premium entitlement checks. **Neither source results nor a help dialog authorize release.**

## Release and next action

All six apps remain unpublished. No Windows EXE, distribution URL, WordPress change, unsigned customer package, or premium file was published. **Next highest-impact step:** restore a single GitHub Actions runner execution (check account billing/spending cap and Actions policies as owner, inspect job-start banner), then execute this committed head's real R44 tests and the 416-command matrix before Windows human accessibility QA and QD/founder review.
