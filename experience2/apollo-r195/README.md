# Apollo Experience 2.0 — R195 keyboard focus + 200% zoom reflow (DRAFT / HOLD)

Parent: R194 draft PR #1441 at `051fbc829f3e26994c8b80d7726af88aff2a7abd`. Primary coordination: Issues #150, #820, business charter #818. Independent of homepage PR #49 and Research Desk PR #158.

## Actual defect and repair
In the R194 PHP-rendered Atlas, activating the **Skip to evidence** link by keyboard left focus on `BODY` in Chromium. The seven other on-page navigation/ChronologyRail links targeted headings/records without a programmatically focusable destination. Adding `tabindex="-1"` to their eight *existing* targets transfers focus via the native anchor behavior without adding keyboard Tab stops or JavaScript.

A separate R194 CSS zoom reproduction overflowed horizontally at 320px and 390px viewports with CSS zoom set to 200% (about 499px content width at a 320px viewport). R195 lets the single-column hero grid actually shrink using `minmax(0,1fr)` and permits long heading words to wrap. This is a CSS zoom simulation, not a claim of genuine user-agent zoom certification.

## Rebuild and QA
Run `python experience2/apollo-r195/build_r195.py`, then `python experience2/apollo-r195/qa/gate_r195.py /tmp/apollo-r195-runA`, repeat with runB, and run `python experience2/apollo-r195/qa/vitals_r195.py /tmp/apollo-r195-vitals`. Requires PHP, Python Playwright and local Chromium. All source artifacts are generated on demand with a SHA-256 manifest and parent digest verification. No generated artifacts are submitted as modified existing files.

Local evidence: PHP lint PASS; 12 Chromium contexts per run spanning 320–1920px plus no-JS, keyboard, touch, reduced-motion, forced-colors and CSS zoom-200 tests; 96 native keyboard focus journeys per run and 540 assertions per run; two complete runs; 12/12 screenshot hashes identical. Five offline Chromium PerformanceObserver LCP measurements 120–252 ms, CLS 0. **These are not production CWV or installed WordPress acceptance.** Genuine axe-core and manual screen-reader tests are not completed.

## Source custody and monetization limits
Retains four chronology milestones, four technical findings, eight source disclosures, four NASA-linked archival records, and eight printable source citations. NASA Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (ignition source not conclusively identified). NASA advertising guidelines: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ (no implied endorsement, astronaut-likeness restrictions). No photographs reused, new map pins, unverified claims or commercial permissions inferred.

Only visitor action: **Read original investigation** (free). The proposed educator dossier is not a verified sellable SKU. Conversion measurement, qualified Grok asset identity, confirmed leads, orders and realized net revenue are all **UNVERIFIED/NOT COMPUTABLE**; no affiliate activation or new tracking.

## Release HOLD
Actual WordPress staging, theme/Jetpack/CDN/CSP behavior, public navigation, genuine axe-core, VoiceOver/NVDA, actual browser zoom, hosted CI on exact HEAD, independent QA, rights clearance for any future product, matched checkout and founder approval remain required. Nothing in this PR authorizes a merge, live deployment, WordPress write, creator post, email or spending.
