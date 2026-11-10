# R267 — screen-only mobile-wallet candidate and browser custody (DRAFT / HARD HOLD)

**Scope:** Issue #136 only; conversion coordination #820, charter #818. **Date:** 2026-11-10. No publication permission or QD approval. **Base:** R266 PR #1915, head `e0cde442cce757c2152d93cda10ac9537410fed0`. All changed files confined to `preparedness/`; original sources, Tool #104, 35 articles, 2,000 citation occurrences, historic URLs, and safety status remain unchanged.

## Verified source-to-candidate change

R266 demonstrated that original **unpublished** R264 card (`40782ef142edfd348fec53eb6d8a0dc673244dea`) causes horizontal overflow in narrow browser previews: source card width 672 CSS px; document widths 680 px at 320, 360, 390px. R267 adds a **separate** unapproved reviewer-only alternative (`5ae643302faf6bce47e8c507fbcfff9c099eaf00`) by inserting ONE `@media screen and (max-width: 739px)` rule ahead of the unchanged `@media print` rule. Narrow screen layouts stack Front and Back and use 14px preview warnings. Exact reverse deletion of this new rule reproduces the original 2,084-byte R264 HTML, without modifying its two warnings, five blank prompts, 7-inch print formatting, any citations or routes. No credentials or personal data entered.

## Real Chromium evidence (bounded; not certified)

Local Chromium `144.0.7559.96`, Playwright `set_content`, no remote assets or household input. Direct initial screen and PDF experiments, plus an **independently rerun, network-aborted reproduction** with the committed `r267_reproduce_browser_observation_REVIEW_ONLY.py`:

| Viewport in CSS px | Original R264 document scroll width | R267 screen-only preview |
|---:|---:|---:|
| 320 | 680 | 320 |
| 360 | 680 | 360 |
| 390 | 680 | 390 |
| 768 | 768 | 768 |
| 1440 | 1440 | 1440 |

Both print modes (JavaScript enabled and disabled) maintain measured 672 × 206 CSS px card, two 335px faces and warning text computed to 10.6667 CSS px (8 pt). One tested four-render run yielded the *same* PDF SHA-256 `232495acec8411828d2c8a67ee6118b6441aafe52de050dd95a9a9f33d13193f` for old/new and JS on/off. `pdftotext -layout` displayed both on-card warnings; a 140-dpi raster was visually inspected. **Follow-up rerun exposed that PDF object/metadata bytes can differ between browser contexts despite identical source text and geometry.** The reproduction script therefore checks semantic text plus geometry, not equality of PDF SHA across contexts. PDFs and 10 screen PNGs are review artifacts, not deployment inputs. The check is reproducible only within tested configuration; other browsers, printer paper, cut/fold, accessibility and 200% real-browser zoom remain untested. An exploratory **CSS-simulated** body zoom at 768px overflowed; that simulation is *not* equivalent to browser zoom and requires dedicated accessibility QA. Do not describe this as a live-site defect or accessibility PASS.

## Source and negative-state custody

- R267 gate: `tools/r267_wallet_responsive_preview_hold.py`, Git blob `36ab403f12c70db3f0d5c0c8592ea6d8a45f4aaf`.
- R267 HTML candidate: `audits/r267_responsive_wallet_card_REVIEW_ONLY.html`, Git blob `5ae643302faf6bce47e8c507fbcfff9c099eaf00`.
- R267 browser observation: `audits/r267_responsive_browser_observation_REVIEW_ONLY.json`, Git blob `74dc8e0f9cbb07e6cfd14a2d2dd3b4552239e40f`.
- R267 isolated Python tests: `tests/test_r267_wallet_responsive_preview_hold.py`, Git blob `5980e6fb7315e008de18609483797003c7f75556`.
- Explicit offline browser reproduction: `tools/r267_reproduce_browser_observation_REVIEW_ONLY.py`, Git blob `461d97b005de520bbece907d6224f15101abfb2e`.
- R220's pre-export custody now loads R267's exact gate, checks all negative flags and R266 inherited overflow witness, authenticates reproduction script, and checks gate/HTML/receipt/repro bytes again at audit completion.
- Original R264 candidate, original Tool #104, historical R266 negative receipt, all seven Claude cluster heads, independent QA PR #157, synthetic-fixture PR #169 and homepage lead PR #1689 are not altered.

## Actually executed vs not executed

**Executed locally:** 66/66 isolated Python regression tests using the exact bytes of the new gate, test file, candidate and receipt; all four Git blob identities match commits. Python compilation succeeded. Chromium screen testing at 320/360/390/768/1440 (original and candidate), JS on/off Letter print-to-PDF, visual PNG review, text extraction, and an independently repeatable network-aborted script. Reproduction differences in PDF hashes are documented, not concealed.

**Not executed:** full repository `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete inherited 36+ test suite, genuine R220–R267 full 35-article integration, intended 41 WordPress draft exports, other browsers/OSes, actual paper cutting/folding, child privacy, accessibility, independent citation/medical/source review or QD signoff. The present local environment cannot DNS-resolve `github.com` for a full checkout; connector access permits authenticated isolated file CRUD only. No false native PASS.

## Open safety/source review gates

All 32 shared-source groups and the three originally disputed occurrences (Article #7 two CDC references; Article #20 one Ready.gov) remain unresolved. Article #7 chemical-contamination advice requires qualified review; Article #15 and Tool #104 still require independent child/privacy/print/accessibility review. 8pt print cautions and physical privacy risk remain unresolved. The mobile-only alternative does NOT repair original Tool #104 or become an approved downloadable resource.

## Conversion-first acceptance; research only

**Audience hypothesis:** households who already watched an authentic Grok asset about emergency contact/reunification. **Public free destination only:** `https://finalvestige.com/preparedness/` currently links to an official Ready.gov emergency checklist. A specific existing creator `asset_id`, its rights/source receipt, tracked UTM and signed-out mobile destination have NOT been authenticated in TASK-008; do not post or invent an asset or imply a funnel is live.

**Proposed on-site copy, NOT installed:** “Build a household contact plan using the current official checklist. The optional printable card is still under privacy review and is not available for use.” Never put an unreviewed wallet-card download CTA in public content.

**Commercial candidate:** existing `Legacy Triage` PDF, only a provisional $19 storefront listing. Complete product-content rights, audience suitability, sensitive credential handling, founder approval, fulfillment, refunds and fees are unverified. **Do not publish or activate a paid CTA.** Existing Focus Fieldbook remains separate and free; the retired water freebie remains retired.

**Offer → funnel step → blocker → experiment → evidence → owner**
1. Official free guide → matched social landing: asset/rights/UTM unknown → Grok/Praxxis authenticate preexisting published asset only → NO VERIFIED MATCH → Grok/Praxxis.
2. Free guide → optional printable card: source child/privacy/8pt printing undecided → real paper, screen reader and qualified review → R267 browser bounded only; HARD HOLD → Preparedness/independent QA.
3. Free guide → optional Legacy Triage: rights, suitability/credential risks unknown → rights/full-PDF audit and explicit release decision → NOT APPROVED → founder/commerce.
4. Paid checkout → settled delivery: merchant payment/fulfillment/refunds unknown → owner-authorized transaction reconciliation without test purchase absent approval → NOT TESTED → commerce.
5. Tagged qualified sessions → net sales: no independently verified attribution/settlement → reconcile merchant order IDs, refunds and fees to 7-/30-day anonymous cohorts and report sample size → NET REVENUE/1000 SESSIONS NOT COMPUTABLE → analytics/commerce.

No publication, WordPress/CMS/navigation, website analytics, Grok queue, social post, merchant, affiliate, email, spending or paid service changes. **DRAFT / HARD HOLD.**
