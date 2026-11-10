# R266 — Apollo post-article conversion bridge (CLI preview; HARD RELEASE HOLD)

**Scope:** isolated Experience 2.0 Apollo staging continuation, after the *free* historical investigation. Issue #150 / conversion coordination #820 / founder charter #818. No homepage PR #49, Research Desk PR #158, WordPress, analytics, seller account, or production changes.

## Why this exists

One controlled editorial-to-commerce hypothesis, not an activated offer: **Grok's as-yet-unverified Apollo long-form asset → source-linked Apollo Atlas → free “The Hatch Opened Inward” article → optional clearly disclosed Mini Museum buying guide → independently verified partner order and net commission**. The actual guide at https://finalvestige.com/mini-museum-history-collectibles/ is publicly available and discloses that FV may earn commission. Current FV publisher acceptance and payable transaction records are **not** verified. No Mini Museum specimen is described as an Apollo flown artifact; the historical investigation is not interrupted or paywalled. No merchant redirect is inserted into the Apollo narrative.

## What is built

- `fv-post-article-preview.php`: **CLI-only** rendering helper, not a WP plugin (no `add_action`, shortcode, filter, or automatic inclusion). It outputs nothing without five distinct strict-boolean preview approval flags, including `founder_preview_permission`; it refuses HTTP usage. This is a code review gate, **not** evidence that the founder gave preview or publication permission. The script is never installed and is unreferenced by the site.
- `assets/postscript.css`: modest single-CTA companion card isolated *outside* the protected `.fv-apollo-atlas`, native HTML, text-based, no images/JS/network tracking; explicit commission and NASA-nonendorsement notice; touch target >=44px, visible focus, forced-colors and reduced-motion behavior, print omitted.
- `qa/cli-preview.php`: explicit CLI smoke/test fixture and 17 strict approval-state assertions.
- `qa/committed_smoke.py`: exact-source original PHP-rendered Atlas browser smoke, responsive 320–1920, no-JS, Chromium ARIA tree, original NASA sources, no calls or overflow.
- An **extended independent QA runner and screenshots are in the accompanying audit archive**, not included in this PR. Extended QA repeats 23 browser contexts, including reduced-motion/no-JS, forced-colors, two negative-control mutations, and reproducible screenshots; committed smoke independently executes 10 contexts.

**Placement limitation:** the local test shows this *after the original Atlas and a hidden placeholder article seam*. It does **not** place the card into a real WordPress article. Actual article-end placement, canonical route, template/Assembler CSS, HTTP/CSP and installed WordPress must be independently tested and approved before any proposed integration. The source of historical evidence and original one free article CTA are unchanged.

## Run the committed smoke

`python experience2/apollo-r266/qa/committed_smoke.py fixture/sealed-r238 experience2/apollo-r262 experience2/apollo-r266 experience2/apollo-r263/qa/wp-real-source-sequence.php`

The protected R238 fixture seal SHA-256 is `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`. In the extended local test, NASA source links 55, Atlas internal fragment anchors 31, exactly one original free investigation CTA plus one separate guide CTA after the Atlas, no merchant URL in the postscript, no external requests, no detected overflow.

**Explicit gaps:** axe-core not available or executed; no independent screen reader; no real browser UI zoom; browser `localhost` navigation blocked by administrator so tests use Playwright `set_content`; no installed WordPress, live HTTP/CSP acceptance, or field LCP/CLS; no CI statuses, outside QD, merchant confirmation, Apollo Grok asset/post or purchase evidence. NASA's Review Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ determined an electrical arc probable, but no specific initiator conclusively established. NASA's advertising guide https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ bars implied endorsement and imposes additional likeness restrictions. Source citations are not promotional permissions.

## Release governance / owner

- **Founder / Claude:** authenticate approved Awin publisher status, current merchant terms, authorized guide/affiliate placement, privacy-safe measurement, refund/fee/settlement reporting and public release approval. No unapproved activation.
- **Grok / Praxxis:** reconcile real long-form Apollo asset_id, publication URL, landing link/UTM from existing Drive TASK-008. No invented asset and no posting by Apollo.
- **Apollo QA:** original-source and independent in-site acceptance only; maintain STAGING HOLD until genuine axe, actual installed WP and independent review.

**No claims of live paid conversion or realized net revenue.** KPI remains authenticated net revenue per 1,000 qualified human sessions for seven- and 30-day cohorts, when denominators and merchant data exist. An outbound click is never a paid order.
