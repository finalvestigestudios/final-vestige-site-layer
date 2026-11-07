# Mind R187 — conversion-first implementation and acceptance dossier
**UNPUBLISHED / no partner acceptance / merchant CTA HARD HOLD / do not publish, merge, deploy or mail**

## Commercial decision before more design
**Offer candidate 1: Hypnosis Live / Total Focus, exact seller SKU page:** https://hypnosislive.com/mental-skills/total-focus . Seller describes 33 minutes and 47 MB, narrator J. A. Amos, and promises extraordinary concentration. This is a **high-intent, product-specific review opportunity**, not a scientific validation or an approved affiliate offer. The storefront's public dollar figures have varied across observations (an R186 capture recorded $24.44/$29.95; another Nov 6–7 retrieval displayed $17.95/$22.95). None is a confirmed final checkout or refund. Withhold hardcoded price and any countdown. The public partner portal https://affiliates.inspire3.com/ advertises a program; **publisher-specific FV acceptance, allowed website/email/social channels, commission terms, payout records, approved creatives and earning URL are unknown**. Do not infer acceptance or payout from generic portal advertising.

**Offer candidate 2: Zen12 Premium** (https://zen12.com/hnp). Seller lists twelve levels, 48 MP3s, four listening styles and an advertised one-year guarantee. It asserts one hour of meditation's benefits in 12 minutes and brainwave effects, neither established here. Existing R186 Variant A (text), Variant B (same text + optional static 42s poster/transcript) remain disabled and unpublished; R187 fixes the prior source/a11y QA problems. This is a planned experiment, not a delivered video or a running A/B.

**Owned fallback: FV Payhip Mind SKU.** Founder conversion directive makes this next if Inspire3 cannot be authenticated. Site search and currently available connector evidence did **not** establish a named, rights-cleared **currently purchasable** Payhip Mind SKU, exact selling price, refund terms, fulfillment or a verified paid order. Other unrelated Payhip products are NOT evidence. **Do not fabricate a SKU or route visitors to unverified checkout**. Commerce must independently authenticate Payhip inventory, rights, product ownership, real checkout readiness, delivery, policy and merchant order reconciliation. Existing 52-page Focus Fieldbook is **free**, not a paid fallback; preserve its single established Jetpack/Dispatch list.

## Three creator-topic → exact article → next step routes

| Grok-produced hook (proposal only) | Source and eventual landing | Suitable action | Paid-offer fit / release status |
|---|---|---|---|
| “Can a recording really give you limitless focus?” | NEW R187 source-controlled **The Voice in the Headphones** (2,099-word independent Hypnosis Live Total Focus evidence guide); not public | Read seven buyer questions, optional existing /focus/ | **Highest buyer intent; NO authorized merchant URL.** After approval, conditional clearly disclosed merchant decision CTA only in labelled buyer guide. |
| “Don't think of a white bear. What happened?” | R186 Wegner thought-suppression investigation, corrected on R187; not public | Read source, optional existing /focus/ | Low sales intent, preserve editorial neutrality; never force offer |
| “What changed while you watched?” | LIVE Change Blindness https://finalvestige.com/2026/11/02/change-blindness/ | Read original study, optional existing /focus/ | Low intent; no hypnosis upsell attached to the experiment |

**Grok and Praxxis own original social media content, distribution, rights and actual asset assignments** via https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit . These hooks are NOT assigned videos. Before any tagging request actual channel, immutable platform asset_id, public media URL, publish timestamp, rights/credits, CTA placement allowed by platform and authorized canonical landing destination. Do not alter queue or Mini Museum priority. No fake media IDs.

## Buyer intent, credible hook and one controlled decision CTA
**Target audience:** people considering a downloadable, short guided-focus/hypnosis recording who want to know what is delivered and whether evidence supports concentration promises. Not clinical patients seeking treatment. The buyer guide's hook is concrete: a short MP3 file can be described accurately; “limitless concentration” is a separate efficacy claim. The micro-story is the on-page moment a customer moves from running time and file size to a promised changed mind. No invented customer testimonials.

**One CTA contract (currently native disabled):** “Merchant offer unavailable — authorization pending.” After *named account approval, authorized channel and exact earning URL, validated product listing/checkout/return disclosures, source QA, site QA and explicit founder release*, replace with one carefully disclosed outbound CTA: “Review the official Total Focus offer.” Adjacent visible copy: **“If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.”** Do not use affiliate links inside original historical investigations. A plain seller source reference for factual attribution is not an earning link, not a commerce CTA and must never be counted as affiliate_click.

### Conditional disclosure block prototype (NOT an activated CTA)
```html
<section aria-labelledby="total-focus-title" class="offer-under-review">
  <h2 id="total-focus-title">Total Focus — independent offer review</h2>
  <p>Seller describes one 33-minute, 47 MB download; effects and final checkout/returns not independently verified.</p>
  <p class="affiliate-disclosure">If you purchase through an affiliate link we may later add, Final Vestige may earn a commission at no additional cost to you. No affiliate purchase link is active.</p>
  <button type="button" disabled aria-disabled="true">Merchant offer unavailable — authorization pending</button>
  <p>Free alternative: <a href="https://finalvestige.com/focus/">Seven Day Focus Fieldbook</a> (existing Dispatch/Jetpack flow).</p>
</section>
```
Do not modify CMS until separate production approval; this example is design-only. When activated, disclosure must be beside the earning link and understandable at mobile widths, not in a modal or footer alone. No health or cognitive outcome promise.

## Practical A/B hypothesis (NOT TESTED)
**A:** honest source-linked text offer guide with the same permitted paid destination and disclosure. **B:** identical layout and text plus a user-initiated original 30–45-second video with transcript, accessible captions/VTT, no autoplay, `preload="none"`, first-frame poster, keyboard/pause controls, no third-party embed, mobile bandwidth budget. Existing R186 B has ONLY static poster/transcript for a 42-second concept, **not a rendered film**. Preserve a no-JS route in both. Keep merchant conditions and price presentation identical. Pre-register split, sample frame, consent/rights, checkout completeness, return window, cost of production, primary outcome and minimum detectable effect before assignment. Avoid treating 5 visitors as statistical evidence.

**Primary outcome:** independently verified *net realized revenue* per 1,000 qualified unique human landing sessions, with verified paid orders and paid conversion rate as primary operational supporting metrics. If the source-system cannot tie orders lawfully to campaigns, report outcomes un-attributed rather than guessing. Secondary: confirmed leads (not submits), qualified CTA clicks, correct buyer satisfaction/complaints, refunds, page speed. No declaration of A/B winner from clicks alone. Use 7- and 30-day cohorts with exact sample sizes/uncertainty.

## Privacy-safe measurement contract for Claude engineering
No live implementation permission. Do NOT install scripts or duplicate Ahrefs/Jetpack tracking. Use approved existing first-party analytics where possible. Canonical campaign tags **only on actual Grok-created assets**: `utm_source=<platform>`, `utm_medium=organic_social`, `utm_campaign=mind_offerfit_2026_11`, `utm_content=<actual_immutable_asset_id>`. These are public **asset** labels, never viewer IDs, email, IP, fingerprint, raw referral query, session token or names.

Event definitions and proof:
1. `campaign_landing`: observed session landing at approved URL from actual campaign. Do not certify human solely from pageview; document bot/internal exclusions and evidence gaps.
2. `article_to_resource_click`: first-party link interaction to established /focus/ (diagnostic).
3. `confirmed_signup`: only confirmed Jetpack opt-in with consent and welcome/delivery proof, not form click, form submission, or unconfirmed contact.
4. `affiliate_click`: outbound interaction with approved earning link **after activation**; diagnostic only; NOT a purchase.
5. `merchant_confirmed_purchase`: independently reported settled paid transaction, from official merchant or payment processor (not checkout start).
6. `affiliate_paid_commission`: independently reported paid partner commission, net of adjustments and chargebacks; distinguish approved future payable vs actually received.
7. `refund_fee_adjustment`: separately verified fees, refunds, chargebacks and attributable variable costs. Record event timestamps for reconciliation without exposing PII in GitHub.

Report by 7-/30-day cohort: actual `asset_id`, approved campaign, qualified session denominator with confidence, confirmed opt-in leads, verified paid orders, verified paid commissions or owned-product receipts, gross, refunds, processor/partner fees, direct attributable costs, realized net. Formula where allowed: `1000 * verified_net_dollars / qualified_human_sessions` only if all inputs known and denominator > 0. Otherwise **NOT COMPUTABLE**; do not substitute zero.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER
| Priority | Offer / step | Actual blocker | Change / experiment | Acceptance proof | Owner |
|---|---|---|---|---|---|
| P0 | Hypnosis Live → commission | FV named approval, allowed channels/link absent | Verify account, terms, link and tracking; hold disabled CTA until authorized | FAIL/HOLD until partner record with publisher identity + link | Founder / Mind |
| P0 | Own Payhip Mind product → paid checkout fallback | SKU, rights, checkout and refund unknown | Authenticate existing owned inventory and one actual payable SKU | UNKNOWN until rights/sku evidence | Commerce |
| P0 | All paid sales → net dollars | Partner/payments orders and adjustments unavailable | Reconcile 7/30-day settlement data without publishing PII | NOT COMPUTABLE | Commerce / Growth |
| P1 | Grok asset → qualified article landings | Real media ID not supplied | Request real asset packet via Praxxis TASK-008 | PENDING | Grok / Praxxis |
| P1 | /focus/ → confirmed lead | Opt-in + welcome delivery not tested this run | Authorize one controlled guest signup delivery QA using existing list | NOT TESTED | Site QA / Dispatch |
| P1 | A vs B presell | Film unrendered; approval and authorization absent | Complete light 42s clip only after decision gate; real-browser QA and approved controlled split | NOT TESTED | Mind / Site QA |
| P2 | /mind/ taxonomy/nav | No approved live route and canonical PR #172 exists | Keep only new isolated hub preview; coordinate with homepage #150/QA | BUILT draft, NOT LIVE | Mind / Art / QA |

## Reproducibility, security, accessibility, release boundaries
R187 updates only three inherited R186 files on a **NEW isolated branch**, not R186 PR #1370. Fixes: (a) Wegner 1987 **explicit expression instruction** after suppression, not “allowed” neutral period; (b) genuine editorial/FTC anchor destinations added to both A/B; (c) B poster aria-label now describes the actual beam/circle/lettering rather than an absent bear. An exact R186 A/B parity comparison must still pass after removing optional-film section. Verify no scripts/forms/iframe/earning URLs, no merchant CTA enabled, no new Jetpack form, no remote video or autoplay, no unapproved prices, no health promises. Source-only checks are not screen-reader, actual browser, WCAG AA, mobile, Lighthouse or live payment QA.

Keep original homepage PR #49, art Issue #150, Mind hub PR #172, Dispatch #174, conversion Issue #820 and current Jetpack welcome message unchanged. **DO NOT publish or merge this branch, write WordPress CMS, alter production navigation, publish emails/posts, spend, change analytics, enable affiliate links or treat clicks as paid conversions.**
