# R486 — Offer → funnel → revenue acceptance and creator-topic fit

**Date:** 18 November 2026 PT · **Scope:** Mind & Perception ONLY · **Release:** source-only draft · **No checkout, merchant URL, email, CMS or live measurement activation**

## Decision-first summary

The commercially decisive next action is *not* another finished-looking sales page. It is to authenticate a payable offer. The last direct, account-related Refersion email observed in the targeted connected Gmail search is dated **24 August 2026**, subject **“Your affiliate account is pending.”** It explicitly says approval would trigger a later welcome email. The search did not establish a later named Final Vestige acceptance, issued referral URL, permitted website/email use, official commission schedule or merchant settlement. A Gmail search is not the partner dashboard. Thus partner status is **NOT VERIFIED APPROVED**, not a declaration that the partner permanently refused the application. Any approved link and offer terms must come from authenticated merchant records.

The publicly available Zen12 standard page advertises multiple bundles. Its separate /secret page uses a coupon and countdown. These are different commercial surfaces and no legitimate FV-specific earning offer has been authenticated. The source-only presell guide intentionally contains **no click-through merchant sales link**, only human-readable reference to the source pages and the free FV Focus route.

The existing 52-page Seven Day Focus Fieldbook is free with the current Jetpack/Dispatch subscriber flow. It is not an authenticated paid product. The founder-charter mentions owned Products 001–015 and Payhip, but this run did not establish a currently sellable, rights-cleared, accurately priced, fulfillable Mind SKU. Never invent one. Request a read-only product inventory from the product owner before changing direction to a paid owned-item pilot. A new hypothetical paid Mind product is **not** a near-term validated sale.

## Offer-first acceptance table

| Offer → funnel step | Actual blocker | Change/experiment in this PR | PASS/FAIL/UNKNOWN | Owner |
| --- | --- | --- | --- | --- |
| Zen12 → eligible purchase | Account acceptance, eligible bundle, earning URL and allowed web/email rights absent | Hold merchant links; record exact standard vs promotional offer | HOLD: no release evidence | Founder / Commerce |
| Owned Mind product → paid sale | Payable SKU, rights, live checkout, refund terms and fulfillment not independently evidenced | Demand exact product inventory, not an invented presell | UNKNOWN: source of truth missing | Founder / Claude |
| Social asset → qualified visit | Exact real Grok asset IDs, campaign paths and landing routes missing | Three-topic creator/source crosswalk below | DESIGN ONLY | Praxxis / Grok |
| Editorial article → free optional lead | Existing confirmed Jetpack signup and delivery need QA | Reuse /focus/; no form, extra CRM or welcome edit | EXISTING LIVE ROUTE; delivery UNTESTED | Dispatch / Claude |
| Independent buyer guide → checkout | No partner permission or activated link | A full text-only page vs same buyer text + optional 42s film concept | STATIC DRAFT; browser test PENDING | Mind / Site QA |
| Paid order → realized net | No merchant transaction, settled commission, fees, refunds or cohort denominator in scope | Event schema and exact reconciliation rules below | NOT COMPUTABLE | Commerce / Claude |

## Three creator topics and buyer-fit, without stealing Grok's lane

| Grok-owned topic and factual hook for consideration | Evidence/editorial landing | Next reader choice | Optional honest offer and fit constraint | Real Grok post ID |
| --- | --- | --- | --- | --- |
| **Change blindness:** “Could the person giving you directions change in front of you?” Explain the original door-study limitations, not a diagnostic label | LIVE: https://finalvestige.com/2026/11/02/change-blindness/ | Free /focus/ as general attention/reflection resource | Zen12 format guide *only if* a future article transition explains why a twelve-minute audio routine is relevant; study does NOT prove efficacy | UNKNOWN — obtain from Grok |
| **White bear:** “Why checking whether you thought of something can keep bringing it back.” Give 1987 task and 2020 caveat; avoid intrusive-thought medical framing | DRAFT: mind/r486/THE_WHITE_BEAR_THAT_WOULD_NOT_LEAVE.md; **no public URL** | Free /focus/ with neutral journal/timer, not therapy | Zen12 *optional* format-only guide after approval; commercial offer is not part of scientific conclusion | UNKNOWN — obtain from Grok |
| **Puységur:** “A notarized claim can verify that someone said something—without proving the magnetic mechanism.” Show specific archive evidence and consent limits | LIVE: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Evidence archive and optionally /focus/ | Hypnosis Live guide is conditional; no inference that historical magnetism demonstrates contemporary self-hypnosis benefits. Exact SKU/checkout must be reviewed first | UNKNOWN — obtain from Grok |

**Coordination:** Praxxis/Grok TASK-008 https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit . Supply these **research only**, ask Grok for its actual titles, media URLs, asset_id, intended public landing and whether a link is possible on each platform. No scripting/posting, no queue overwrites and no invented published IDs. This workstream owns editorial presell/evidence; Claude owns website instrumentation; Dispatch Issue #174 owns newsletter content and existing welcome.

## One offer journey, only after authorization

Reader sees creator-led sourced short → opens one accurate article or archive page → optionally reads free Focus Fieldbook (and may subscribe using existing Jetpack only) → independently reads product-format guide → encounters a clearly explained optional paid seller offer with **immediately adjacent** disclosure → visits an authorized unmodified merchant URL → optionally buys → the merchant independently records order, fees/refunds and settled commission. No step can be assumed because the preceding one happened.

**Plain disclosure near any future earning link:** “If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.” On the current static draft, replace “through this link” with explicit *prospective* language since there is no active link. Disclose before the action, not solely in site footer. If a future video endorses a product, place necessary disclosures in the media itself as well as accompanying copy according to context.

## Existing first-party measurement contract; no new script in this PR

Use Claude's approved existing analytics/WordPress/Jetpack infrastructure where its observability is demonstrably real. Do **not** add new GA4, pixel, cookies, browser fingerprinting, third-party scripts, or UTM redirects. Public UTM example for creator approval: `utm_source=youtube&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=ACTUAL_GROK_ASSET_ID` (literal placeholder **must not** ship). Apply standard tags only where each platform permits functional links; never assume TikTok captions are clickable.

Definitions (all with lawful consent and no unnecessary PII):

- `campaign_landing`: first-party qualified-human landing event, source and content asset if observed; **not a purchase**.
- `offer_guide_view`: real rendered guide view, variant assignment A/B if independently verified; **not an endorsement**.
- `article_to_resource_click`: observed click from a sourced article to the free Focus landing route; **not a confirmed lead**.
- `confirmed_signup`: independently recorded accepted/confirmed Jetpack subscription, with deduplication and consent; **not an order**.
- `affiliate_click`: outbound click on verified authorized partner URL after release; **not a paid conversion**. Must remain zero/unavailable preapproval; do not label an old generic seller-source citation as an affiliate click.
- `merchant_confirmed_purchase`: paid order confirmed by source-of-truth merchant, reconciled order identity without exposing customer PII.
- `settled_affiliate_commission`: independently reported affiliate payout amount actually settled and attributable, adjusted for cancellations/returns, separate from prospective commission.
- `net_revenue`: realized gross receipts/settled commission **minus attributable refunds, fees and chargebacks**, with provenance and currency documented. If absent → *not computable*, not zero.

**North-star KPI:** `1,000 × (realized_net_revenue / qualified_human_sessions)`. Only calculate with both compatible 7-day or 30-day cohort numerator and denominator, and attribute uncertainty and tiny n. Also report merchant-confirmed purchases, paid conversion, confirmed lead rate, lead→customer rate (only linked with permitted data), gross/net and refunded counts. If downstream merchant reporting lacks matched attribution, keep separate totals with an explicit “unattributed” bucket and never infer per-asset conversion. Never infer buyers or revenue from YouTube views, Jetpack pageviews, email signups, CTA clicks or stale coupons.

## Hypothesis and fair A/B acceptance

**Hypothesis, not a claim:** For readers who have already decided to evaluate a listening format, an original optional 42-second visual explanation may improve comprehension or verified paid purchase outcomes relative to an otherwise identical text guide. The experiment could just as plausibly be neutral or worse. The no-video version must remain fully useful.

Variant A = substantive evidence guide only. Variant B = **exact same buyer core** plus illustrated, captioned, transcript-backed film that does not autoplay or load any third-party assets until the reader explicitly chooses. Here the B film is only original storyboard/caption **concept**, not encoded or hosted. Do not run a visitor test or claim a winner until:
1. Approved payee, offer, checkout and rights permit an actual purchase.
2. Original final 30–45s encoded video, poster, caption file and full transcript are hosted without performance regressions; document exact media size and rights.
3. QA passes 360/390/768/1440/1920 px, zoom 200%, keyboard, assistive technology, high contrast, reduced motion, no-JS, captions, pause/control, consent and WordPress sanitization.
4. Existing privacy-compliant first-party assignment/exposure instrumentation is verified; same attribution coverage and outcome definition across both arms.
5. Analysis is pre-registered against confirmed net-revenue paid conversions; at tiny samples, report raw counts and wide uncertainty, no false significance. Disclose attribution gaps and confounders such as platform mix.

No experiment is live, no human has been randomized by this branch, and no product purchase or video conversion has been verified.

## Security/privacy audit and release ownership

Static pages contain **zero JavaScript, zero form controls for data collection, zero external scripts, no merchant shopping href, no URL redirect, a genuinely native-disabled CTA, and no autoplay**. Film variant includes only an inline original SVG poster and readable transcript; no image tracking. The optional VTT is a media-production concept. Existing first-party free Focus link and editorial/source guidance remain available without JS.

**Before any WordPress draft import:** inspect scoped CSS sanitization and responsive overflow; check all external source links, accessible focus outlines and captions; retest on staging. Unapproved source-only HTML MUST NOT be copied to public CMS/navigation. Preserve #49, #150, canonical Mind #172, and existing Jetpack welcome unchanged. Publish/merge/email/affiliate activation/spend require founder and owner approvals.

**Commercial release hold is intentional.** This branch is a real evidence/UX proposal; it is not a merchant acceptance, traffic improvement, sale, net-revenue metric, published WordPress draft or A/B result.

### Reference inventory

- [Mind issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818); [conversion issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
- Official seller catalog https://inspire3.com/ ; ordinary offer https://zen12.com/ and https://zen12.com/about ; separate promotional surface https://zen12.com/secret/ . **Sources only**, not FV earning destinations.
- FTC endorsements https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; FTC health-products substantiation https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
- Wegner 1987 https://pubmed.ncbi.nlm.nih.gov/3612492/ ; 2020 meta-analysis https://doi.org/10.1177/1745691619898795 ; 1993 non-replication https://doi.org/10.2466/pr0.1993.72.3.867 .
