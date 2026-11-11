# Apollo Experience 2.0 — R283 native chronology-focus custody (STAGING / HARD HOLD)

**Scope:** Independent Apollo EvidencePlate/SourceDrawer/ChronologyRail staging, stacked on R282 draft PR #2030. Do not modify PR #49 (homepage), PR #158 (Research Desk), production WordPress, Grok's creator queue, or Claude's analytics.

## Reproduced defect and fix
In actual Chromium, pressing Enter on an R282 chronology link updated the hash but dropped focus to `<body>` because the destination `<li id=…>` could not accept programmatic focus. R283 adds `tabindex="-1"` to each EvidencePlate target, without adding ordinary Tab stops, and a scoped visible focus outline plus forced-colors correction. Native fragment navigation now transfers focus to the evidence plate even without JavaScript. Historical source text, pinned R282 content SHA-256, NASA destinations, source relationships, pending review labels, and the one free-investigation CTA are unchanged. No maps, unreviewed images, merchant links, tracking or JS added.

## Source-controlled executable gate
```sh
php -l experience2/apollo-r281/apollo-source-experience.php
python3 experience2/apollo-r281/qa/committed_gate.py /tmp/fv-apollo-r283
```
The updated gate renders actual PHP (two instances) and runs actual Chromium via Playwright at 320/390/768/1440/1920px × JS on/off. It verifies 60 native Enter-to-target focus transfers, rejects the deliberate R282 missing-`tabindex` control, checks focus outline, absence of extra ordinary Tab stops, 200%/400% root-text stress without horizontal overflow, native SourceDrawer keyboard open/close, reduced-motion, touch emulation, forced colors, printed NASA URLs, unique IDs, all source links and the one free investigation next action per component. No unexpected requests or JS errors. Two local executions produced matching receipt and screenshot SHA-256 values. Reproducible ZIP and original Chromium performance-observation JSON are supplied separately.

**Measurement limits:** Genuine axe-core could not run (dependency registry/network inaccessible); independent screen reader, installed WordPress/Assembler, browser HTTP/CSP, browser-interface zoom, navigated LCP/CLS, field p75 CWV and hosted CI remain untested. Where local `PerformanceObserver` produces LCP/layout-shift entries under `about:blank` + `set_content`, they are laboratory diagnostics, not field CWV or a conversion claim.

## Historical source and rights boundary
[1967 Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) says an electrical arc was the **most probable initiator**, while no single ignition source was conclusively identified. NASA [mission history](https://www.nasa.gov/mission/apollo-1/) and [safety summary](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) discuss the same event, not three independent witnesses. Editorial review remains pending. [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) do not grant promotion/endorsement or imagery rights. No photos, marks, astronaut likenesses or speculative geo pins are used.

## Conversion hypothesis and owner gates
Verified **already published** Grok Apollo long-form asset (Grok posts, Praxxis verifies TASK-008) → correctly tagged mobile landing in Apollo Atlas → NASA evidence inspection → **single nonintrusive free Apollo investigation CTA** → optional, separately disclosed relevant Mini Museum guide **only after** merchant acceptance/rights/fit approval → authenticated paid merchant order → refunds/fees → realized net revenue. Claude owns production analytics/commerce, founder owns release approvals. Missing: authenticated Apollo asset_id/UTM destination, Mini Museum payable eligibility, confirmed orders, qualified sessions and refunds/fees. **Net revenue per 1,000 qualified human sessions is NOT COMPUTABLE.** No affiliate activation or sale claim. 7/30-day cohort and tiny-sample review required.

## Final release gate
**HARD HOLD**: independent editorial/rights review, genuine axe and screen-reader QA, installed WordPress, HTTP/CSP, real browser zoom and field CWV, exact-head CI/QD, verified creator and merchant data, founder approval. No merger, release, CMS/settings write, social post, email, analytics, merchant activation or spending authorized.
