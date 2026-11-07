# Apollo Experience 2.0 — R197 native evidence navigation (DRAFT / STAGING HOLD)

Parent R196 PR #1458 at commit 68c48f9cb9be83101c8e665eb055801ffcebd050. Scoped to experience2/apollo-r197/. Does not modify frozen homepage PR #49, independent Research Desk PR #158, WordPress content/settings, or any production code.

## Change and source contract

This source-controlled builder regenerates the four existing Apollo findings with a named, native HTML navigation panel inside the Research Desk source guide, and adds tabindex="-1" to the three previously non-focusable findings. Native fragment links move keyboard focus to the correct finding and visually mark the :target element, without requiring JavaScript. The existing eight NASA source disclosures, four chronological events, text-only gallery, integrity-pinned PHP/CSS/optional JS, print source appendix and the single free "Read original investigation" CTA remain intact. No invented map pins, unverified scientific claims, commercial links, external assets, tracking, email or social posts were added.

Sources: NASA Apollo 204 Review Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; NASA photograph S67-21294 https://www.nasa.gov/image-detail/amf-s67-21294/ ; NASA advertising restrictions https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . The exact ignition source was not conclusively identified. NASA media are cited, not sublicensed; astronaut likeness and NASA endorsement permissions are not established.

## Rebuild and local acceptance

With stacked parent files checked out, run from repository root:

    python3 experience2/apollo-r197/build_r197.py
    php -l experience2/apollo-r197/dist/fv-ex2-apollo-r197.php
    python3 experience2/apollo-r197/qa/gate_r197.py /tmp/apollo-r197-evidence

Prerequisites: PHP, Python 3 + Playwright, /usr/bin/chromium. No paid services. Builder verifies parent file digests, creates deterministic derived artifacts and a file-hash manifest, without touching WordPress.

QA uses actual shortcode PHP output in a constrained WordPress-function shim; tests normal/printed/late fallback; validates four target links in a genuine Chromium CDP accessibility tree; tests 48 keyboard/touch claim journeys across 12 browser contexts: 320, 360, 390, 768, 1440, 1920, no JS, reduced motion, forced colors, touch, and 200% CSS zoom simulation at 320 and 390. Also checks disclosure controls, single free CTA, no horizontal overflow, buffered Chromium LCP and CLS. Each run yields 12 screenshots and a JSON receipt. Compare screenshots, not variable timing fields, for deterministic visuals.

**Limits:** page.set_content fixture only; external, data and localhost browser navigation blocked. WordPress-function shim is NOT installed WordPress. No real axe-core, NVDA/VoiceOver, true browser zoom, staging CDN/CSP/theme, exact-head CI or independent QA. Fixture LCP/CLS are not production Core Web Vitals.

## Conversion: one editorial trust bridge

Proposed offer: Apollo classroom research dossier, NOT a verified saleable SKU. Mini Museum may be evaluated later as an adjacent collectible affiliate offer only after offer eligibility, editorial fit, compliant disclosure, merchant checkout and founder approval. No affiliate commerce in the factual chronology.

Proposed funnel: Grok-published Apollo long-form with verified asset_id -> Atlas sources/chronology -> free original-investigation CTA -> approved product or confirmed lead -> independently merchant-confirmed purchase/paid affiliate conversion -> refunds and fees -> realized net revenue per 1,000 qualified human sessions in 7/30-day cohorts. Grok owns production and distribution; Praxxis independently reviews creator assets; Claude owns production checkout and analytics. Published Apollo asset, confirmed lead, orders, revenue and qualified-human denominator remain UNVERIFIED.

**STAGING HOLD:** installed WordPress/Gutenberg, real link navigation, CSS/CSP/cache isolation, genuine axe-core, screen readers, actual zoom, real performance, exact-head CI, independent QA, merchant rights/checkout and founder release approval are outstanding. Do not install, merge, deploy, publish, spend or send.
