# Apollo Experience 2.0 — R238 keyboard skip-link + source-journey acceptance

**STAGING HOLD.** Isolated draft stacked on R237 PR #1742 at HEAD 58cba03423261568397c8294c96e57c4dc433404. Homepage PR #49 and Research Desk PR #158 untouched. No production edits or publishing.

## Actual-source change

Verified R236 parent manifest SHA-256: f9169870eb3c02415feaf70eed9bbefdca5b194c6ddb27a92a0b80102ef1ce95. Protected NASA HTML SHA-256: 50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6. Every parent file is hash verified before generating the new, separate staging output. The parent is not edited.

The focusable skip-navigation link measured 42.39px tall at 320, 390, 768, 1440 and 1920px in actual baseline Chromium. R238 scoped CSS makes it at least 47.17px (51.17px at 768px forced-colors), preserves hidden-until-focus behavior, visible keyboard outline and reduced motion. No JS, NASA content/URL/image/chronology/geo coordinates, product or CTA change.

The committed r238_focus_accept.py builds a separately pinned staging artifact: append scoped CSS; update PHP full CSS integrity hash and cache version; update manifest and verify it. Do not activate alternative adapter alongside other Apollo adapters.

## Tests and deterministic proof

Two independent runs passed 11 Playwright Chromium contexts each: 320/390/768/1440/1920px JS enabled/disabled plus 256px no-JS. Actual Tab and Enter sequences checked mast navigation, skip-link focus movement to main region, next NASA link, visible focus, native source drawer keyboard/touch, reduced-motion and forced-colors, 44px skip target, no overflow, network calls or added scripts, four NASA source plates and one free investigation CTA. **11/11 screenshots identical between runs.** PHP syntax and simulated normal-render, duplicate-shortcode fallback, CSS corruption rejection passed.

Derived manifest SHA-256: f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68.
QA receipt SHA-256: 65f713ae5224a84e3c12841a3d72fd65ab24c31c68ad0126898b8288c302ae27.
Derived CSS SHA-256: 025ef6721875a41096404c8e2697a7de4a7130aeb3ee337df338c1e54823a478.
Derived PHP SHA-256: 6e8d4b73642417c97300fc5aa3ea4c60827a1e1a771f89fab9fa3ecf8f295262.

Offline fixture PerformanceObserver LCP 80–160ms and observed CLS 0 in ten JS-enabled samples across both executions. NOT production field Core Web Vitals. Variable timing samples are in a separate file to preserve deterministic receipts.

**HARD HOLD:** Genuine axe-core missing, installed WP/Assembler not tested, screen reader not tested, real browser-UI zoom not tested, browser page.goto on localhost/file was ERR_BLOCKED_BY_ADMINISTRATOR, hosted CI and independent QA unavailable, R198 ancestry unresolved, commercial photo/likeness rights and founder authorization unverified. No WCAG or commercial-rights certification claimed.

## Reproduction

Obtain the exact LOCAL_RUN/generated-r236 directory from R237 QA archive. Run with Playwright Chromium/PHP and unused output locations:

    python3 experience2/apollo-r238/qa/r238_focus_accept.py --parent LOCAL_RUN/generated-r236 --patch experience2/apollo-r238/assets/focus-bridge.css --output /tmp/apollo-r238-out --qa /tmp/apollo-r238-qa
    php -l /tmp/apollo-r238-out/fv-ex2-apollo-r224.php
    php experience2/apollo-r238/qa/r238_php_smoke.php /tmp/apollo-r238-out

The browser test uses the complete generated historical HTML/CSS in an offline Chromium fixture, not installed WP HTTP navigation. The R237 release gate continues to protect immutable NASA evidence and disallow invented revenue claims.

## Conversion-focused source-led route

One flagship: Apollo 1 January 27, 1967. NASA Apollo 204 Review Board supports probable electrical-arc initiation but cannot conclusively identify exact ignition. NASA S66-58038, S67-15717 and S67-21294 are photographic records with different dates/roles. Source links are not a license for commercial image reuse. No speculative pins.

One candidate high-intent audience: history/science educators from a potential Grok Apollo long-form video. No actual published Grok Apollo asset_id, social post, date, hook, UTM/mobile destination or attribution verified through TASK-008; Grok retains creator/distribution ownership, Praxxis independent review. **One relevant existing action only:** free original investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . No paid CTA. Potential educator dossier has NO verified rights-cleared SKU/checkout/fulfillment/merchant acceptance or founder approval.

Only after approvals: unique published asset_id and permitted UTM → qualified-human sessions → landing → relevant CTA → confirmed lead where applicable → independently verified paid order or affiliate settlement → refunds/fees → net realized revenue per 1,000 qualified-human sessions, 7/30-day cohorts. Currently NOT COMPUTABLE, not zero. No measurement script added, no social or WordPress changes.

NASA: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Governance: Issues #150, #820, #818.
