# Apollo R370 — pre-head WordPress style custody (STAGING ONLY)

Parent Apollo Experience 2.0 Issue #150; conversion governance #820. Stacked on draft R369 PR #2527, not homepage #49 or Research Desk #158. Grok and Praxxis retain their TASK-008 production/review ownership. No WordPress install, production writes, analytics, affiliate activation, merchant offer or deployment.

## Change
R369 previously enqueued its CSS at shortcode-render time, potentially after wp_head. R370 adds an opt-in staging-only read-only adapter at wp_enqueue_scripts priority 1. It detects the exact R369 shortcode in the queried singular post, bounded reusable blocks, same-theme template parts and the actual verified resolved block template, if exposed by WordPress. It does not guess template hierarchy. Foreign/stale theme IDs, cycles and excessive scans are refused. It enqueues the existing R365→R367→R368→R369 CSS once in dependency order before normal rendering. No new visual design, historical claim, map pin or tracking script.

## Reproduce
- php -l experience2/apollo-r370/prehead-assets.php
- php experience2/apollo-r370/qa/wp_contract.php (29 API-stub assertions PASS locally; **not real WordPress**)
- python experience2/apollo-r370/qa/browser.py (8 real local Chromium fixture contexts at 320–1920px, touch, keyboard, no-JS, reduced motion, forced colors, 4× root-font; NOT HTTP/installed WP/CSP/axe or production CWV).

In an already authorized **isolated staging plugin only**, load existing R365, R367, R368 and R369 source, then require_once prehead-assets.php before wp_enqueue_scripts. Exercise [fv_apollo_educator_bridge_r369] on a staging page. Do not install on finalvestige.com without founder/QD approval.

## Commercial custody
Proposed journey: published Grok Apollo long-form **only after asset_id verification** → NASA source-backed R369 educator bridge → existing free Apollo investigation → separately authorized, rights-cleared payable educator kit **only after SKU/checkout verification**. Exactly one editorial CTA. NASA sources linked, commercial image rights not cleared, no NASA endorsement. No verified paid orders, refunds, fees or qualified-human cohort: net revenue per 1,000 qualified sessions is NOT COMPUTABLE.

## HARD HOLD
Installed WordPress/Assembler before-first-paint style order, independently run axe-core and screen readers, browser-enforced HTTPS/CSP, native zoom, p75 CWV, hosted exact-head CI, provenance/rights and approved checkout, founder/QD authorization. Local fixture CLS=0 cannot establish live CLS. No deployment, WP edits, social posting, spending or new measurement scripts.
