# Apollo R102 — actual WordPress interaction acceptance + redacted LCP diagnosis

Status: **STAGING HOLD — not approved for publication or merge.** Issue #150.

## What R102 changes

1. Extends the *existing real disposable WordPress 6.8.3* browser harness (`browser_actual_wordpress_r100.py`) with eight independent interactive scenarios: 320, 390, 1440 and 1920px, each with JavaScript enabled/disabled. Forces high-contrast at 320/1920, reduced motion at all widths, and real touchscreen input at 320/390. This is not a simulated WordPress hook test.
2. In the gallery, selects two exact NASA records and verifies the populated provenance table, a third selection's rejection and status announcement, keyboard-focused reset, six visible sources without JavaScript, absence of photographs and speculative geo elements.
3. In the Atlas, checks month-only versus day-specific date precision, `aria-pressed`, zero-results state, hidden-record deep-link restoration, focused target, and complete no-JS record access.
4. Adds real Chromium screenshots for the paired-source comparison and restored Atlas at 390px and 1440px (SHA-256 inside the normal receipt); injects pinned axe-core 4.14.0 in the controlled QA context on the restored interactive Atlas at those two widths. Ordinary loading and request checks remain active.
5. The preexisting R100 receipt and LCP/CLS metrics remain; **zero existing source records, NASA URLs, reuse statuses, date uncertainties, plugin content, or production pages are changed.**
6. Keeps the **unchanged** R77 Assembler nested-Gutenberg LCP budget at 2500ms and CLS at 0.1. Writes a bounded, *numeric-only, fail-closed* `R102_R77_PERFORMANCE_DIAGNOSTIC.json` before the assertions. Records width, JS state, rounded LCP, CLS millionths and whether budget was exceeded; it cannot include URLs, credentials, local paths, DOM text or browser exceptions. A failed performance gate must remain failed.

## Exact-head test expectations

- `Apollo R100 real disposable WordPress + source custody browser acceptance`: the 70 inherited HTTP combinations, role/capability security, photo/source rights, keyboard and print PDF, and the **new eight interactive cases** must all pass. Four new browser screenshots appear only on accepted runs.
- `Apollo R78 / genuine Assembler`: the R77 performance gate remains mandatory. Its new diagnostic JSON is meaningful **even on a failed run**, and is deliberately not a passing release receipt.
- Source syntax tests: `python -m py_compile experience2/evidence-atlas/tests/browser_actual_wordpress_r100.py experience2/evidence-atlas/tests/wp_reusable_r77.py`.

## Earlier known blocker

R101's exact-head authentic Assembler/Playground workflow run 41726838317 failed after three R77 nested-pattern cases with `R77_LCP_LAB_GATE` at 1440px and JavaScript enabled. That result is unresolved; R102 adds measurement evidence without weakening the test or claiming the failure was transient. The R100 real WordPress-core environment passed on R101, but does **not** prove actual hosted WordPress.com/Assembler parity.

## Release controls

- Photo-specific NASA rights clearance: 0/6. Do **not** embed photos; the proposed S67-19766 crew portrait identification is provisional.
- No invented map pins or historical edges; retain verified exact NASA identities.
- No hosted WordPress.com claim until separately authorized/tested. No production writes, plugin activation, or site configuration changes.
- Manual NVDA/VoiceOver, real phone/tablet accessibility, independent editorial review, field CWV, and founder go/no-go remain outstanding.
- Home PR #49 and lead's branches are out of scope. Original Research Desk PR #158 remains untouched.
