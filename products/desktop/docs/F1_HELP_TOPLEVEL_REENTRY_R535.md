# Labs R535 — F1 re-entry from the help window itself

**DRAFT / QD + explicit founder HARD HOLD.** Isolated branch stacked on R534 draft PR #3066, parent `cd8d2be5f574fa8b097c2cd02d4d1c2a01f6c1cf`; no change to production `main`.

## Reproduced accessibility defect

The six apps install F1 on their main Tk root. The scrollable help popup created by `show_keyboard_help` is a *separate Tk Toplevel*. When keyboard focus moves to its read-only Text or Close button, its bindtags do **not** include the application's root, so F1 from the help window was ignored. The previous focused behavior tests called the helper directly and did not dispatch a real key event inside the Toplevel.

## Implementation

- Bind `<F1>` only on the **help Toplevel**, not globally: all its child widgets inherit this toplevel key binding.
- The handler routes back through `show_keyboard_help(root, legend)`, which reuses and refocuses the single live help window or reconstructs the help Text after external destruction; it returns `"break"` to stop additional processing.
- Preserve existing Escape, Close, original form-focus restoration request, bounded static text, Tk scroller, no global `bind_all`, and no accidental Generate/Browse/Review invocation.
- No financial data reading, network/telemetry, Decimal changes, generated reports, entitlement bypass, audit evidence mutation, compliance auto-decisions, premium distribution or WordPress publication.

## Changed paths

1. `products/desktop/fvs_suite/keyboard_access.py`: Toplevel-scoped F1 handler/binding.
2. `products/desktop/tests/test_keyboard_help_reentry_r535.py`: **9 committed tests**, four mandatory mocked/headless and five native-Tk tests that skip only without a display.
3. This runbook.

## Executed isolated Linux evidence (NOT full repo)

Local environment: Linux CPython 3.13.5, Tk 8.6, Xvfb. The local `format_keyboard_help` + `show_keyboard_help` source excerpt is byte-for-byte FNV-1a32 **`b1bd48b7`** across 6,264 characters, matched against the R535 GitHub source. The new 7,000-byte committed test module matches the locally executed copy at FNV-1a32 **`251705c5`**. The local package intentionally contains only the exact extracted helper functions; this evidence **does not** certify the full committed module's imports or the remainder of the desktop suite.

Run from the local isolated package root:

```shell
xvfb-run -a python -m unittest discover -s tests -p test_keyboard_help_reentry_r535.py -v
xvfb-run -a python -OO -m unittest discover -s tests -p test_keyboard_help_reentry_r535.py -v
```

**9/9 PASS** normal and **9/9 PASS** optimized, **18 focused test executions**: Tk Text-F1, Close-F1, destroyed Text recovery, Escape original-focus restoration request, no global/root binding, and mocked repeat/rebuild behaviors. A negative control removing only the new Toplevel F1 binding produces **6 failures of 9** (expected), distinguishing tested behavior from the prior unhandled event. One initial Xvfb test asserted immediate operating-system keyboard focus after transient destruction and failed; the committed test now correctly asserts the original form widget received the `focus_set` restoration request instead. Native Windows focus retention still requires human verification.

## Verification and release blockers

The complete inherited R44 suite, 416-command source matrix, six native Windows x64 binaries, install/uninstall, NVDA/Narrator, 100/200/400% scaling, Defender scanning, SHA256, premium entitlement and protected-link checks **have not run**. GitHub Actions runner jobs on the R534 parent failed before steps (`steps=null`), tracked in #75. This sprint cannot prove Windows release readiness or claim the full committed regression module passed.

**Next highest-impact action:** fix Actions runner allocation/billing/workflow eligibility so one tiny source job executes with preserved step logs, then run the new and inherited committed suites in normal/-OO and all Windows release gates. No merge, deployment, public executable or premium URL until independent QD review and explicit founder approval.
