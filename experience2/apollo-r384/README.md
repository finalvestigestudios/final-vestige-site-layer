# Apollo Experience 2.0 R384 — primary-source document gallery (research only)

**BUILT; offline PHP stubs and local Chromium TESTED; NOT installed on WordPress; NOT LIVE; no verified sales.** Draft-only isolated component, stacked on R383 (PR #2615) to retain R377 custody and R381 curated Atlas source contracts. Do not merge with conflicting alternative R381 PR #2603. No homepage PR #49, Research Desk PR #158 or Grok TASK-008 changes.

## Purpose
Six source **questions**, not six unique NASA publications. Five questions cite NASA's hosted 1967 Apollo 204 Review Board report, and the sixth cites NASA's 2018 post-fire flammability testing retrospective. The text gallery groups them into a three-stage chronology without mapping to coordinates, causal edges or invented satellite/photo provenance. Every card shows a source-backed claim, what the source *does not* prove, native keyboard/touch disclosures, and a direct NASA link. All source links remain visible/printable without JavaScript. Two document URLs are not six distinct documents.

This is *not* a photograph gallery: no photographs, logos, scanned images, 3D models, external scripts, paid CTA, newsletter form or visitor tracking are embedded. NASA's media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/ . The NASA insignia and logos are protected; blanket rights are not inferred from NASA hosting, and endorsement must not be implied. The 2018 test series (102 deliberate Command Module ignitions) is **later** than the January 27, 1967 accident. Original Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; retrospective: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ .

## WordPress integration contract
The shortcode is `[fv_apollo_source_gallery_r384]`. Optional staging-only loader requires `fv_r377_environment()`, `fv_r377_records()` and R381's `fv_r381_approved()` canonical six-record guard. A fixed expected NASA URL per record rejects swapped source roles. It refuses foreign shortcode owner registration. The component is inert unless installed by the independent approved staging lane; **do not install on production**. Its CSS enqueue is scoped to directly queried singular post content and sealed by SHA-256, with semantic unstyled fallback if CSS is missing. Nested reusable/template/builder shortcode CSS coverage is explicitly **NOT VERIFIED**: do not assume existing R383 loader covers this distinct R384 shortcode. No JavaScript is required to use the component. No WordPress settings/content/DB writes, no affiliate activation or commerce links.

## Local QA and deterministic reproduction
From a checkout containing `experience2/apollo-r377/custody.json` (verified SHA-256), and the new R384 directory:

```sh
php -l experience2/apollo-r384/document-gallery.php
php experience2/apollo-r384/qa/contract.php
python experience2/apollo-r384/qa/browser.py
python experience2/apollo-r384/qa/package.py
python experience2/apollo-r384/qa/package.py # same archive SHA-256
```

`qa/contract.php` tests source corruption, wrong source/role, context protocol, production refusal, absent sitewide CSS, collision preservation, fallback, and the exact one free CTA. `qa/browser.py` uses genuine headless Chromium and locally rendered PHP fixtures, ten 320–1920px contexts, keyboard/touch/no-JS/reduced-motion/forced-colors/4x-root-text, CDP accessibility tree role inspection, visual screenshots, PDF source hyperlinks and local LCP/CLS observers. It **does not** execute axe-core: genuine axe-core is unavailable. It is not an installed WP/Assembler, CSP, HTTP asset waterfall, Lighthouse or real visitor Core Web Vitals test. Native 400% browser zoom, Safari/VoiceOver, NVDA, hosted exact-HEAD CI, and staging LCP/CLS/INP remain unverified. Screenshots and PDF in QA are reproducible *lab evidence*, not live production screenshots.

## Controlled visitor pathway and commercial release gate
The founder-approved objective is realized net revenue, not time-on-page. Proposed hypothesis only: **published, approved Grok Apollo documentary** (asset ID/UTM not verified) → this document-source gallery → [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → *only if subsequently approved, rights-cleared and merchant-tested*, an educator source-analysis kit. One link to the existing free investigation is the only onsite next step; this gallery does **not** represent a paid product. Product SKU, fulfillment, merchant evidence, attribution, qualified sessions, paid conversions, refunds, fees and realized net revenue are not verified.

| Offer → funnel step | Blocker | Change / experiment | Pass / fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Rights-cleared educator kit → paid order | No verified SKU/checkout/rights | Hold purchase CTA, separately validate offer | HOLD / unverified | Founder + Claude |
| Grok video → qualified visitor | Published asset ID and organic UTM source unavailable | Creator/Praxxis review; preserve script/channel ownership | Not observed | Grok + Praxxis |
| Source gallery → existing free investigation | Readers need visible source proof with no invented photo rights | Source-linked native disclosure cards and one free CTA | Local PHP/Chromium PASS; installed staging PENDING | Apollo QA |
| Qualified traffic → realized net revenue | No confirmed orders, settlements or 7/30-day human cohorts | Require source-confirmed paid conversion minus refunds/fees | KPI not computable | Claude / Commerce |

**Release HARD HOLD** pending installed WordPress/Assembler and real asset/CSP QA, actual axe-core, independent screen readers, staging performance and hosted CI, visual approval, commercial offer validation, independent QD and founder production authorization. No merge/deployment/WordPress edits, Grok work, merchant changes, email, social posts, tracking scripts or spending.

Source-of-truth: GitHub Issue #150; commercial coordination #820; business charter #818. Existing approved creator coordination remains in Praxxis/Grok Drive TASK-008.