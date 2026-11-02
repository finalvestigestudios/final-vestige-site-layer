# Shelter, Power and Family Communication: QA record (2026-11-01)

What was run, with exact commands and results, and what was **not** run. These are standalone browser tests of the built preview pages. They do **not** show how the pages behave inside a WordPress theme or the Assembler; that needs its own test before anything is published.

## Commands and results

Run from the repository root.

| Command | Result |
|---|---|
| `python -I preparedness/tools/validate.py` | 0 errors, 0 warnings |
| `python -I preparedness/tools/build.py` | succeeded |
| `python -I preparedness/tools/gen_shelter_tools.py --check` | generated tool pages are current (also run by a unit test) |
| `node preparedness/tests/test_shelter_tools.js` | all assertions passed |
| `python -I -m unittest discover -s preparedness/tests -v` | 64 tests; 63 ran and passed, 1 skipped (the axe-core test, because no axe bundle path is set) |
| `PA_AXE_JS=<path to axe.min.js> python -I -m unittest discover -s preparedness/tests -v` | 64 tests, all passed, 0 skipped |

Test files added: `tests/test_shelter_tools.js` (logic), `tests/test_shelter_tools.py` (static, privacy and security: 11 tests), `tests/test_shelter_tools_browser.py` (real browser: 17 tests). No existing test was changed or weakened.

## Environment

Windows 11; Python 3.13; Node 24.11; Playwright for Python 1.64.0 driving the installed Microsoft Edge (Chromium 156.0.4314.50), headless. Preview pages were loaded from `file://` after `build.py` (the `build/` directory is git-ignored).

## axe-core

axe-core 4.10.2, installed from the npm registry with `npm pack`. The tarball's SHA-512 (`RE3mdQ7P3FRSe7eqCWoeQ/Z9QXrtniSjp1wUjt5nRC3WIpz5rSCve6o3fsZ2aCpJtrZjSZgjwXAoTO5k4tEI0w==`) and SHA-1 (`85228e3e1d8b8532a27659b332e39b7fa0e022df`) match the values the registry reports for that version (`npm view axe-core@4.10.2 dist.integrity dist.shasum`). That checks the download against the registry, not the registry against the publisher.

Rules: tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`, `best-practice`. Run against all three tools at 390 and 1440 px (results in `docs/qa/axe-*.json`, each `[]`), and against the four articles at 390 and 1440 px inside the browser test. **Result: no violations.** An earlier run found one heading-order violation (card preview headings), which was fixed. axe finds only some accessibility problems; it is not a substitute for testing with assistive technology.

## What the browser tests check

* **Network and errors:** every request on each tool page is `file:`, `data:` or `blob:`; no console errors or page errors.
* **Widths:** no horizontal overflow at 320, 360, 390, 428, 768, 1024, 1440 and 1920 px for the three tools and four articles; 400 percent zoom is simulated with a 320 x 256 viewport.
* **Controls:** every field and button has an accessible name; form controls are at least 44 px tall (checkbox rows counted by their label); a visible focus ring of at least 2 px on every focusable control reached by Tab.
* **Input handling:** `<img onerror>` and `<script>` strings typed into fields never execute and never become elements; they appear as text in the page and the text export.
* **Storage:** after typing, `localStorage`, `sessionStorage` and cookies stay empty.
* **Reduced motion:** with `prefers-reduced-motion: reduce`, buttons and links have no transition.
* **Behavior:** fire worksheet checks, date reminders, adding and clearing rows, text download; outage planner adapts to answers, exports checked items, contains no generator sizing or discard-medication wording; card minimal version omits school, caregiver and access details, address-like text is flagged, copies per sheet.
* **No JavaScript:** with scripting disabled the worksheet form, the full outage checklist (every item as a checkbox, each with its "If: ..." condition) and a blank fold-over card are present and visible; scripted-only buttons stay hidden.
* **Printing:** print media is emulated; only the printable sheet prints (header, table of contents and the rest of the article are hidden). The card prints on one Letter page for four cards; the worksheet prints on 5 pages; the planner on 3 (see `docs/qa/*-print.pdf`). The fold-over card measures 7 x 2.125 in, text is at least 7.5 pt, and worst-case field contents (maximum lengths of the widest characters) do not overflow any card face.

## Evidence files in `docs/qa/`

`v-fw-1440.png`, `v-op-1024.png`, `v-rc-390.png` (viewport screenshots), `fig-decision.png`, `fig-floor.png` (the two original diagrams at phone width), `home-fire-escape-worksheet-print.pdf`, `power-outage-planner-print.pdf`, `reunification-card-print.pdf` (Chromium print-to-PDF), and `axe-*.json`.

## Not run, or not established

* WordPress, the Assembler or any theme: not tested. `:has()`-based print scoping and container queries need a check in the theme.
* Firefox, Safari/WebKit, and mobile browsers: not run. Only Chromium (Edge) was used.
* Real assistive technology (NVDA, JAWS, VoiceOver, TalkBack): not run. Screen-reader semantics were checked only by accessible names, roles and axe.
* Physical touch devices, paper printers, and a human reading the printed 7.5 pt card: not tested.
* Layout stability (cumulative layout shift): not measured.
* Color contrast: covered by axe and the repository's token contrast test, not by manual review of every state or Windows high-contrast mode.
* The FCC, NFPA, USDA and Red Cross pages listed in `SHELTER-SOURCE-LEDGER.md` as unread.
* No human has verified any source link (`human_link_check` is false for all 45).
