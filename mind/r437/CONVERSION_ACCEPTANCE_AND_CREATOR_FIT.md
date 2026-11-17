# R437 — Mind/Perception conversion acceptance, creator fit, release risk

**Status:** Unpublished source-control pilot / all affiliate and publication activation on HARD HOLD (2026-11-16 PT).  
**Owner lane:** Mind/Perception editorial, merchant claim review and presell acceptance.  
**Out of lane:** Grok content creation/posting; Praxxis Grok QA and Drive queue ownership; Claude site production and analytics; Dispatch email/newsletter drafting and Jetpack flows; homepage flagship PR #49, Issue #150 and existing Mind PR #172.

## What the visitor is choosing

**Intended high-intent user:** an adult already considering a twelve-minute guided/ambient meditation recording, who wants a practical routine and is skeptical of large "instant brain change" promises. They need clear package content, free alternatives, expected limitations and credible payment/refund details—not a forced lead gate or invented neuroscience.

**Candidate paid offer:** Zen12 full-course MP3 program **only if** Final Vestige partner eligibility, exact SKU approval, approved web/social/email channels, issued referral URL, current referred checkout and refund policy and actual settlement reporting are authenticated. Official seller content: https://zen12.com/about and exact seller order presentation https://zen12.com/secret/ . This is **not** an active affiliate offer for Final Vestige now. A separate public page https://zen12.com/ shows multiple tiers and different promotional prices; therefore no price or coupon appears in the draft. The official page's 1-year guarantee statement is a *seller representation*, not independently confirmed checkout rights. Do not endorse urgency countdowns.

**Fallback near-term owned offer:** the existing 52-page Focus Fieldbook at https://finalvestige.com/focus/ is *free* with the existing Dispatch list. It can achieve a provider-confirmed qualified lead, **not** a paid order. No genuinely payable, rights-cleared, currently deliverable FV-owned Mind SKU was authenticated; do not invent one. Ask commerce owner for actual owned-product checkout URL, license, SKU, receipts and returns before proposing a paid pilot.

**What this pilot tests:** whether an original optional 42-second movie placed before the exact same buyer content improves **merchant-confirmed net paid conversion** relative to a text-only guide. The creative idea is a hypothesis, not a conversion claim. At present the film is an original vector poster + six-scene script + VTT concept, not an encoded video.

## Source- and intent-grounded three-video crosswalk — research-only, no Grok task creation

| Candidate audience question / factual hook | Sources | Exact landing content | Secondary first-party action | Optional paid offer | Immutable video ID |
|---|---|---|---|---|---|
| "Why does a face look normal upside down but wrong upright?" | Thompson 1980 https://doi.org/10.1068/p090483 ; Wong 2010 https://doi.org/10.1068/p6659 | **NEW UNPUBLISHED** R437 Thatcher investigation; only an approved published canonical route may be promoted | Existing https://finalvestige.com/focus/ or https://finalvestige.com/dispatch/ without duplicates | Zen12 guide for genuinely interested audio shoppers; no link while HOLD | **UNMATCHED** |
| "How could someone fail to notice a stranger swapped mid-conversation?" | Simons & Levin 1998 https://doi.org/10.3758/BF03208840 | **ALREADY LIVE** https://finalvestige.com/2026/11/02/change-blindness/ ; do not publish competing R436 canonical | Existing Fieldbook only if relevant | Zen12 guide not an experimental intervention; optional | **UNMATCHED** |
| "Could a witnessed hypnosis episode prove an invisible force?" | Actual Puységur cases https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | **ALREADY LIVE** complete archive, with ethical failure/consent evidence | Existing Fieldbook/Dispatch if reader wants free practice | Hypnosis Live separate guide only with SKU-specific evidence and approval; no link | **UNMATCHED** |

**Required Praxxis/Grok task check:** verify ONE ALREADY POSTED and relevant exact social asset_id per topic, actual post URL/date/hook, accurate rights and mobile-permitted destination, not just "a video somewhere on YouTube." Until found leave all UNMATCHED. Do not modify Grok TASK-008 production queue, schedule, content, uploads or attribution tags. Prior research-only request exists; do not create a duplicate creator assignment.

## A/B preregistration — video B is a controlled experiment only after activation

**Variants:** A is evidence-led text guide. B has precisely the same buyer paragraphs and CTA/disclosure language, with one **optional** original 42-second non-autoplay media element before the identical content. An encoding must provide <video controls preload="none"> with real caption track (default for accessible use), accessible poster alt/prose and nearby transcript; low bitrate, locally hosted, responsive, keyboard/focus, no motion requirement to comprehend content, gracefully omitted on no-JS. Current B is a storyboard, **not playable**.

**Primary outcome:** net realized revenue per 1,000 *qualified human sessions*, 7- and 30-day cohorts. A qualified session must be bot-filtered through a documented consistent rule, privacy-appropriate, with channel/asset_id/utm_campaign appropriately collected. The revenue numerator only includes independently merchant-reported settled paid orders/commissions that can be reconciled to this campaign *minus* refunded amounts, merchant/processing fees and variable transaction costs. If a merchant only reports aggregate commissions without reliable attribution, show "unattributed" separately; don't credit a specific video.

**Secondary diagnostic observations:** visible variant assignment, landing views, presell CTA clicks and (if consent permits/observable) existing Jetpack confirmed new leads. An outbound click **is not** a confirmed lead, initiated checkout, order or commission. Gross sale is not realized net. If merchant transaction IDs are unavailable, net revenue metric is NOT COMPUTABLE rather than 0 dollars by inference. Never use an ad/affiliate link as the study's only source of "conversion."

**Pre-treatment allocation:** Claude may allocate A or B 50:50 server-side, persist a short non-PII variant token only under applicable consent/retention rules, without a new third-party analytics vendor. Count variant assignment only once per qualified session. Avoid session stitching across devices without consent. Campaign asset IDs are creator-assigned, fixed, nonpersonal identifiers; do not put names, emails, IPs, user IDs or raw social handles in UTM or link parameters.

**Decision threshold:** Set sample requirements with a power calculation *before* launch based on realistic baseline rates. Do not declare a winner because B gets 3 clicks against A's 1. Report counts, confidence intervals, acquisition mix and bot filtering. If video playback slows LCP or prevents accessible use, B fails irrespective of apparent clicks. Do not extend/look repeatedly and selectively stop at a favorable transient.

**Non-negotiable acceptance:** rights-cleared video + actual browser WCAG 2.2 AA keyboard/touch/screen-reader/reduced-motion/no-JS checks at 360/390/768/1440/1920; web vitals measured (LCP/CLS/INP), no unnecessary external requests, CSP/HTML sanitization, XSS and open-redirect review; affiliate disclosure same visible context as earning link; refund terms verified at referred checkout; partner permission for all routes. QD independent signoff and founder publication/commercial approval.

## Minimal, privacy-safe attribution contract — design, NOT deployed

| Event | Permitted minimal fields | Server-side conditions | What it proves |
|---|---|---|---|
| `qualified_landing` | stable non-PII `asset_id`, allowlisted `utm_campaign`, approved page id, experiment variant, day cohort | dedupe by anonymous ephemeral consented session token; bot filters; no IP persisted in analytic row | qualified human visit, not lead/sale |
| `focus_cta` | same campaign/page/variant plus CTA id `focus` | event fires on first-party click only; do not create second Jetpack list | click to the existing free resource, not confirmed email |
| `confirmed_lead` | provider-approved aggregate confirmation count + permitted cohort tag | **only** Jetpack-authoritative opt-in confirmation/delivery evidence; aggregate if cross-system join not authorized | new confirmed lead, not buyer |
| `affiliate_click` | approved product/placement/variant/asset campaign metadata, no personal values | fire only after merchant URL approval, disclosure rendered, explicit outbound click | merchant outbound click, not purchase |
| `merchant_paid_order` | merchant statement's non-PII order reference, currency, gross, fee, refund, net and attribution confidence | only authenticated merchant report; no inferred sale from traffic or checkout events | independently reported paid sale/commission |
| `settled_net` | reconciled net in currency and report date, attribution confidence | subtract returns, fees, chargebacks, unsettled amounts and avoid duplicates | realized net revenue attributable where provable |

Do not add duplicate measurement scripts. Claude owns implementation; Mind owns schema acceptance. UTM keys: `utm_source` (allowlisted platform), `utm_medium=social`, `utm_campaign` (approved campaign id), `asset_id` (verified immutable creator asset), and optional `variant` only if safe and consented. Reject unexpected or untrusted parameters, never echo them unsanitized into HTML. Avoid visitor fingerprinting. Observe opt-out and retention controls. Provide no attribution claim when missing.

Formula for a single cohort:

`net_revenue_per_1000 = 1000 * attributable_refund_adjusted_settled_net / qualified_human_sessions`

If denominator missing/zero, transaction data missing, or currency/settlement inconsistent: output **NOT COMPUTABLE**; don't silently substitute zero. Show revenue attributable fraction and unknown separately. A verified zero requires a verified complete reporting period and zero orders/settlement, not lack of access.

## Prioritized commercial blockers — OFFER → STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Priority | Offer → step | Evidence blocker | Next isolated change or test | Status | Responsible owner |
|---|---|---|---|---|---|
| P0 | Zen12 → actual paid commission | No FV-named publisher approval, specific channel rights, issued earning URL, settlement | Independently authenticate authorized account + exact SKU and referred checkout; only then request commercial release | **HOLD** | Founder / Commerce |
| P0 | FV-owned Mind → paid purchase | No authenticated payable rights-cleared SKU | Authenticate checkout, ownership, deliverability, refund terms, test receipt | **HOLD** | Founder / Claude |
| P1 | Zen12 guide → prospective paid offer | Price conflicts and contextual policy terms across official entry pages | Time-stamped referred checkout and return-policy QA; no discount countdown in copy | **HOLD** | Commerce / Site QA |
| P1 | A/B → accessibility and buyer trust | Video not encoded; browser and mobile audits unrun | Encode rights-cleared 42s film; run A/B diff, captions and WCAG plus CWV | **HOLD** | Mind / QA |
| P1 | existing Focus → confirmed lead | No Jetpack authoritative confirmation/delivery test in this run | Claude provider-confirmation test, no second signup/list | **HOLD** | Claude / Dispatch |
| P2 | social asset → qualified audience | No three verified immutable Grok IDs matching proposed pages | Praxxis read-only verify actual posted assets, rights, mobile UTM and topic match | **UNMATCHED** | Praxxis / Grok |
| P2 | reporting → realized net /1000 | No merchant-reconciled orders or qualified sessions | Instrument approved server attribution once, reconcile refunds and fees over 7/30 days | **NOT COMPUTABLE** | Claude / Commerce |

## Commercial permission research and hard bounds

Public Inspire3 https://inspire3.com/ and public program access are not evidence that this publisher is approved. The 2026-11-16 Gmail searches for Inspire3/Zen12 affiliate publisher notices and Final Vestige affiliate acceptance produced no identifiable publisher authorization, issuing link, or program statement. Consumer promotional emails are NOT merchant acceptance. The official product pages must be consulted again at activation time; price, return terms, copy and SKU composition can differ by entry URL.

FTC endorsements https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking requires a conspicuous earning disclosure near recommendation/link. FTC claims guidance https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance requires adequate substantiation for objective health/mental/benefit claims; research on meditation *in general* is not enough to say Zen12 achieves the same result. Nothing in the R437 investigation demonstrates product efficacy.

## Protected scope & approval

All artifacts are **draft PR only**, under `mind/r437/`. No WordPress CMS/navigation/settings writes, affiliate redirects, merchant activation, Dispatch draft editing, Jetpack alterations, Grok uploads, homepage changes, merges, deployment, paid services, or purchases. The author of the historical investigation does not control the production site or social accounts. A draft PR is not a green release and a static regex check is not real browser QA.
