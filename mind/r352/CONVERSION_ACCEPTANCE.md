# Mind R352 — Commercial conversion acceptance, source custody and ownership

**Status:** DRAFT / HARD HOLD / NOT PUBLISHED · 2026-11-13 PT

## Decision: one high-intent offer before another channel launch

**Candidate primary affiliate:** Zen12 Premium, because a buyer actively searching for structured twelve-minute meditation audio can reasonably compare its twelve levels and 48 MP3s against a free twelve-minute baseline. No publisher-specific acceptance, issued earning link, content/channel rights, or partner-side paid conversion proof was authenticated. The public affiliate enrollment portal is only a solicitation; it is not an account-specific authorization.

**Fallback owned offer:** The existing Seven Day Focus Fieldbook is a **verified free** 52-page lead resource with existing Jetpack/Dispatch signup, not a verified paid product. Public searches and the site collection are insufficient to identify an **active paid, rights-cleared and deliverable Mind Payhip SKU**. The Commerce owner must produce the authenticated SKU, public checkout and delivery proof; no source-controlled pilot should invent a payment link.

**Business implication:** The independent Zen12 buyer guide is worth keeping review-ready but the shortest path to revenue is an authenticated paid product/affiliate offer, not another unverified landing-page variant. Missing approvals are blockers, not "zero conversions."

## Offer → funnel → blocker → change/experiment → evidence → owner

| Priority | Offer / step | Blocker | Controlled change or next experiment | Evidence status | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Zen12 Premium → eligible paid commission | FV-specific account acceptance, channel approval, earning URL, commission/attribution/refund and payout terms absent | Read private partner dashboard with authorized identity, confirm exact Zen12 product, channel, link format, disclosures, creative restrictions, retention and settlement | HOLD / not authenticated | Founder + Commerce |
| P0 | Rights-cleared owned Mind SKU → actual paid checkout | Public inventory doesn't authenticate live SKU, price, rights, checkout/delivery | Commerce reconciles SKU against actual store, copyright licenses, receipt, tax/fees, fulfillment and refunds without real purchase or live mutation | UNKNOWN / no eligible pay-to-buy CTA | Commerce |
| P1 | Verified Grok asset → matching source page | No real immutable published media ID and permitted placement verified for selected creative | Praxxis reconcile TASK-008; Grok retains posting/creative ownership; publisher is not contacted through this lane | HOLD / media IDs pending | Praxxis + Grok |
| P1 | Mind article → Focus lead | Existing Jetpack lead confirmation attribution not proven | QA existing /focus/ and /dispatch/ welcome and confirmation, preserve list, do not send tests to real recipients without approval | PARTLY OBSERVABLE; no attributed lead | Claude + Dispatch |
| P1 | Buyer guide A/B → paid order | No permitted merchant CTA and hosted playable 42-second film | Controlled text-only A vs same buyer-copy + optional original short B. Both functional without JS; compare paid orders only after launch gates; don't present poster as playable movie | BUILD / not an executed A/B | Mind + Site QA + Claude |
| P1 | Merchant order → realized net per 1k | No paid merchant orders/refunds/fees/qualified sessions | Obtain privacy-safe 7/30-day cohort reports; source-confirmed paid orders and settled affiliate payouts only | NOT COMPUTABLE | Commerce + Claude |

## Three creator-topic-to-product fit paths (research-only; no Grok production action)

| Proposed Grok topic (not a verified published asset) | Existing article / source destination | User value | Current offer route | Fit and risk |
| --- | --- | --- | --- | --- |
| Change Blindness: the difference that vanished | https://finalvestige.com/2026/11/02/change-blindness/ | Explain the experimental blind spot, not diagnose viewers | Optional /focus/ · paid audio only if separately chosen later | High editorial fit / LOW merchant intent; do not force an upsell |
| Mesmerism: Franklin's blindfolded apricot-tree test | https://finalvestige.com/2026/11/02/mesmerism/ → https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Examine original records, expectation and consent | /focus/ for independent practice; source-controlled commercial guide only as distinct further reading | High source fit / LOW paid intent |
| Brainwave audio: can twelve minutes replace an hour? | R352 *unpublished* article WHEN_A_SOUND_PROMISES_FOCUS.md, **not a live URL** | Critically compare the specific seller package to conflicting research and free baseline | /focus/ then independent Zen12 Premium pilot if authorization verified | HIGH research/buyer fit; highest conversion hypothesis, but route and links HOLD |

For any actual creator asset: Grok/Praxxis must provide `platform`, immutable `asset_id`, true post URL, publication timestamp, media permissions, permitted link placement, actual destination, and asset-specific landing UTM. Do not fabricate them. Use `utm_source=<actual-platform>`, `utm_medium=organic_social`, `utm_campaign=mind_audio_evidence_202611`, `utm_content=<actual-asset-id>` with controlled character whitelist and no PII. No spoken script commerce CTA. Do not overwrite TASK-008.

## Internal links and navigation (approval-only concept)

- From existing published Change Blindness / Mesmerism source notes to future `/mind/` as a small "Continue the evidence" link **only after route is live and owner approves**.
- From `/mind/` hero to two genuinely live sources and published Focus Fieldbook; Mind article R352 is clearly marked unpublished; don't link to a fictitious live permalink.
- From source article to Focus resource as an optional next step. Buyer guide is separated into a "Tools Under Review" section; **not the conclusion of the investigation**.
- Future approved Zen12 direct CTA requires an immediately adjacent commission disclosure on desktop and narrow mobile, active only after all gates. No email wall before a product guide.
- No WordPress navigation edits, homepage PR #49 changes, canonical hub PR #172 overwrites, Issue #150 edits or Dispatch #174 content changes in this workstream.

## Revenue measurement contract

1. Capture first-party qualified human landing session only after appropriate consent, existing analytics mechanism and Claude's approval. Filter obvious bots and self-traffic with documented, conservative criteria; never equate all pageviews with humans.
2. Attributes: real `asset_id`, `utm_source`, `utm_campaign`, `utm_content`, destination and anonymous short-lived experiment variant. Never capture raw IP, email, health attributes, cross-site fingerprinting IDs or merchant secrets in new scripts. R352 installs **no measurement code**.
3. Record funnel stages distinctly: `qualified_session`, `article_view`, `fieldbook_cta_click`, `confirmed_lead` (Jetpack provider), `offer_view`, `affiliate_click` (approved outgoing link), `checkout_start` only if merchant actually reports it, `confirmed_paid_order` or `partner_verified_paid_conversion`, `refund`, `fee`, `settled_net_revenue`. An affiliate click is never a confirmed order.
4. Only merchant/provider-confirmed commissions or actual owned-product receipts, settled and net of fees/refunds, qualify as recognized net revenue. If sale attribution, fees or refunds are missing, represent cohort net as **NOT COMPUTABLE**; never silently use clicks or inferred conversion percentages.
5. Report separately at 7 and 30 days, with eligible qualified-human sessions as denominator, confirmed order rate, gross and net, lead-to-customer conversion where both ends are confirmed, and net revenue per 1,000 humans = `1000 * net_revenue / qualified_human_sessions`. No denominator → null, not 0.
6. A/B hypotheses: A independent text baseline vs B same substantive text plus opt-in original short. Primary success = confirmed paid conversion and net revenue per 1k humans. Secondary = confirmed lead completion (not merely submit), relevant CTA interaction and qualified return visits. Predefine duration and guard against tiny samples; no winner until merchant-level reconcilable results and confidence/uncertainty reviewed.
7. Variant assignment by approved existing server infrastructure, not a new tracker. B movie only if encoded, poster/captions/transcript checked, user-controlled play, no autoplay, no external video embeds, low page weight, reduced motion and no-JS working.

## Seller product/returns/consent evidence

- https://zen12.com/ : 13 Nov seller displayed Beginner $67.77 / 24 MP3 / first six; Premium $87.99 / 48 MP3 / all twelve; Advanced $67.77 / 24 MP3 / final six; one-year advertised guarantee. **Seller snapshot, not final checkout or enforced refund contract.**
- https://zen12.com/gift : separate seller newsletter is part of merchant gift opt-in; must not be represented as FV confirmation/lead.
- https://hypnosislive.com/mental-skills/total-focus : seller described 33-minute 47-MB MP3, $17.95 page display and fourteen-day guarantee, not authenticated checkout.
- https://brainwaveshots.com/focus-shot : seller described fifteen/thirty-minute packages, 12–18 Hz protocol and $17.99 page display with one-year guarantee; neither proves claims of hours of focus.
- https://affiliates.inspire3.com/ : signup and generic publisher marketing are not personalized agreement or issued tracking.
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance : disclosure and health-claims substantiation are separate obligations.

## QA and release

Source validator must compare A/B common buyer prose, ensure no merchant earning URL, `<script>`, `<form>`, autoplay, live media or clickable disabled CTA; inspect focus links; adjacent disclosure; SVG accessible text, VTT cues; text-only fallback and source provenance. Native browser/axe at 360/390/768/1440/1920, keyboard, contrast, touch, no-JS and WordPress sanitizer testing still required. No publish, merge, deployment, email, social post, merchant activation, or paid acquisition without founder release and QA. Record exact commit, tests and gaps in #171 and #820.