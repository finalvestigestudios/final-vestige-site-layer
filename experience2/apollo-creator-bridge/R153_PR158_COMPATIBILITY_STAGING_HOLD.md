# Apollo R153 — Research Desk template-compatibility correction (STAGING HOLD)

Scope: Experience 2.0 Issue #150; revenue/attribution Issue #820 and charter #818. Stacked on isolated R152. No edits to homepage PR #49, Research Desk PR #158, WordPress, analytics, Grok/Praxxis, merchant systems, or production.

## Root cause — actual GitHub PR #158 source inspected

At blob `403d128c57b9bc82dac7c619651689070edef86c`, `experience2/research-desk/templates/ledger.html` contains **zero** `data-fvx-clear` elements and **zero** `data-fvx-chrono-link` attributes. The six actual evidence records have `data-fvx-record`, search indexes, and a hidden `data-fvx-tools` container. R152's JS requires a Clear button and therefore exits without initializing on PR #158's actual markup. Previous passing synthetic tests did not detect this mismatch.

R153 supplies `r153_source_ledger_compat.js` and scoped staging-only `r153_source_ledger_compat.css` (responsive wrap, 44px touch target, visible keyboard focus; load CSS after the PR158 stylesheet) as an **isolated candidate replacement**, NOT a second script to load beside PR #158's JS. It generates the optional Clear button only in JS when the six-record metadata contract is valid. External and repeated same-fragment links can reveal search-hidden evidence records. Native anchors and no-JS evidence remain readable. Malformed indexes or duplicate record IDs fail open.

## Evidence and limits

- Node v22.16.0 `--check` of the source JS: PASS.
- Playwright Chromium 144.0.7559.96, **PR158-markup-shape controlled fixture (NOT complete real template)**: 99/99 checks PASS at 320, 360, 390, 768, 1440 and 1920; keyboard, touch, reduced motion, source links, hash continuity, fail-open/no-JS, horizontal overflow. Two runs identical (JSON receipts + 6 screenshot SHA-256 values).
- Committed smoke runner `r153_pr158_smoke_qa.py`: 36/36 PASS in two native Chromium runs; receipts and screenshots identical.
- Prior R152 browser runner using R153 JS: 79/79 controlled-fixture checks PASS.
- Source JS Git blob `3610ec8f68fc0332db04bcfa5c368574818e9866`; smoke runner Git blob `5066635d5b2ec213f975469fcc176c989ba2e82c` — both match locally tested files.
- **NOT RUN:** complete PR #158 template, published WordPress 2017 export, actual-page axe-core, page LCP/CLS, third-party image delivery, exact-head hosted CI. NASA individual media commercial permissions and merchant checkout/confirmed orders are NOT VERIFIED.

## One controlled conversion pathway

Audience: secondary educators wanting primary-source historical investigations. Flagship: **Apollo 1: Fourteen Seconds, More Than One Failure**. Proposal: Grok video/Shorts asset_id → Apollo Evidence Atlas → **Read the full investigation** (single existing, nonintrusive editorial action) → possible educator-casefile interest expression through a separately approved consented mechanism → **future** rights-cleared educator casefile purchase **only if a real Payhip listing, license, delivery, checkout and founder approval are verified**. No casefile purchase CTA is approved or live. No unrelated affiliate inserted into tragedy history.

Hypothesis: reliable source navigation reduces investigative friction and improves visitor trust; **not evidence of sales**. Existing approved measurement only: qualified human asset_id/UTM sessions → investigation click → confirmed lead if applicable → independently verified merchant paid order → refunds/fees → net realized revenue per 1,000 qualified sessions, with 7/30-day cohorts and small-sample cautions. Attribution and Apollo paid revenue currently NOT VERIFIED.

## Gates and owners

**Apollo:** full-source page/PR158 browser acceptance, source rights custody, keyboard/touch, axe, responsive 320–1920, screenshot review and meaningful performance measurements.

**Claude/site lead:** review staged integration with WP/theme and independently guard production; frozen homepage PR #49 untouched.

**Growth/founder:** independently verify rights-cleared sellable SKU, checkout/order evidence and authorize commercial CTA/release; no spending or live changes.

**Grok/Praxxis:** provide independently reviewed platform asset IDs and UTMs through existing TASK-008 Drive handoff; do not replace their production queue.

**QD/founder:** exact-head CI and independent acceptance before any governed production release.

**BUILT / FIXTURE-TESTED / STAGING HOLD — not merged, published, or revenue-verified.**
