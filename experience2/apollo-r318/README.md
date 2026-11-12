# Apollo R318 — independent staging release-readiness gate

**Built/tested offline; not live, deployed or approved for release.** Child of [R317 draft PR #2242](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2242). Engineering [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); commercial source of truth [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Homepage PR #49 and separate Research Desk PR #158 remain untouched.

## Why
R281–R317 accumulated browser interactions without a consolidated independent release-readiness baseline. R318 adds source-controlled cross-mode QA and an extended screenshot/contrast evidence archive. Offline Chromium does NOT prove WordPress, CDN, NASA delivery, production performance, real commercial conversion or WCAG conformance. No staging component source, historical claim, merchant, social post or live tracking changes.

## Reproduce
Run: python experience2/apollo-r318/qa/source_controlled_gate.py

Prerequisites: PHP, Node, Python Playwright and BeautifulSoup, Chromium at /usr/bin/chromium. The test checks exact reviewed R317 Git blobs for PHP and campaign JS, PHP/JS syntax, cache-invariant rendering across visitor query strings, dual-instance ID integrity, three documentary plus four contextual NASA media records per instance, official NASA link destinations, one existing editorial CTA per instance, and no invented geo pins or loaded images.

Offline Chromium runs seven widths (320, 360, 390, 768, 1024, 1440, 1920) by four modes (JS, no-JS, no-CSS, forced colors), with reduced-motion/touch configurations, keyboard context menu, native source routing, keyboard focus, touch disclosures, printed source custody and an R316 negative control. Extended browser QA in the independently distributed evidence archive samples computed text-color contrasts at four widths, captures six screenshots and writes a JSON receipt.

## Evidence — November 12, 2026
- Source-controlled Playwright gate 28/28 contexts PASS; R316 negative control and print source custody PASS.
- Extended QA 28/28 contexts PASS. All 73 sampled computed text contrasts passed at each of 320/390/1440/1920px; sampled minimum ~9.16:1. This heuristic does NOT replace genuine axe-core or full WCAG review.
- Offline fixture PerformanceObserver LCP 48–108ms in the source-controlled test, CLS zero across seven widths, and no network resources fetched. These are not production p75 Core Web Vitals.
- No network beacon, lead event, checkout, affiliate acceptance or purchase. No commercial CTA added.

## HARD HOLD — unverified release gates
1. Genuine axe-core not run: npm registry DNS resolution failed in this environment. NVDA/VoiceOver manual acceptance remains outstanding.
2. Installed WordPress/Assembler, real shortcode enqueue, CSS/JS delivery, Jetpack, CDN and CSP have not been tested. Native Chromium HTTP(S) is blocked by ERR_BLOCKED_BY_ADMINISTRATOR.
3. Production p75 LCP/CLS/INP and physical mobile devices are unverified.
4. Grok/Praxxis published Apollo asset ID, approval for link placement and real destination are unverified.
5. There is no verified rights-cleared, payable Apollo-relevant product/affiliate commission or authenticated Payhip order, fee and refund reconciliation. NASA source links do not license commercial use or imply endorsement.
6. Founder, independent QD and official editorial/media rights reviews remain outstanding. No merge, deployment, publishing, sending or spending is approved.

**Hypothesized path only:** approved Grok Apollo long-form film → original NASA Board evidence in Atlas → one free investigation CTA → separately approved relevant paid product. Net realized revenue per 1,000 qualified human sessions is NOT COMPUTABLE from these staging tests.

NASA Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (probable electrical initiator, no conclusive exact ignition source). NASA advertising rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/.
