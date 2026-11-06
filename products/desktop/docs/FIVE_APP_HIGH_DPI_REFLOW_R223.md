# R223 — Five-app keyboard-first high-DPI form reflow (source-only, release HOLD)

**Date:** 2026-11-05 PT  
**Target:** Issue #73, all six Windows x64 utilities; this increment changes five forms and preserves the existing LedgerDiff Lite row contract (R133).  
**Disposition:** Draft PR, independent QD/founder approval required. No built/published executable or premium entitlement is introduced.

## Before / concrete problem
The existing LedgerDiff Lite form has a separate stacked-entry layout because 65-character path fields with adjacent Browse buttons overflow narrow/high-DPI Tk viewports. The other five tools still used the old multi-column fixed-width layout. At 200% and especially 400% scaling, the requested width could hide required input paths, picker controls or premium review actions.

## Changed
- `fvs_suite/form_layout.py` defines a pure, deterministic five-app row plan. Each required input has **three independent rows** (label, flexible-width Entry, Browse); the output folder has the same pattern.
- `fvs_suite/app.py` now uses that plan for Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro. No 65-character path Entry remains. The shared ScrollableForm retains native vertical focus reveal and Tab order.
- Invoice Twin's near-match days field gets independent label/entry rows. ProcureGuard's optional JSON price policy gets its own label, entry and Browse rows. Human-only premium review remains after Generate; the entitlement checks are unchanged.
- LedgerDiff Lite's existing R133 row plan, optional match/amount settings, premium separation, rule engines and local-first handling are untouched. Geometry uses only application IDs and input counts, never file paths or financial values.

## Evidence — accurately scoped
Locally reconstructed **byte-identical Git blobs** of new form-layout helper `632564ccfde94a96e3993fe51be2d3f4d8423216` and its 16-test module `c34f21da52a9683ca40488a8f9e185d9a3477222`. Linux CPython 3.13.5:

- `PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_standard_stacked_layout_r223.py' -q`: **16/16 PASS**.
- `PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_standard_stacked_layout_r223.py' -q`: **16/16 PASS**.
- `python -m compileall -q fvs_suite tests`: **PASS** for isolated helper/tests.
- Tests check five application inventories, sequential/nonoverlapping rows, Tab/Browse ordering, invoice window, policy picker, premium review isolation, fail-closed malformed IDs/counts, deterministic repeatability and no financial values in geometry.
- The changed full `app.py`, complete inherited 261-file suite, real Tk accessibility, Ubuntu/Windows CI, Windows EXEs and installer/distribution chain are **NOT locally verified**. This is **not** native Windows accessibility certification. The existing offline source gate will discover new `test_*.py` tests when a runner is available.

## Owner/QD acceptance gate
1. Restore Actions runner provisioning and execute full-source suite, including R133 and R223, in both normal and `-OO` modes on Ubuntu and Windows; preserve failure details without customer data.
2. On a **real Windows 11 x64 desktop**, observe all six forms at 100%, 200%, and 400% scaling: no horizontal loss, visible/scrollable Browse and Generate, sequential Tab/Shift+Tab, Alt+number and Ctrl+number, invoice window, procurement policy picker, disabled premium launch without entitlement and human review authorization. Record physical screenshot/witness results privately; do not interpret headless row plans as physical acceptance.
3. Independently build, checksum, malware scan and smoke-test the six private x64 executables. Verify premium access controls and keep binary artifacts private. QD review and explicit founder authorization remain mandatory before any release.

**Next highest-impact:** obtain real Windows scaled-layout observations and unblock CI; do not widen release claims based on source-only geometry tests.
