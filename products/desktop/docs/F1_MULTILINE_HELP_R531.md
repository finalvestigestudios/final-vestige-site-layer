# R531 — readable, bounded F1 keyboard help for six desktop applications

**Date:** 2026-11-18. **Issue:** #73. **Base:** R530 draft PR #3045 at `f7752944ff531c9fb68ff18c6afd8b0f83267f99`. **Status:** internal source-only DRAFT; independent QD review and explicit founder approval HOLD. No release/distribution authorization.

## Problem / acceptance criterion

R530 made static keyboard help accessible with F1, but passed the entire semicolon-separated one-line legend directly to a Windows/Tk modal. Depending on OS display scaling and assistive technologies, a very long message can be difficult to scan or announce. This sprint makes the **existing** static legend a compact, ordered, one-shortcut-per-line message. It does not alter or register an additional keyboard action.

Across LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro:

- `format_keyboard_help()` accepts only a native Python `str` with a `Keyboard: ` prefix, 1–700 characters, 4–12 semicolon-separated shortcut sections, at most 75 characters per section and no ASCII control characters or malformed embedded separators. It rejects malformed or oversized legends with generic errors, never interpolates customer fields.
- The F1 action formats its legend **lazily** (only when pressed); registration is inert and the existing Generate/Browse/premium Review widget invocations remain unchanged.
- Invoice Twin's static near-match-window description now uses a comma rather than an internal semicolon, so the complete `Alt+W` instruction stays on one help line. No financial matching rule or day-window default was changed.
- No telemetry, file access, customer path, financial value, entitlement token or source row enters the help message. No display claim of legal/compliance/payment approval.

## Changed, inventoried paths

1. `products/desktop/fvs_suite/keyboard_access.py` — bounded, screen-reader-oriented deterministic line formatter; existing Tk shortcut registration unchanged.
2. `products/desktop/fvs_suite/app.py` — formats the static legend when F1 is pressed; Invoice Twin hint punctuation avoids splitting a single instruction.
3. `products/desktop/tests/test_keyboard_access_r44.py` — ten new headless methods: output lines/order; LedgerDiff/Invoice Twin/ProcureGuard labels; lazy read-only dispatch; type, control, separator, length and privacy bounds.
4. This runbook.

No new package module or test filename; the existing pinned **416-command** source manifest is unchanged.

## Measured evidence and limits

An **isolated local Python probe of the new formatter** completed 10/10 passing under ordinary Python and 10/10 passing under `python -OO` (20 total). A separate local probe constructed the six static hints using the current app rules and observed formatted section counts of **8, 7, 6, 6, 7 and 9**, with maximum rendered line length of **59 characters** (excluding OS decoration). These are synthetic checks of the standalone formatter implementation; **they are not executions of the committed repository test module or native Windows Tk UI**. Do not cite them as proof that Windows Narrator/NVDA or 400% scaling passed.

## Required reproducible validation (HOLD)

From repository root at this PR head:

```bash
cd products/desktop
python -m unittest discover -s tests -p 'test_keyboard_access_r44.py' -v
python -OO -m unittest discover -s tests -p 'test_keyboard_access_r44.py' -v
cd ../..
python -B -W error products/desktop/scripts/source_evidence_runner_r509.py
```

On **native Windows x64** run each of the six launchers; place focus in the first input and press F1 at 100%, 200% and 400% scaling. Verify legible lines, focus transfer into the Windows/Tk modal, Narrator or NVDA announcement, Enter/Escape dismissal, and restoration of focus. Verify that Generate/Browse do not fire from F1, and the two premium review controls cannot bypass live entitlement or human confirmation. Build and smoke-test all six distinct binaries, run Defender, SHA-256, access controls and distribution-link verification **before** any publication.

## Infrastructure, review and release gate

GitHub Actions workflow jobs have been failing *before step execution*; issue #75 tracks the unknown startup cause. An owner must inspect the first failed job's Actions UI startup banner, check Actions billing/spending limits and runner eligibility/policies, and restore **one** running job with step logs. Only then claim real committed regression/416-command/source verification and native Windows acceptance. GitHub Actions startup failure is not a regression-test failure.

**Never merge directly to `main` or change the WordPress catalog from this draft.** Independent QD review and explicit founder approval remain prerequisites. No untested EXE may be published, and premium executables must stay behind verified access controls. All four free and two premium desktop utilities remain unreleased.
