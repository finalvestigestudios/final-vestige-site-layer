# R164 — One-offer conversion audit, creator fit, release gates and controlled test
**Status:** UNPUBLISHED / no production tracking / no affiliate links / no checkout claims  
**Date:** 2026-11-06 PT · **Accountable lane:** FV Mind & Affiliate · **Business charter:** [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) · **Editorial source of truth:** [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171)

## Decision: do not activate a sale CTA yet

**Primary possible offer:** Zen12 Premium, intended to serve an already-motivated visitor searching whether a short, varied meditation-audio library is worth buying. The actual official seller page is https://zen12.com/?no-popup=1 (reviewed Nov 6). It lists 12 levels/48 MP3s, four listening styles, an $87.99 *displayed* Premium price and a seller-described one-year money-back guarantee. Checkout total, tax, refund processing and any discount eligibility remain unknown. The separate promotional route https://zen12.com/secret/ MUST NOT be conflated with the standard offer, and does not establish a coupon available to FV referrals.

The seller claims extraordinary results from twelve-minute sessions. FV has no independent product-specific proof of the claimed equivalence to an hour of meditation, automatic brainwave control, treatment of anxiety or sustained focus gains. We can describe what the customer may buy, not assert those results. The research-backed article on choice blindness also cannot be marshaled as support for Zen12 efficacy.

**Eligibility:** Public Inspire3 program is visible at https://affiliates.inspire3.com/, but a named authorization for Final Vestige, approved destination link, tracking parameters, permitted channels, creatives or commission/settlement reporting is NOT VERIFIED. Gmail search on Nov 6 found promotional/marketing correspondence, not acceptance proof; it cannot exclude acceptance in an authenticated dashboard. Hard hold for affiliate commerce. Any authorized link must be inserted only after product/terms and publisher identity are verified and founder release approval is documented.

**Owned alternative:** FV has some Payhip business operations historically, but authenticated inventory does not establish an *actually sellable, rights-cleared Mind-related SKU*. Do not claim a Mind checkout exists. Owner Commerce must return SKU permalink, title, price, currency, ownership/rights, preview, fulfillment, taxes, buyer-access test, written refund terms and settlement evidence. Until then, no owned paid alternative is approved for this pilot.

## High-intent audience and matching offer
Visitor: 'I want a short, structured meditation-audio program; I am comparing Zen12 Premium against free guided sessions or ordinary meditation apps and need to know exactly what I would receive and whether the benefits are proven.'

This segment has substantially better offer fit than a general invisible-gorilla or choice-blindness viewer. An evidence archive must **not** hide sales behind the result of a perceptual experiment. A first-party free resource and public product comparison are optional choices; no subscription gate to read journalism and no forced upsell after the Focus fieldbook.

### Creator topic → article → existing free asset → prospective offer fit

| Creator topic idea (Grok owns actual asset and hook) | Source and accurate proposition | Destination and existing status | Next action | Offer fit |
| --- | --- | --- | --- | --- |
| 'The photo you never chose—why did you explain it?' | Johansson et al. 2005 [PubMed](https://pubmed.ncbi.nlm.nih.gov/16210542/); sometimes unnoticed outcome substitutions; not mind control | R164 choice-blindness article **UNPUBLISHED**; no public link | **DO NOT** send traffic until approved publication and media-ID reconciliation; then optional existing /focus/ | **LOW** for Zen12 buying; lead with investigation only |
| 'The person changed—what did you miss?' | FV [Change Blindness](https://finalvestige.com/2026/11/02/change-blindness/) **historically reported LIVE**; independently verify site/accessibility and original sourcing | Existing published article → an editorially unobtrusive /focus/ body link *only after approved site work* | Praxxis/Grok reconcile actual immutable media ID and allowed caption/pinned/profile links | **LOW–MEDIUM**; recommend free fieldbook, no direct paid nudge |
| 'The magnetic sleep archive: what do we know?' | FV [Puységur Animal Magnetism Files](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) **historically reported LIVE**; historical testimony ≠ modern therapeutic efficacy | Existing page → /focus/ optional, plus separate self-hypnosis methodological review | Praxxis/Grok reconcile actual immutable posted asset IDs | **MEDIUM** for a *disclosed independent hypnosis guide*, not a scientific endorsement |
| 'Zen12 Premium review: 48 MP3s, but what does the research prove?' | Exact [Zen12 product](https://zen12.com/?no-popup=1); distinguish merchant features from scientific evidence; do not copy sales pitch | R164 Zen12 independent offer guide **UNPUBLISHED** | Only after named approval, site QA, creator-topic fit and release approval | **HIGH** commercial search intent; proposed A/B landing pilot |

No actual Grok media IDs, upload timestamps, platform CTA permissions or exact published hooks were independently verified in the available TASK-008 document. Do not fabricate them, change Grok scripts or assign publishing work.

## Contextual link/navigation proposal (NO CMS writes)

1. Existing article-body Change Blindness page: after source/limitations, add a small 'Practice noticing what you miss' editorial link to /focus/. No banner, offer or new signup form; site QA tests link accessibility before Claude's authorized release.
2. Existing Puységur archival page: add 'What suggestion research can and cannot show' research-path link to a later published /mind/ guide **only when the destination is genuinely live**; otherwise no dead-link addition. An optional /focus/ link after archival conclusions can provide a useful free next action.
3. Canonical /mind/ hub remains in existing draft PR #172; do not overwrite or create a second WordPress hub. Propose R164 article under Perception & Attention, buyer preview only under Tools Under Review. No changes to menus without homepage art owner and founder approval.
4. The direct search-intent Zen12 guide may link back to the real official research, independent evidence and /focus/, but cannot imply the scientific studies tested the product.

## Conversion contract — commercial outcomes first

Events MUST remain logically distinct:
- `qualified_human_session`: first-party aggregate, excludes known bots/spiders and internal QA traffic using documented classification, with campaign keys; absence of bot filter proof = denominator UNKNOWN.
- `offer_view`: view of a relevant, approved product-information module, not proof of purchase intent.
- `focus_cta_click`: click to the existing /focus/ page, not a confirmed subscriber.
- `focus_lead_confirmed`: subscribed via **existing** Jetpack consent path and independently confirmed by permitted Jetpack record or delivery test; don't create new list identifiers.
- `affiliate_click`: outbound affiliate click only after named approval; do not create an event before an authorized link exists.
- `merchant_paid_order_confirmed`: authoritative Payhip/merchant sale, after payment confirmation; no reliance on WordPress JS click as a sale.
- `affiliate_commission_confirmed`: partner-reported eligible purchase/commission if contract grants reporting. Separate from click, pending balance and settlement.
- `refund_or_chargeback`, `fees`, `settlement`: authoritative dollar accounting, not estimates of what a click could earn.

**Privacy:** Allowed campaign fields: fixed `utm_source`, `utm_medium=organic_social`, `utm_campaign`, `utm_content=<immutable_platform_asset_id>`, `landing_slug`, `offer_id`, `variant`, *aggregated* counts. Never put email, IP, person ID, a device fingerprint, user-agent log, personal search term or account identifier into UTMs. Do not add a new pixel, cookie, third-party tracker or duplicate analytics script. Claude decides whether already approved first-party collection can produce these aggregate counts with appropriate consent. Campaign source may be obscured by social platform bio-link patterns; state as unattributable, not guessed.

**Primary KPI** when denominator and settlement both verified: `1000 × (settled_gross_receipts − refunds − chargebacks − processor_fees − partner_reversals − directly attributable campaign costs) / qualified_human_sessions`. Affiliate commissions included only when actually earned, merchant reported and settled according to records. For a merchant-owned product, use net revenue actually attributable to FV, not the customer's gross basket total. Report **NOT COMPUTABLE**, not zero, if denominator or source-of-truth money absent.

Seven-day and thirty-day publication/landing cohorts. Support with confirmed paid orders, attributed paid-order rate, buyer count, gross/net amounts and lead-to-paid rate only when both records can legitimately be joined without breaching consent. For tiny cohorts show absolute counts, confidence intervals if method permits and warning; don't imply a winner from a handful of purchases. Do not call email signups 'sales', or treat repeated page reloads as unique humans.

## Predeclared pilot A/B hypothesis — NOT RUN

**Hypothesis:** For high-intent Zen12 Premium search visitors, the exact same independent buyer guide **plus optional, original 40-second evidence explainer** (B) may raise the **merchant-confirmed purchase conversion rate** versus the text-only guide (A) without harming accessibility, mobile performance or trust. This is testable, not presumed.

- **A:** research-first article, same seller-description facts, sourcing, free alternative, objections, same FTC disclosure and commercial CTA position, text-only, no video placeholder.
- **B:** identical content, with one user-initiated video after evidence summary; no autoplay, preload metadata/none until user action, poster, captions, full transcript and reduced-motion-aware presentation. No external video iframe or third-party cookies. The B video must add an explanatory example, not an emotive endorsement.
- **Randomization:** session-stable assignment only after Claude security/consent review, sticky across internal steps within allowed first-party instrumentation, no PII. Use one approved campaign/variant mapping and exclude internal test traffic; no fingerprinting.
- **Primary outcome:** merchant-confirmed **attributable paid purchases per qualified human session**; interim CTA and lead events are funnel diagnostics. **Secondary:** refund-adjusted net revenue/1k qualified humans, proportion of leads reaching authenticated purchase, mobile content loading, voluntary video starts/completions if consent and tracking permit; avoid measuring playback with a new SDK.
- **Safety guardrails:** no deceptive copy, no off-site CTA without approval, no email form duplication, disclosure immediately beside earning link, equal offer price/product, same traffic intent, no change to Grok posting without founder authorization, WCAG 2.2 AA 360/390/768/1440/1920, keyboard/reader and no-JS parity. Stop if variant unexpectedly routes a paid offer without FTC disclosure or causes broken Focus enrollment.
- **Decision threshold:** Pre-register minimum sample and statistical approach with Growth/Commerce before launch. Until legitimate paid merchant outcomes and meaningful counts are available, do NOT designate a winning variant; report only feasibility/a11y/performance and intervals. An optional video is NOT by itself a conversion accomplishment.
- **Video status:** storyboard/poster/transcript **BUILT**; original MP4 and synchronized WebVTT **NOT BUILT**; browser/video testing **NOT TESTED**; test allocation **NOT RUN**; campaign and affiliate **NOT LIVE**.

## OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER

| Priority | Offer and funnel step | Blocker | Change / experiment | Actual acceptance evidence | Owner |
|---|---|---|---|---|---|
| 1 | Zen12 → paid affiliate commission | named approval, approved URL, product-specific terms unverified | founder authenticates partner dashboard and saves a nonsecret approval summary; Mind re-checks exact seller page, FTC and channel rights | **HARD HOLD**, public portal insufficient | Founder + Mind |
| 1A | FV-owned Mind SKU → paid Payhip order | inventory, rights, pricing, delivery unverified | Commerce authenticates SKU with checkout/fulfillment/refund evidence; only then consider pilot instead | **UNKNOWN**, no authenticated SKU | Commerce |
| 2 | Existing article → Focus | reported absence of direct in-body /focus/ link; live route needs fresh authenticated QA | Claude stages scoped article link; Site QA checks keyboard mobile CTA, founder approves release | **UNRELEASED**, no CMS modifications here | Claude + QA |
| 2 | Focus → subscriber | Jetpack anonymous opt-in and welcome not recently independently tested | QA tests existing consent/form and Dispatch welcome only in authorized process, no new list | **UNVERIFIED** | QA + Dispatch |
| 3 | Grok media → article → paid cohort | immutable posted asset IDs and destination attribution unavailable | Praxxis reconciles TASK-008 with Grok; Claude maps approved UTMs | **PENDING**, do not fabricate | Praxxis + Grok |
| 4 | Zen12 text vs video | merchant approval + original playable asset + browser QA absent | hold A/B until all gates pass; then run controlled approved test | **NOT RUN**, source-level only | Mind + Claude + QA + Founder |
| 5 | Paid order → settled net | no authoritative order/commission/refund/fees or qualified denominator | direct merchant-first reconciliation by 7/30d | **NOT COMPUTABLE**, not zero | Commerce + Growth |

## Coordination boundaries

This lane owns exact-offer presell, sources, claims, disclosure, disabled design, research and experimental acceptance plan. **Grok owns social creative/distribution**; Praxxis QA independently; **Dispatch Issue #174** owns newsletter drafts; **Claude** owns production analytics, WordPress engineering, Jetpack reliability and checkout journey; **Site QA Issue #126** audits a11y and links; **Issue #150 / flagship PR #49** and **canonical Mind hub PR #172** are untouched. Preserve existing Focus welcome and single Jetpack funnel. Founder authorizes publishing, paid acquisition, partner activation, payment tests and deployments.

## Verification limitations and next evidence

Source checks: 2005 Science, 2010 Cognition, 2012/2013 PLOS articles; current Inspire3 and exact Zen12 official pages; FTC guidance. New article/presell/matrix are source-controlled **BUILT**; source-level lint checks can be executed independently. Browser, screen-reader, actual WordPress, merchant payment, partner acceptance, opt-in delivery, and paid conversion remain **NOT VERIFIED**. This sprint deliberately makes no production CMS, social, email, analytics, affiliate, or merchant writes.
