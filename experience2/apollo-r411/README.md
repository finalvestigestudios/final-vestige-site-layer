# Apollo Experience 2.0 R411 — NASA Source Drawer (unmerged staging proposal)

**Scope:** `experience2/apollo-r411/` only. Stacks on R410 review PR #2761. Does not edit homepage PR #49, Research Desk PR #158, WordPress content/settings, social channels, creator task documents, analytics or commerce. Production is **HARD HOLD**.

## Built

`[fv_ex2_source_drawer_r411]` is a default-disabled, single approved-page WordPress shortcode. It presents six documentary source records as native `<details><summary>` disclosures in an ordered list, each with an explicit finding, evidence boundary and two direct NASA links. R411 has no JavaScript, no images, no maps, no cookies, no analytics, no lead forms and no paid CTA. No photo-rights claim is made: archive hyperlinks are **not** embedded images. All source URLs are the actual NASA archive records in original PR #158; record six links to NASA's separately dated December 1967–February 1968 flammability tests rather than treating those tests as evidence of the January ignition. The original source remains immutable.

Activation requires all of `FV_R411_ENABLED=true`, `FV_R411_STAGING_PAGE_ID` equal to the current singular page, WordPress environment `staging`, and an exact Git-blob pin of the reviewed local CSS. If any gate fails, a plain HTML link to the existing free Apollo investigation replaces the component. Page-specific `wp_enqueue_scripts` adds one versioned local CSS asset early, including cases where a shortcode lives in a nested or reusable block. There is no prod installation or automatic activation.

### NASA primary-source and rights ledger

- Original Apollo 204 Board, ignition initiator not positively identified: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA retrospective dated 2018-02-14: 102 **later** Command Module deliberate ignitions between December 1967 and February 1968: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
- NASA images and media guidance, publisher rights and non-endorsement, which **does not automatically confer rights to third-party credited media**: https://www.nasa.gov/nasa-brand-center/images-and-media/
- Original #158 source: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158 — `experience2/research-desk/templates/ledger.html`, original Git blob `403d128c57b9bc82dac7c619651689070edef86c`.

## Local reproducible QA (not installed WordPress)

```bash
php -l experience2/apollo-r411/staging-source-drawer.php
php experience2/apollo-r411/qa/test_php.php
python experience2/apollo-r411/qa/test_browser.py
python experience2/apollo-r411/qa/package_evidence.py
```

The browser test uses **real PHP-generated HTML and real Chromium via Playwright**, injected into an in-memory document. Tests exercise native disclosures with JavaScript disabled, keyboard and touch, accessible names from Chrome's accessibility tree, reduced motion, forced colors, 400% root font, 320/360/390/768/1024/1440/1920px and CSS-computed layout. It saves 12 responsive/accessibility screenshots and counts horizontal overflow. Do not mislabel this as an installed staging, genuine axe-core or navigated HTTP test. **axe-core NOT RUN; navigated LCP/CLS/INP NOT MEASURED**. CI checks and independent screen-reader/QD review are not replaced by CDP accessibility names. The deterministic ZIP is generated locally and excluded from Git.

## Conversion contract and owners

**One audience:** history/science/homeschool educators curious about primary-source Apollo evidence. **One next action:** existing free Apollo 1 investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . The *potential* $19–$39 individual-educator lesson dossier from charter #818 remains a **pricing hypothesis**, not a rights-cleared merchant SKU. No sale, checkout, lead capture or affiliate click is claimed. No sales CTA until the founder and Claude independently verify rights, deliverability, authorized checkout, fees/refunds and approval.

Grok retains long-form and Shorts scripting/posting; Praxxis independently verifies any authentic already-posted asset ID, topic match and allowed destination; Claude owns core website/consented attribution; Apollo QA owns in-site prototype; founder controls release/commerce/spending. No TASK-008 edits. Conversion hypothesis: transparent references reduce trust friction and improve qualified evidence→free-article progression; measure only if authenticated traffic/click data exists. Required funnel: qualified human `asset_id`/`utm_campaign` sessions → landing → relevant CTA → confirmed lead where applicable → confirmed paid order/settled affiliate conversion → refunds/fees → realized net revenue. **net revenue per 1,000 qualified sessions is not computable without both verified numerator and denominator**; evaluate 7/30-day cohorts with tiny-sample caveats.

## Release gate (HOLD)

No deployment without installed WordPress staging on the exact approved URL, original source and rights review, genuine axe-core and independent screen-reader, real HTTP/CSP/network, native browser zoom and reliable LCP/CLS/INP observations, current CI on exact commit, QD independent signoff and founder production approval. No production writes, social posting, paid services or unverified affiliate integration.
