# Apollo Documentary Trails — isolated staging QA (2026-10-30)

**Release: HOLD.** This is a new, additive, source-first component stacked on Apollo after-action PR #209 (which itself stacks on PR #202). It does **not** alter frozen homepage PR #49, homepage lead branches, original Research Desk shortcode PR #158, or WordPress.

## What the visitor gains

A documentary reading path for **each of six actual Apollo 204 Board recommendation/NASA response pairs**: the 1967 Board's recommendation, what the 1968 NASA response report said, and the remaining unproven step. This is an original visually linked three-stage reading rail, not a claim of hardware certification or a fabricated documentary timeline. It draws from the existing, versioned six-row `response-crosswalk.json` and six-item `custody.json`; source-custody deep links are labeled as **thematic** and never misrepresented as direct photographic proof.

Links point directly to NASA's original Apollo 204 Review Board report and 1968 Senate-report excerpt hosted by NASA. NASA image bytes, logos, new external fonts, libraries, analytics, map pins and location edges = **zero**.

## Actually executed, separate local fixture

- `python render.py`: static full-page generated HTML with new `trail.py`, `assets/trail.css` and `assets/trail.js`.
- `python qa/trail_contract.py`: **PASS** canonical six linked source rows, both NASA URLs, explicit evidence limits, no invented imagery or geography, fail-open CSS, deterministic rebuild.
- `python qa/trail_browser.py`: **PASS** real Chromium/Playwright at **320, 360, 390, 768, 1024, 1440 and 1920** px. Six cards and original citation anchors; search/selector + reset; deep-link restoration and keyboard focus; native summary; 390px no-JS reading; 320px reduced-motion; forced bad selector fail-open; zero root horizontal overflow and no page errors in tested states. Screenshots: `qa/screenshots/trail-390.png` and `trail-1440.png`.
- `python qa/trail_a11y_perf.py`: **PASS** actual Chrome Accessibility Tree smoke at 320/390/768/1440/1920. At each width: 127 named interactive nodes checked, none lacking accessible name; selector geometry 48px high. Local Chromium synthetic LCP: 348/160/168/208/188ms respectively; CLS=0 in the in-memory fixture. These are **NOT** production p75 CWV numbers, nor do they include WordPress/Assembler, fonts, third-party images, actual HTTP transport or user interactions at scale.
- `axe-core` **NOT RUN**: verified axe-core JS bundle was not installed locally. CDP name/role checks do **not** replace axe or manual WCAG 2.2 AA audit.

## Integration contract and release gates

The Python renderer imports `trail.section`, inserts the new component after `response_html`, and concatenates scoped trail CSS+JS into the offline fixture. Canonical `response-crosswalk.json` and `custody.json` remain unchanged. The page's Source Gallery and Atlas section labels advance VI→VII and VII→VIII. No CMS changes.

The local fixture uses **pre-existing** local response-lab/crosswalk files whose bytes were not identical to the streamlined GitHub PR #209; all new component files and the renderer patch must be re-read from the exact GitHub head and re-tested there, preferably with identical source manifests. Pending actual WordPress staging, CSP/theme/caching/shortcode lifecycle, download routing for existing CSV/JSON links, Safari/iOS, NVDA/VoiceOver, valid pinned axe, current NASA media rights (no images used), independent QD and green hosted CI. No release without founder approval.

NASA primary sources: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/. Policy: https://www.nasa.gov/nasa-brand-center/images-and-media/.
