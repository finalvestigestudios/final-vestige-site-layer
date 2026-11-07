# Apollo Experience 2.0 — R194 source-boundary experiment (DRAFT / HOLD)

**Owner:** isolated Apollo Evidence Atlas lane under Issue #150. **Parent:** R193 draft PR #1433, SHA `cb9dbcc8ffa1fbaf9f57f8a1a37a770361570d12`. **Cross-reference:** commercial attribution #820 / charter #818. Do not modify frozen homepage PR #49 or original Research Desk PR #158.

R194 adds **one short source-verification note directly before the single free-original-investigation CTA**. It cites NASA's Apollo 204 Review Board as the technical source and cautions that NASA gallery photographs cannot establish ignition or confer commercial advertising rights. The free CTA destination is unchanged. This is a conversion hypothesis about increased trust/qualified click-through, **not** a reported or measurable revenue result. No new offer, signup, affiliate link, media, cookies, pixels, map pins, geo edges or analytics are introduced. No source statements, photo destinations or chronology dates are altered.

## Deterministic workflow

From repository root with the R193 parent ancestry checked out:

```bash
python3 experience2/apollo-r194/build_r194.py
php -l experience2/apollo-r194/dist/fv-ex2-apollo-r194.php
python3 experience2/apollo-r194/qa/gate_r194.py experience2/apollo-r194/evidence-A
python3 experience2/apollo-r194/qa/gate_r194.py experience2/apollo-r194/evidence-B
python3 experience2/apollo-r194/qa/vitals_r194.py experience2/apollo-r194/evidence-A
```

The builder verifies the pinned R193 ancestor manifest and every parent asset SHA-256, then emits a new, separately namespaced, pinned staging PHP shortcode, HTML, scoped CSS, unchanged optional campaign JS and manifest. `gate_r194.py` runs PHP through a **WordPress function shim, not an installed WordPress instance**; exercises missing/tampered optional JS, modified core HTML and late-render fallback; then tests the generated component with real Playwright/Chromium at 320, 360, 390, 768, 1440, 1920px plus 390 no-JS, reduced-motion, forced-colors and touch. It verifies exactly one free CTA, NASA-source note and destination, eight native details, print source appendix, keyboard/pointer controls, no page errors, no overflow and captures reproducible screenshots. The vitals tool uses real Chromium buffered PerformanceObserver entries; results describe a local PHP/DOM fixture, **not installed-site LCP/CLS or CrUX**. RunA/RunB screenshot SHA-256 digests must match.

## Rights and editorial custody

Primary technical report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/. NASA advertising guidelines: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/. The Review Board did **not** conclusively establish one ignition source. NASA photographic catalog citations and advertising/likeness permission are separate issues; imagery rights for a paid Apollo product are **NOT CERTIFIED**. No image is embedded in this stage.

## Release and commerce blockers

**STAGING HOLD.** Need (1) exact-head hosted CI and independent reviewer, (2) installed WordPress/Assembler/Gutenberg test with real stylesheet/JS delivery, CDN and CSP, (3) genuine axe-core, actual screen-reader QA and 200% zoom, (4) real-navigation, mobile performance, LCP/CLS and cache isolation, (5) legitimate relevant rights-cleared SKU, merchant checkout/fulfillment and verified refunds/fees, (6) Grok/Praxxis actually published `asset_id` and destination inventory in TASK-008, (7) founder approval before any production change. No live website or WordPress writes, product listing, paid service, outreach, newsletter or social posting authorized by this draft.

**Commercial measurement contract:** unique organic-social Grok `asset_id` / campaign → **qualified-human** visit → free investigation CTA → optional verified lead → independently confirmed merchant order → refunds/fees → realized net revenue per 1,000 qualified human sessions (7/30-day cohorts; small-sample caveats). None of those outcomes is established by a fixture passing.
