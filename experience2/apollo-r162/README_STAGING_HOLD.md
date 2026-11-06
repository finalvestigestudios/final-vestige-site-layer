# Apollo R162: Accessible failure state for archival images

Status: **BUILT / OFFLINE CHROMIUM TESTED / STAGING HOLD**. No WordPress, analytics, email, affiliate, or production write.

Source: WordPress Page 2017, read-only editor inspection 2026-11-06, last modified 2026-11-05T18:19:45; exactly extracted gallery fragment `live_gallery_fragment.html`, SHA256 `c814d0ce743a6f49caf16c66218702d9272d8b370ba965dc36b61a3b56df56df`. This is a partial excerpt, not the full website source. NASA photos are contextual: S66-58038 (October 1966 training), S67-15717 (January 1967 processing), KSC-20170124-PH_KLS01_0129 (January 2017 museum). They are not fire telemetry. Technical chronology: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/. Commercial media rights remain **UNCLEARED**.

`gallery-fallback.js` and `.css` are additive staging proposals. When an archival image fails, the figure retains its original NASA source link, date, caption and reserved layout space while showing an accessible failure notice. If the NASA source link is absent, the enhancement fails open. Neither asset makes network requests, measures visitors, advertises products, or introduces speculative map records. With JS off, source links and figures remain readable. The source fragment is preserved as evidence, not proposed for replacing current WordPress content.

Run `python src/test_gallery_fault_tolerance.py --source src --out fresh-evidence-dir` with Python Playwright and `/usr/bin/chromium`. Real Chromium with deterministic intercepted image responses, not networked photo requests. Six widths: 320, 360, 390, 768, 1440, 1920; keyboard, reduced-motion, touch-capable context, no-JS, source-link mutation test, CLS/LCP offline observations, screenshot checksums. Two local runs on 2026-11-06: **140/140 PASS each**, 6/6 identical screenshot hashes. The test shell is not the entire WordPress page. **axe-core NOT EXECUTED; actual WordPress staging NOT TESTED; networked image delivery/LCP/CLS NOT MEASURED; hosted exact-head CI NOT VERIFIED.**

Only one appropriate next action: **Read original investigation**. High-intent Grok YouTube educators → verified Apollo Atlas → original investigation; a later rights-cleared product/checkout step is **blocked** pending merchant listing, delivery, permissions and founder approval. Do not place unrelated affiliate offers into the historical record. Grok owns script/distribution, Praxxis creator QA, Claude site/analytics production and founder release approval. Use Issue #820 standard `utm_content=asset_id`; no extra scripts. No confirmed paid Apollo conversions or net revenue can be computed.

OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:
* Approved educator casefile (not yet verified) → purchase → absent rights-cleared SKU → verify inventory/checkout → BLOCKED → Growth/Claude/founder.
* Free Apollo historical evidence → social-to-Atlas-to-investigation → possible image delivery failure → source-preserving fallback → BUILT; 140/140 offline PASS, real site NOT TESTED → Apollo/Site QA.
* Paid orders → realized net revenue → missing asset IDs and merchant reconciliation → compare TASK-008 to #820 → UNVERIFIED → Grok/Praxxis/Claude.

Staging release requirements: native theme/shortcode compatibility, exact WP build, actual CSP, genuine axe-core/manual screen-reader/200% zoom, 320–1920 networked browser tests and actual LCP/CLS, real NASA image delivery, QD and founder approval. Removal of these two additive assets is the rollback. Homepage PR #49 and Research Desk PR #158 untouched.
