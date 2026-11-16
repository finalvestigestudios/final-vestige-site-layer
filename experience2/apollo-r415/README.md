# Apollo Experience 2.0 — R415 integrated source-to-investigation journey

**BUILT + OFFLINE FIXTURE TESTED; NOT INSTALLED, NOT LIVE. Production HARD HOLD.**

An isolated, opt-in WordPress staging shortcode `[fv_ex2_apollo_journey_r415]` composes a three-stage NASA-cited chronology with the **unchanged** R414 archive gallery and six-record R411 source catalog. It is a first-party source navigation experience, not a geographical map; no invented coordinates, 3D visualizations, media embeds, NASA logo/photographs, analytics, forms, affiliates, purchases or misleading NASA endorsement. The only next-action link to the existing free Apollo investigation is inherited from R414 (exactly one CTA per instance). The original R414 gallery and R411 source catalog remain byte-identical.

## Provenance / custody

- Original source contract: [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158).
- Source catalog and six limitations: R411 `staging-source-drawer.php`, Git blob `efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1`.
- Gallery implementation: R414 `staging-archive-gallery.php`, Git blob `41540268014b4a792b2e52685ebe8c471a35c3da`.
- Gallery CSS: R414 `assets/archive-gallery.css`, blob `a5eeb96aeebe5569db4cef0d3d0a0e05fdf99c5f`.
- Sources for chronology: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (January 27, 1967), [NASA flammability tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) (102 *later* Command Module ignitions, Dec 1967–Feb 1968), [NASA 1968 mixed-atmosphere decision](https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/) (announced March 14, 1968).
- [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/) and [advertising rules](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): NASA endorsement cannot be implied. Commercial rights clearance and any product naming must be handled separately. No assets reproduced.

The base R411 catalog links to specific NASA image-detail *record pages*, **not to images hosted by FV**. That distinction is maintained. The exact SHA-1 Git blob identity of all three inherited files and new CSS is required at runtime. WordPress rendering requires both `FV_R415_ENABLED=true`, `FV_R415_STAGING_PAGE_ID`, singular matching ID and `wp_get_environment_type()='staging'`. Failure produces a plain accessible link to the free investigation. Dependencies are included only after identity checks. No homepage or existing plugin source is edited.

## QA

Run from repository root after installing PHPUnit? Not needed: CLI `php experience2/apollo-r415/qa/test_php.php` and `python experience2/apollo-r415/qa/test_browser.py` using Playwright and existing local Chromium. Fixture composes genuine PHP markup from unchanged R411 + R414, **not** installed WordPress or NASA live rendering. The bundled `qa/render_fixture.php` is test-only and never deployed. `python experience2/apollo-r415/qa/package_evidence.py` generates a deterministic ZIP with QA manifest and screenshots.

Tests assert default-off fallback, source hashes, malicious URL rejection, six source headings and limitations, chronological attribution, 1 paid-CTA-free route per instance, instance ID isolation, 320–1920px layouts, no JS keyboard disclosure, touch/reduced-motion, 4x root font, forced colors, and linked fragments. The two-instance fixture proves no collision (each instance retains its own single CTA). No navigated HTTP measurements can be claimed from `set_content`: actual LCP/CLS, axe-core, WCAG 2.2 audit, WordPress/Assembler installation, source/media QD and real traffic/checkout acceptance remain blocked by staging/host access and founder approval. A fixture result must never be called a production CWV pass.

## Conversion hierarchy: OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

1. **Unverified original Apollo classroom dossier** → paid purchase: merchant SKU, clearance, pricing, checkout and fulfillment have not been evidenced. **Change:** no commercial CTA; seek founder/Claude product verification and buyer interview approval. **Evidence:** HOLD, no transactions claimed. **Owner:** Founder + Claude commerce.
2. **Verified Grok-approved long-form asset** → qualified-human visit: actual post, immutable asset ID, permitted link placement, approved UTM and human-session events unavailable. **Change:** keep campaign link as an integration spec, no fake URLs/attribution. **Evidence:** HOLD. **Owner:** Grok (creation/publishing), Praxxis (independent review), Claude (events).
3. **Apollo evidence navigation** → existing free Apollo investigation → separately approved educator purchase: source-linked chronology + original six NASA record gallery + single free CTA per component. **Change:** integrate only on staging page by founder approval, retain editorial separation. **Evidence:** local PHP/Chromium PASS subject to outcomes, live HOLD. **Owner:** Apollo QA / independent QD.
4. **Paid order** → net revenue: settlement, refunds/fees, first-party attribution, 7/30-day qualified-human session cohorts unavailable. **Change:** verify at merchant/analytics source before revenue KPI. **Evidence:** not computable. **Owner:** Claude + Commerce.

**KPI:** realized net revenue per 1,000 *qualified* sessions. No source-grounded numerator or denominator yet. Don't equate clicks, leads or social views with purchases.

Coordination: [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); [conversion Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Grok owns creator production, Praxxis external creator QA through TASK-008, Claude owns analytics/checkout engineering, founder retains spending, posting and release decisions. PR #49 and the homepage lead are frozen and **untouched**.
