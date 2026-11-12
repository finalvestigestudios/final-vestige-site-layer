# Apollo Evidence Studio R311 — cache-stable editorial continuation (STAGING ONLY)

Source-of-truth: Apollo #150, conversion #820, business charter #818. Base: R310 draft PR #2198, not homepage PR #49 or independent Research Desk PR #158.

## Defect, mitigation and proof

R308 placed visitors' campaign labels in the server-rendered editorial continuation URL. A shared WordPress/CDN full-page cache that ignores the URL query could replay A's labels to B. This is a reproducible design risk, **not proof of production misattribution**. R311 disables that feature unconditionally: both healthy and source-integrity-recovery PHP paths always return the immutable free Apollo investigation link. The old helper name is retained for compatibility. A data-fv-attribution-policy attribute describes the cache-stable policy; it is passive, not analytics.

This deliberately sacrifices cross-page UTM continuity pending independently proven first-party attribution and cache segregation. Do not re-enable query-dependent HTML without Claude's cache verification, privacy review, independent browser QA and founder release approval.

Historical claims, original NASA sources, review-board chronology, claim-to-drawer-to-catalogue custody, four link-only contextual NASA media records, visible rights cautions, native disclosures, and the single free investigation CTA are unchanged. Source links do not grant image-reuse rights or prove a precise ignition point. No new imagery, map edges, scripts, cookies, merchant links or products.

## Reproduce from repo root

    python experience2/apollo-r311/qa/source_controlled_gate.py
    python experience2/apollo-r310/qa/source_controlled_gate.py

The R311 gate runs actual local PHP and offline Chromium Playwright at 320, 360, 390, 768, 1440 and 1920 px with JavaScript on/off, disclosure keyboard/source-focus navigation, alternate visitors and a poisoned-body negative control. Full HTML must be byte-identical across campaign queries. R310's gate maintains the documentary source/media list boundary.

**Intentional test deprecation:** the R308 test that requires UTM forwarding will now fail by design, because the risky behavior is OFF. Do not report it as a passing regression.

An expanded QA ZIP documents additional screenshots, fixture-only LCP/CLS and SHA receipt. Browser navigation is administratively blocked in the QA sandbox, so native HTTP/CSP and installed WordPress/CDN behavior are NOT VERIFIED. Genuine axe-core (public package retrieval blocked by DNS), independent screen readers, hosted CI, editor/rights acceptance and production field CWV are NOT VERIFIED.

## One controlled commercial pathway

Audience: source-conscious grades 6–9 teachers and history-documentary viewers. Proposed pathway: a published, authenticated Grok Apollo long-form asset → primary-source Atlas → NASA source proof → free Apollo investigation → separately verified rights-cleared educational dossier. The proposed dossier is **NOT** an authenticated buyable FV SKU; no paid CTA is added. Grok owns content/posting, Praxxis independent creator QA, Claude owns merchant attribution and technical release, Founder owns approvals.

| Offer | Funnel step | Blocker | Change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Apollo teaching dossier hypothesis | free article to paid order | no confirmed payable SKU, rights, checkout | audit existing FV/Payhip inventory first | HOLD; no confirmed sales | Founder / Claude |
| Grok Apollo long-form | asset to qualified landing | actual asset ID and destination unknown | verify TASK-008 handoff; no queue changes | UNVERIFIED | Grok / Praxxis |
| Free investigation | Atlas source to editorial continuation | shared-cache attribution contamination risk | static destination, passive safe-policy label | LOCAL PHP/CHROMIUM PASS, NOT LIVE | Apollo |
| Owned commerce | purchase to realized net revenue | no authenticated sessions, settled orders, fees/refunds | privacy-safe 7/30-day cohort reconciliation | NOT COMPUTABLE | Claude |

Governing KPI: verified realized net revenue per 1,000 qualified human sessions. Editorial click, confirmed lead, checkout start and affiliate outbound are NOT verified paid sales.

## Release: HARD HOLD

No WordPress, social, merchant, email, homepage PR #49, or Research Desk PR #158 writes. No spend. Require exact-SHA hosted CI, actual WP/Assembler and reusable-block tests, genuine axe-core, manual NVDA/VoiceOver, real browser/CSP and CDN checks, production p75 LCP/CLS/INP, NASA rights/editorial review and founder signoff. Roll back R311 by reverting the scoped PHP diff on this branch; never restore unsafe server-UTM forwarding as a production rollback.
