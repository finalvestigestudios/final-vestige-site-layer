# Apollo Experience 2.0 R268 — CDP Accessibility / Conversion-Custody Gate

**DRAFT / HARD HOLD.** Issue #150; revenue coordination #820; business charter #818. Isolated test-only follow-up stacked on Apollo R267 PR #1936 (parent HEAD f2543d6d439023b47881bd39a97472281cfb2c14). No homepage PR #49 or Research Desk PR #158 edits. This PR does not alter HTML, NASA materials, WP plugins, commercial CTAs, campaigns, analytics, commerce accounts or live pages.

## What actually runs

The executable qa/committed_ax_smoke.py runs the original R224 source-sealed PHP through the actual R263 PHP hook-sequence *simulation*, validates the original manifest (SHA256 f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68), loads the R262 accessibility overlay and the R266/R267 **CLI-only** after-article review fixture, then tests 320/390/768/1440/1920 CSS-pixel Chromium viewports with JavaScript enabled/disabled (10 contexts). It queries Chromium's actual CDP Accessibility.getFullAXTree and rejects anonymous link/button/textbox nodes; also checks one free investigation destination, one *unreleased* disclosed Mini Museum-guide destination, 55 NASA hyperlinks, 31 fragment references, browser keyboard source disclosure, 400% root-text stress, no horizontal overflow, no incidental network requests, and print exclusion of the commercial preview. qa/conversion-hold.json pins the lack of commercial/creator/release approvals.

Run from repo root with the **separately distributed** original sealed fixture and local PHP, Python Playwright and Chromium:

    python experience2/apollo-r268/qa/committed_ax_smoke.py fixture/sealed-r238 experience2/apollo-r262 experience2/apollo-r266 experience2/apollo-r267 experience2/apollo-r263/qa/wp-real-source-sequence.php

An additional R268 extended acceptance runner in the QA archive exercises 20 Chromium contexts (five widths × JS on/off × reduced-motion on/off), keyboard, touch, 400% text stress, native disclosures, ARIA ID references, source and merchant link custody, five *deliberately unsafe* mutations, six reproducible screenshots, and local PerformanceObserver LCP/CLS entries. The extended script is **not** committed; its outputs are supplemental and must not be described as source-controlled execution. Timing observations are raw and non-deterministic; acceptance receipts and screenshot hashes are stable across two executions. Local LCP timing and CLS are **not field Web Vitals**.

## Historical and commercial constraints

NASA's original Apollo 204 Review Board finding states that electrical arcing was the most probable initiator but no single ignition source was conclusively identified: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA prohibits implied commercial endorsement; image and astronaut likeness uses have distinct restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No NASA imagery, reconstructed explosion, or invented map pins are added here.

Flagship hypothesis: a **verified** Grok Apollo long-form video → NASA Evidence Atlas → the original free investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → a **separate, optional** disclosed https://finalvestige.com/mini-museum-history-collectibles/ guide → independently confirmed payable affiliate order. These links are from the original HTML and an unpublished review fixture, not verified public funnel HTTP. No item is an Apollo artifact or NASA-endorsed. Apollo long-form asset_id, actual clickable placement, merchant eligibility/commission settlement, consent-safe attribution and founder approval **unverified**. Grok owns creation/distribution; Praxxis reviews creator output; Claude owns production/analytics; founder owns spending and production approval. TASK-008 remains unchanged.

**Conversion objective:** net revenue per 1,000 qualified human sessions, 7/30-day cohorts, with source asset_id/UTM → qualified session → landing → valid CTA → authenticated paid order/affiliate settlement − fees/refunds. Actual KPI currently **NOT COMPUTABLE**, not zero. Do not equate clicks, reported visits or leads with purchases.

## Non-negotiable gates

Browser navigation to localhost, file and data origins returned ERR_BLOCKED_BY_ADMINISTRATOR. Tests use Playwright set_content, not installed WordPress or real HTTP/CSP. Real axe-core could not be obtained due missing provenance-verified bundle and offline npm/CDN; CDP AX-tree checks are **NOT axe-core certification**. Independent screen-reader review, browser-interface zoom, installed WP/Assembler, HTTP/CSP, real field CWV/INP, affiliate authorization, media rights, independent QD, exact-HEAD hosted CI and explicit founder release approval remain **HARD HOLD**. Never merge, deploy or activate based on this test alone.
