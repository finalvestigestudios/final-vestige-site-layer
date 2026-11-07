# Apollo Experience 2.0 — R183 native Evidence Atlas (unpublished)

**Status: SOURCE-CONTROLLED LAB PROTOTYPE; NOT WORDPRESS STAGING OR PRODUCTION.** Issue #150, conversion governance #820, charter #818. Additive branch stacked on R182 PR #1355 at `eb94515e2cba63cdf41c5b9a527fc0edeb31b01d`. Frozen homepage PR #49 and original Research Desk PR #158 are not edited.

## What is actually built

A fully readable, script-free Apollo 1 mini-Atlas is deterministically reconstructed by `reconstruct_atlas.py`: 4 dated ChronologyRail landmarks, 4 evidence plates with primary written NASA Review Board links, 4 native HTML `details` SourceDrawer gallery entries with NASA archive links and media-use HOLD, 1 contextual **Read original investigation** CTA. Includes skip link, semantic headings/landmarks, touch and keyboard-accessible native drawers, forced-colors fallback, reduced-motion and responsive CSS; all content available without JS. This is *not* a speculative map and has no geospatial pins, tracking, injected analytics, advertising or third-party media embeds.

The source distribution uses a verified, compressed UTF-8 HTML snapshot to avoid alterations in content handoff. Run `python experience2/apollo-r183/reconstruct_atlas.py --output /tmp/apollo-r183.html` to produce the full reviewable **13,750-byte plain HTML source**. Expected output SHA-256: `dd09aaeefa1326d2c1ab42d7084a6525a048c167e7de8e013f53c930486b2b27`. The built output is normal readable HTML, not a proprietary runtime, and no network is needed. Future iteration should commit editable HTML directly when repository transport permits. Note that compression is a transport accommodation, not approval for live embedding.

## Provenance and rights (research only)

- Apollo 1 mission and three astronauts: https://www.nasa.gov/mission/apollo-1/
- Apollo 204 Review Board (1967): https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . Primary authority for 100% oxygen at 16.7 psia, cabin rupture around 23:31:19 GMT at least 29 psia, inward hatch/egress barrier and **no conclusively identified ignition source**. These are report findings, not interpretations from photos.
- NASA image S66-58038 (Oct. 18, 1966): https://www.nasa.gov/image-detail/amf-s66-58038/ — pre-fire training.
- NASA S67-15717 (1967 processing): https://www.nasa.gov/image-detail/amf-s67-15717/ . Jan. 3 processing reference separately derived from https://www.nasa.gov/humans-in-space/55-years-ago-final-preparations-for-the-planned-launch-of-apollo-1/ ; **do not assert photo taken Jan. 3**.
- NASA S67-21294 (Jan. 28, 1967): https://www.nasa.gov/image-detail/amf-s67-21294/ — aftermath photo; **not proof of an ignition source**.
- NASA 2017 hatch exhibition: https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ — retrospective exhibit, not a 1967 accident photo.
- Separate Research Desk **S67-19766** match remains unverified against its linked NASA page; this Atlas avoids certifying it.

**Media rights remain NOT CLEARED for commercial promotion.** The gallery includes text descriptions and direct NASA links only, not copied or embedded NASA image bytes. NASA attribution is not NASA endorsement or a paid-media license. The Apollo educator dossier is a hypothesized future product, **not a verified FV SKU**.

## Reproduction and evidence boundaries

1. Run reconstruction; verify SHA-256 above. `python -m unittest discover -s experience2/apollo-r183/qa -p 'test_*.py'` for static custody and negative-control tests (requires BeautifulSoup).
2. Local full Playwright/Chromium acceptance harness is packaged with the R183 evidence ZIP: six widths 320,360,390,768,1440,1920, 320 no-JS, 390 touch, 390 forced-colors, keyboard drawer controls, Chrome AX tree, checks against unexpected network and errors, layout overflow, LCP/CLS lab observers, reproducible full-page screenshots. The offline harness uses `page.set_content`; local file:// navigation was blocked in this execution environment.
3. Fixture verdict can never clear release. Genuine axe-core (not installed), manual screen readers, installed WP/Assembler/Gutenberg/shortcode lifecycle, actual image delivery and licensing, CSP/caching, exact-head CI and real-page p75 CWV are all outstanding.
4. Never merge, install, publish, collect data, deploy, change WP content/settings, activate commerce, or claim paid conversions without founder approval and independent QD.

## Conversion-first handoff / ONE next action

**OFFER:** original source-grounded Apollo educator investigation kit (HYPOTHESIS; no currently verified paid offer) → **FUNNEL STEP:** Grok long-form/Shorts asset with immutable asset ID and compliant UTM → Evidence Atlas → free Apollo investigation → **BLOCKER:** no verified saleable Apollo SKU, checkout/rights/merchant confirmation or Grok Apollo published asset → **EXPERIMENT:** evidence-first bridge and contextual reading CTA, never unrelated Mini Museum commerce in a tragedy case → **EVIDENCE:** source-coded offline prototype with browser fixture only → **OWNER:** Apollo QA; Grok and Praxxis own creator research; Claude/Commerce owns production tracking/storefront; founder releases.

No Apollo orders, paid attribution, confirmed leads or net revenue observed. Do not compute net revenue per 1,000 qualified human sessions without verified qualified sessions, paid transactions, fees and refunds. See #820 and TASK-008 for approved measurement contract.
