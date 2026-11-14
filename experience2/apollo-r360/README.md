# Apollo R360 — source-link touch target + independent browser acceptance

**Scope:** Research-only staging. Stack on R359, do not merge or deploy; do not edit frozen homepage PR #49, Research Desk PR #158, WordPress content/settings, Grok/Praxxis TASK-008, tracking, merchants or email.

## Actual defect and correction

The **2018 NASA post-fire engineering record** link inside the native `<details>` Source Drawer measured **22 CSS pixels high** at 390px viewport after keyboard expansion. It was readable but below the 24px minimum for WCAG 2.2 target size and the existing Apollo target goal of 44px. R360 adds a selector-scoped `min-height:44px`, `display:inline-block` and vertical padding to `experience2/apollo-r355/postfire-ledger.css`. It does not alter source records, URLs, page identity, print content, JavaScript, or the editorial CTA. Baseline pre-fix was independently reproduced on 2026-11-14 in Chromium with the reviewed R359 code. Do not mistake 44px bounding boxes for proof of all WCAG requirements or all assistive technology behavior.

## Executable local checks

```sh
php -l experience2/apollo-r355/postfire-ledger.php
php experience2/apollo-r359/qa/wp_contract.php
php experience2/apollo-r360/qa/php_custody.php
python experience2/apollo-r360/qa/compact_browser.py
python experience2/apollo-r360/qa/browser_acceptance.py  # independent supplemental, archive-only
python experience2/apollo-r360/qa/build_evidence.py
```

The source-controlled compact Playwright suite covers 320/390/768/1440/1920 CSS-pixel widths, JavaScript off, optional filter interactions (13/3/5/1/4 index record counts), keyboard Enter on the native source disclosure, touch, reduced motion, forced colors, no horizontal overflow, 44px corrected target, the Chromium accessibility-tree named links, and native print PDF historical-source retention. The separate archived acceptance suite adds programmatic contrast sampling, 24px minimum-target sampling and local synthetic LCP/CLS observations; not an axe-core substitute. Browser visuals/screenshots are replayable but timing and PDF metadata may change on regeneration. Determinism applies to packaging frozen artifacts, not creating exactly identical screenshots on another Chromium build.

**Historical provenance:** the original Apollo 204 Review Board did not prove an exact ignition source; NASA's later 2018 retrospective describes 102 deliberate postfire test ignitions as subsequent engineering evidence, NOT the Board's 1967 findings. NASA source-page links do not themselves clear images, astronauts' likenesses, logos, endorsement, marks or third-party media. See https://sma.nasa.gov/sma-disciplines/accllp/apollo-1 and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No NASA photos were embedded and no invented geographic pins or connections added.

## Business/release hold

Only one editorial continuation remains: Grok's yet-to-be-verified Apollo documentary and asset_id → source-backed Evidence Atlas → existing **free** Apollo 1 investigation → independently validated Apollo educator evidence product **if** founder and Claude verify a rights-cleared payable SKU, delivery and checkout. This is a conversion hypothesis, not a sale. No unapproved purchase action. Grok owns production/posting, Praxxis creator review, Claude commerce/instrumentation. Attribution from `utm_content=actual_asset_id` through qualified human sessions, consent-aware lead, verified merchant order, fees/refunds and realized net/1k qualified sessions is **UNVERIFIABLE** until source-of-truth records are available.

Production remains **HARD HOLD**: installed WordPress/Assembler, actual browser HTTP/CSP, genuine axe-core, independent screen readers, Firefox/WebKit, hosted exact-HEAD CI, commercial media rights, offer/checkout verification, QD/founder approval. This QA is local PHP-rendered Chromium; it is not production CWV, live conversion evidence, or WordPress acceptance.
