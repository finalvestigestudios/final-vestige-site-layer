# Mind R361 — Conversion acceptance, owner decisions and creator topic fit

**Status:** Unpublished / research prototype / HARD HOLD, Nov 13, 2026 PT. This document is NOT a deployment instruction or publisher approval.

## Commercial finding to act on first

1. Inspire3's **public** publisher site exists, but no authenticated Final Vestige-specific accepted publisher account, exact earning URL, approval for website/social/email placement, creative usage rights, payout/refund terms or merchant attribution join could be substantiated. Targeted connected Gmail searches for affiliate-account approval and transaction terms produced no matching evidence; two unrelated historical marketing emails mentioning “approved” were not partner acceptance. The public publisher site's generic commission advertisement must **not** be treated as FV's rate or earnings. **Owner: Founder / Commerce.**
2. No currently sellable, rights-cleared, *Mind-related* FV Payhip SKU with its checkout, actual delivered file, tax/price and return policy was authenticated. **Owner: Commerce.** This is a missing proof, NOT a claim no such product exists.
3. The near-term permitted action is a useful free fact-checked Mind article and the existing 52-page Focus Fieldbook, without any new email form. No payable CTA can be activated today. Article readership and Focus signup are lower-funnel indicators, not substitutes for paid commerce.

## Creator-topic → evidence → offer-fit matrix

| Intended Grok source and asset ID | Actual article | Reader intent | Existing free route | Conditional merchant fit | Status |
|---|---|---|---|---|---|
| Change Blindness creator clip, ID **UNVERIFIED** | Published [Change Blindness](https://finalvestige.com/2026/11/02/change-blindness/) | Explain the door swap and visual limits | Existing [Focus Fieldbook](https://finalvestige.com/focus/) | Zen12 Premium only as optional structured audio guide, after enrollment and claims review | VIDEO→LANDING NOT VERIFIED |
| Attentional Blink creator clip, ID **UNVERIFIED** | Unpublished [Mind R356 manuscript](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2395) | Understand a missed second target | Existing Focus | Zen12 possible; NO leap from meditation trials to a 12-minute commercial recording | NO PUBLIC ARTICLE ROUTE |
| Puységur / Suggestion creator clip, ID **UNVERIFIED** | Published [Mesmerism](https://finalvestige.com/2026/11/02/mesmerism/) and [Puységur source archive](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) | Check extraordinary historical claims | Existing Focus / Dispatch | Hypnosis Live Total Focus only in separately evaluated guide after authorization | VIDEO→LANDING NOT VERIFIED |

**Handoff:** Grok owns videos and social posting; Praxxis independently authenticates each immutable real asset ID, publish date/time, platform URL, CTA placement and authorized click path via existing Drive TASK-008. Do not assign today's new documents as a production task, overwrite Grok's queue, or claim a social video exists merely because the investigation does.

## One high-intent offer and controlled experiment

**Audience:** Adult visitor who searched “Zen12 Premium review” or arrived from a real, relevant attention demonstration and wants a practical decision about buying structured meditation audio. Exclude clinical-treatment intent (diagnosis or cure). **Offer:** Zen12 Premium, but **HOLD** until partner eligibility and checkout are authenticated. **Fallback:** an FV-owned Mind product only if Commerce can establish a rights-cleared live deliverable with actual priced checkout and fulfillment. In the meantime offer the existing free Focus Fieldbook; it is not paid revenue.

**Variant A** is a standalone buyer guide with merchant-described contents, objections, a free demonstration, close disclosure and disabled purchase button.

**Variant B** contains the identical buyer guide plus an ORIGINAL 42-second visual storyboard and complete transcript/caption treatment. It adds no autoplay, no active third-party embed, no JavaScript, no tracking call. Future real media must use user-triggered HTML5 controls with captions, poster, `preload="none"`, verified accessibility and performance. Current B is NOT playable or a completed video.

**Hypothesis, untested:** when merchant authorization and checkout are satisfied, the film version may reduce uncertainty about what a paid listening routine entails. It may also create friction or decrease conversion. Do NOT claim superiority from CTR or time on page.

**A/B acceptance:** stable random per-human assignment using Claude's existing privacy-safe analytics/experimentation infrastructure if available and approved, identical copy and merchant offer, equal placement, same disclosure and eligibility. Until measured, label A/B as design review only. Compare independently verified paid orders per unique qualified human and refund/fee-adjusted net revenue per 1,000; report 7-day and 30-day cohorts with confidence intervals and tiny-sample warnings. If no stable consenting assignment exists, run a sequential observational comparison clearly labeled **noncausal**, or defer.

## Attribution contract without new trackers

Reuse **existing approved first-party tracking**, not a second script, pixel, cookie, client fingerprint or payment webhook. Proposed campaign fields, subject to engineering review:
- `utm_source=tiktok|youtube|instagram` as applicable, `utm_medium=organic_social`, `utm_campaign=mind_attention_pilot_2026_11`, `utm_content=<actual_immutable_asset_id>`. A real media ID is not presently available; never publish example brackets as a valid production link.
- Qualified human session: server/provider-backed filtering and opted-in privacy protections; no email, name, raw IP, device fingerprint, browser uniqueness tokens or unapproved PII in dashboard.
- Events must stay distinct: `landing_view`, `offer_cta_click`, `focus_signup_started`, `focus_lead_confirmed` **only with provider proof**, `affiliate_click` (outbound, not commission), `paid_order_confirmed` / `affiliate_commission_settled` **only with merchant proof**, `refund`, `fee`.
- If purchase-level attribution is prohibited or impossible under partner terms, report aggregate merchant earnings separately; do **not** invent an attributed video, conversion or lead join.
- Count orders only after independent payment status and deduplicate by merchant-provided opaque transaction reference in authorized restricted back office. Do not commit IDs/secret tokens to GitHub.
- `net_revenue_per_1000=1000*(settled_gross_refund_adjusted - merchant_fees - payment_fees - other_attributable_costs)/qualified_human_sessions`. If numerator, denominator or purchase attribution is unknown, report **NOT COMPUTABLE**. A qualified-human session is not simply a pageview.

## Priority owner ledger: OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL EVIDENCE → OWNER

| Priority | Offer → step | Blocker | Experiment / change | Current evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → actual commission | FV approval and issued authorized tracked link missing | Privately inspect account and documented website/social/email permissions; record opaque proof reference only | **HOLD**: public signup ≠ approval; no links | Founder/Commerce |
| P0 | FV owned Mind → paid order | Active SKU rights, actual checkout/delivery/refund missing | Read-only SKU inventory/fulfillment audit before choosing fallback | **HOLD**: no authenticated sellable matching SKU | Commerce |
| P1 | Grok → article | Real published IDs, channels, permissible links and mobile landing paths missing | Via Praxxis TASK-008 reconcile three actual assets, dates and final destinations | **NOT VERIFIED** | Praxxis/Grok |
| P1 | Article → free confirmed lead | Provider-backed consent and campaign joins untested | QA existing Jetpack form and confirmation/welcome, no duplicates | **NOT TESTED** | Claude/Dispatch |
| P1 | Buyer guide A/B → paid order | Merchant/film/browser/site QA not released | Staging at 360/390/768/1440/1920; keyboard and screenreader; headers/CSP, no-JS and sanitizer; no publish | **DESIGN BUILT, LIVE NOT TESTED** | Site QA/Claude |
| P0 | Paid purchase → net revenue | No settled merchant records, refunds/fees, qualified humans | Reconcile 7/30-day cohorts from authorized reports, privacy-safe | **NOT COMPUTABLE** | Commerce/Claude |

## UX, a11y and security release checks

- Native `disabled` attribute; NOT an active clickable link concealed behind a CSS disabled class. Disclosure must be in the same offer block immediately before any future active link.
- Source links to published article/FTC/research are permissible. No active merchant `href` is present.
- A/B body copy identical; film is the only deliberate contrast; poster description is available to nonvisual users.
- No JS, webfonts, third-party embeds, scripts, forms, autoplay, auto redirects, tracking pixels, fake countdown, fictitious testimonial or trust badges.
- Native closed captions and visible controls required before film is implemented. A transcript is not proof a video exists. Real browser WCAG AA, WP sanitizer and performance remain unexecuted.
- Founder approval still required for any live publishing, navigation, email, social or merchant activation.

## Reviewed public materials

- https://inspire3.com/ ; https://affiliates.inspire3.com/ ; https://zen12.com/ ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot
- https://doi.org/10.1080/00207144.2024.2434085 ; https://doi.org/10.1016/j.concog.2024.103730
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- https://finalvestige.com/focus/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- [Business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171).

No live CMS, one-list Jetpack, founder flagship homepage, canonical /mind/ PR #172, agent Issue #150, newsletter Issue #174, social producer queue, analytics deployment, payment or spending was touched.
