# R403 — Six-app keyboard shortcut target preflight (DRAFT / HARD HOLD)

Issue: #73. Branch: `feature/labs-r403-keyboard-target-preflight-20261113`. Parent: R402 draft #2345, not `main`.

## Problem and change

The existing six-app Tk shortcut installer validated that Generate/Review buttons had an `invoke` method, but did **not** validate the focus or invocation methods on source fields, Browse buttons, output controls, the invoice near-match window, ProcureGuard's policy controls, or LedgerDiff's four optional column fields. An accidentally miswired widget could therefore register a partial shortcut map and fail only when a keyboard-only operator attempted to use that action. This is a control-wiring reliability and accessibility issue; it is not a reported customer incident.

A new, pure, dependency-free `shortcut_targets_r403.validate_shortcut_targets` checks all required methods and exact container shapes before the first `root.bind` call. `keyboard_access.install_shortcuts` calls the preflight before constructing handlers. No button is invoked by the preflight. Successful shortcuts still invoke the existing native Tk widgets, including original premium entitlement and human-review commands; existing duplicate/rollback safeguards are unchanged.

Coverage includes the four free tools (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and both gated premium tools (GrantAudit Studio Pro, ProcureGuard Studio Pro). No file contents, customer paths, money, network operations or report evidence are touched.

## Evidence and limits

- **Locally executed** on isolated CPython source, using the *exact Git blob* of the newly authored validator (`a1e41291fa32ed52d6f972c681bab11f6ffacf9e`) and the corresponding 24-method test file (`68d625758d159b3a725047093dcd998ed5029646`): 24/24 in normal Python, 24/24 with `-OO -W error`, 48/48 total test-method executions. `py_compile` passed. Synthetic widgets only; no customer data or Windows GUI.
- **Authored but NOT locally executed:** 10 additional integration regression methods importing the real `keyboard_access.install_shortcuts` and validating that malformed targets cause zero `root.bind` registrations. The R44 inherited keyboard suite also requires the complete checkout.
- **CI wired but NOT passing:** independent `.github/workflows/desktop-source-evidence-r385.yml` invokes all three test modules in normal/optimized Python on Ubuntu and Windows. The exact-HEAD workflow must actually run before integrated acceptance.
- **Not validated:** real GUI Tab/focus order, NVDA/Narrator, Windows high-DPI, six native x64 launchers, code signing, Defender, premium download gating, and QD/founder approval.

## Smallest unblock and next step

Existing R402 source/build workflows failed before any test steps. Restore hosted GitHub Actions runner execution (inspect GitHub check annotations, account billing/spending restrictions and hosted-runner eligibility), then run the R403 workflow on its exact commit on both operating systems. Preserve stacked draft PR, do not merge to `main` without independent QD/founder review, and do not publish executables or unrestricted premium artifacts.
