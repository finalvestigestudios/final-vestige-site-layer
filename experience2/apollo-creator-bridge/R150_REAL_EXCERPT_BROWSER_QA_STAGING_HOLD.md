# Apollo R150: source-bound browser QA — STAGING HOLD

Scope: Issue #150, cross-reference #820, charter #818. Stacked on Apollo R149 PR #1149 only. Isolated experience2/apollo-creator-bridge files; no homepage PR #49 or Research Desk PR #158 changes.

## Built
- r150_real_excerpt_gate.py binds the offline browser test to the exact real WordPress-source-derived R149 fixture Git blob: 899b7c4a1c46b2e6c46bf079d6784124636a011e. Arbitrary/synthetic HTML cannot masquerade as actual source. Explicit --controlled-model downgrades receipts to CONTROLLED_MODEL.
- Reuses R149 native Chromium before/after negative controls and 320/360/390/768/1440/1920px screenshots, keyboard, slider, source-link and no-JS 390 tests.
- Adds no-JS at all six widths: three archival contexts remain visible, source links/one real investigation link, enhancement controls hidden, horizontal overflow checks. Optionally performs real axe-core WCAG 2.2 A/AA scans at all widths from a supplied locally verified axe.min.js. Missing axe is INCOMPLETE, not a fake pass.
- Always marks production acceptance false; no network request, actual WordPress/Assembler theme, external image bytes, live LCP/CLS, commerce, NASA commercial image rights or real paid orders are certified by offline fixture tests.

## Reproduce on clean checkout
From experience2/apollo-creator-bridge on R150 branch (requires Python Playwright and local Chromium):

1. python -m unittest -v test_r149_gallery_release_candidate.py test_r150_real_excerpt_gate.py
2. python r150_real_excerpt_gate.py --input fixtures/r149_published_chronology_source_excerpt.html --out r150_actual_excerpt_run --axe /path/to/verified/axe.min.js
3. If axe-core is not available, omit --axe. Receipt will say NOT_EXECUTED_AXE_UNAVAILABLE and source_excerpt_qa_complete=false.
4. For synthetic negative control ONLY: python r150_real_excerpt_gate.py --input r149_model_fixture_unpatched.html --out r150_model_run --controlled-model
5. Repeat into a new directory; compare screenshots and QA receipt SHA-256. Never overwrite earlier evidence.

## Actually verified 2026-11-05
Authenticated read-only WordPress page 2017 remains published, last modified 2026-11-04T17:09:24. Raw Gutenberg HTML: 96,274 characters; erroneous single-photo JavaScript selector present once, repaired selector absent. R149 source changes not published.
Native Python R150 8/8 PASS. Real Chromium 144 controlled-model regression: 153/153 PASS, 7 screenshots with identical hashes and identical JSON receipt over two independent runs. No real-source-derived excerpt browser run in this environment; no axe-core bundle; no full WordPress page QA, live image transport or production LCP/CLS. Exact-head hosted CI and independent QD not verified. Source and test local Git blob identities match GitHub after upload.

NASA advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/. Editorial attribution and archival source linking are not a commercial image-use clearance or product endorsement. Three historical photographs are not certified for use in paid FV merchandise.

## Conversion first: ONE staged pathway, no activation
Grok Apollo evidence-led historical long-form / Shorts (Grok owns production) -> real Atlas at https://finalvestige.com/apollo-1-evidence-atlas/ with an approved immutable asset_id, utm_source=youtube, utm_medium=organic_social, utm_campaign=history_pilot_2026_11, utm_content=approved_asset_id -> ONE current Read the full investigation editorial link -> optional **separate** relevant educator casefile product offer ONLY after an authenticated sellable SKU, rights audit, fulfillment/refunds review, transparent placement, mobile checkout QA and founder approval. No unverified worksheet destination; do not insert a merchant affiliate advertisement into the narrative. The educator casefile is presently a NOT VERIFIED product hypothesis.

The conversion hypothesis is that accessible, source-custodied evidence improves qualified reader-to-offer intent, not that attention itself equals purchase. Grok TASK-008 and Praxxis external review remain in their shared Drive queues, not rewritten here.

Measurement contract from #820: qualified human sessions per asset_id and UTM -> verified CTA click -> independently confirmed subscriber if applicable -> verified merchant order -> refunds/fees -> realized net revenue per 1,000 qualified sessions with 7/30-day cohorts and tiny-sample warnings. No Apollo-specific attributed revenue, paid order, qualified Grok asset or confirmed buyer has been observed or authenticated.

## Release gate
STAGING HOLD until actual checked-in excerpt passes real Chromium + axe, full WordPress staging/theme/browser and responsive/200%-zoom/keyboard/touch/screen-reader QA, real media transport, measured staging LCP/CLS, rights/merchant acceptance, independent QD, exact-head CI and founder approval. No CMS, production, analytics, affiliate, social, email, merchant or paid-service modifications made.
