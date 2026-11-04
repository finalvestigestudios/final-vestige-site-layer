# R127 — Conversion-First Offer Eligibility, Creator Fit, Measurement and Release Contract
**2026-11-04 | Unpublished / source-controlled | Issues #171, #820, #818; protected PR #49, PR #172, Issue #150**

## Decision: do not create another commercial funnel before one eligible offer exists

**Offer candidate:** Zen12 Premium, strictly as a structured audio-library option for an adult who is ALREADY comparing meditation-audio purchases. Seller page reviewed: https://zen12.com/hnp . The seller's catalog https://inspire3.com/ describes the product family. Secondary conditional seller presentation https://zen12.com/secret/ contains a lower coupon-qualified price and countdown: **do not reuse that price, countdown or pressure language**. Actual permitted merchant destination and final checkout terms remain UNKNOWN. Eligibility is **NOT ESTABLISHED** for Final Vestige. No authorized referral links in this branch.

**Why this audience?** It expresses a format-specific purchasing problem: “I want a repeatable, short session and an organized downloadable collection; which program is transparent about what's included?” Its answer can be evaluated by descriptions, accessibility, compatibility, honest limitations and the individual's format preferences. The free twelve-minute preference check provides immediate value without claiming outcomes. An illusion viewer watching a gorilla disappear is not automatically a paying meditation customer.

**What is truly sellable today?** Earlier WordPress and business records establish an existing free 52-page Focus Fieldbook and public FV paid digital-product initiative, but there is no authenticated Payhip listing, final checkout, refund/fee record, rights ledger or fulfillment proof of one currently purchasable **Mind** SKU available to this lane. Do NOT replace missing merchant evidence with promotional emails, public links that may no longer function, or claims that absence of search results proves absence of products. Payhip audit belongs to Commerce/Claude using authorized account access and must supply a stable SKU, exact live price/terms, rights clearance, tested download, and actual paid settlement record.

**Partner verification:** the public affiliate portal https://affiliates.inspire3.com/ proves program existence, not Final Vestige acceptance. An internal Gmail query on November 4 for Inspire3/Zen12/HypnosisLive affiliate approval/tracking yielded unrelated promotional material and no qualifying approval document; the search is limited, not conclusive. Obtain written authorization specifying account identity, exact offer and link, allowed social/WP/email channels, attribution window, payout, refund handling, prohibited claims, traffic restrictions, and privacy/data processing terms. Inspire3's published https://inspire3.com/privacy/ contemplates sharing customer details with affiliates. Require a workable **aggregate-only** settlement/reporting feed or approved minimization process rather than importing customer names/emails.

## Three creator topics → public article → free/direct audience → potential later offer

| Proposed research topic / creator hook (NOT an assignment) | Existing public destination (previous WordPress verification, recheck before release) | Useful reader action | Legitimate product fit | Attribution requirement |
| --- | --- | --- | --- | --- |
| Change blindness: “What changed while you looked?” | https://finalvestige.com/2026/11/02/change-blindness/ | Read experiment, optional https://finalvestige.com/focus/ | **LOW** direct Zen12 intent; do NOT force offer | Grok real platform post URL, immutable asset_id, CTA/bio-link location, UTM verification |
| Mesmerism & Puységur: “Did suggestion require a magnetic fluid?” | https://finalvestige.com/2026/11/02/mesmerism/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Source trail, optional Focus resource | **LOW–MEDIUM** history-to-buyer, separate research from commercial hypotheses | Grok real media ID + rights + published source video URL |
| Attentional blink/white bear: “Why did the second number vanish?” / “Can you avoid a white bear?” | R123 attentional-blink and R127 white-bear manuscripts **DRAFT, NOT PUBLIC**; no public article destination | Do not post a dead CTA; use a currently verified live article or Focus if topic fits | **MEDIUM only for declared listening-routine buyers**; never infer from illusion interest | Grok confirms actual existing video, and Claude approves URL before use |

This is a **mapping proposal for Praxxis/Grok TASK-008**. It does not assert any video exists, assign a production asset, fabricate a publish date or modify Grok's queue. Only Grok/Praxxis can reconcile actual media IDs and platform permissions. No spoken commercial CTA by this lane.

## Internal navigation: additive plan only

- Proposed /mind/ hub (canonical source-controlled PR #172) → four independent lanes: perception experiments; history of suggestion; free reflection resources; clearly labeled tools under review. Never sneak commerce into evidence conclusions.
- From live Change Blindness/Mesmerism/Puységur → related evidence → optional existing Focus route. Plain-language link text describing the content, not generic “click here.” The new unpublished white-bear article would link to verified Puységur, Mesmerism and the free Focus route **after release**.
- From /mind/ “Tools Under Review” → independent Zen12 buyer guide **only once founder-approved public page exists**. Contextual affiliate disclosure adjacent to exact earning link, not footnote-only. Preserve homepage PR #49, existing Focus welcome and one Jetpack subscriber list.
- Do not treat a WordPress custom HTML block mockup as a live WordPress page, and do not insert unverified offer URLs in navigation.

## Offer → funnel → blocker → change/experiment → pass/fail evidence → owner

1. **Zen12 / eligibility →** missing named partner acceptance & tracking → written merchant qualification → **FAIL / evidence missing** → founder/Mind. Stop at inactive CTA, do not route shoppers to unapproved offer.
2. **FV product / paid checkout →** no authenticated rights-cleared Payhip Mind SKU → commerce export and manual authorized checkout QA → **UNVERIFIED** → Commerce/Claude; fallback only after records show one sellable item.
3. **Grok content / landing →** unknown immutable media IDs and platform bio-link constraints → Praxxis reconcile TASK-008 per published asset; Claude validates actual page → **UNVERIFIED** → Grok/Praxxis/Claude.
4. **Article / Focus signup →** historical signup function exists but no asset-level confirmed lead linkage → site QA tests one native Jetpack Focus path without duplicate forms → **NOT ATTRIBUTED** → Site QA/Dispatch.
5. **Buyer guide / offer CTA →** no approved live buy destination, A/B film is not playable → test text and optional original film in isolated staging; hold merchant link → **STATIC DESIGN ONLY** → Mind/Site QA.
6. **Merchant settlement / revenue →** no verified paid orders, reversals, fees, or qualified-human sessions → request approved aggregate partner/Payhip settlement summary → **NOT COMPUTABLE** → Commerce/Growth.

## Measurement schema and integrity controls — SPEC ONLY

No new script in this branch. Prefer Claude's **existing first-party/native analytics** if they can record events without PII or duplication. Every published Grok asset should have immutable `asset_id`, real `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<actual asset_id>`, and exact landing URL. Use this format only where the platform's link placement is allowed, and document bio-link attribution loss.

A proposed privacy-minimal aggregate event row has `event_type` in `campaign_landing`, `article_to_resource_click`, `confirmed_focus_signup` (only if authoritative), `offer_guide_view`, `affiliate_outbound_click`, `verified_checkout_start` (only if independently observable), `merchant_confirmed_paid_conversion` and `merchant_refund_or_reversal`. Noncommercial events and confirmed paid sales are **different facts**. Suggested dimensions: `event_date_utc`, `asset_id` (allowlisted Grok token only), `utm_campaign`, `route`, `variant=A|B`, and `source_system`. Exclude name, email, IP, user ID, session cookie, device fingerprint, individual cart contents and raw referrer query strings. Never attach buyer email to an affiliate click. Require appropriate consent where applicable.

Session qualification is an explicit engineering/QA rule—not “all pageviews.” Exclude internal QA, known bots, duplicate visits by the same privacy-safe session under an agreed bounded deduplication policy; report how many were excluded, and treat uncertain bot filtering as **unknown**, not precise. If robust qualified human sessions cannot be established without disproportionate tracking, report a bracketed sensitivity analysis and mark the primary KPI provisional.

**Financial reconciliation:** trusted seller order count (paid/settled only) × actual amount collected = gross; subtract refunds/chargebacks, merchant/processor fees and other directly attributable variable costs. For affiliate revenue use actual **approved and paid** commissions net of reversals, not estimated retail item value. Deduplicate via merchant-controlled aggregate identifiers, not imported purchaser PII; refuse to merge incompatible merchant records. Report 7- and 30-day cohorts with denominators, open refund windows, cohort maturity and confidence warnings. **Primary:** realized net revenue per 1,000 qualified human sessions. **Support:** settled paid conversion rate, unique verified customers only where privacy-safe source can support it, lead-to-paid where opt-in/merchant linkage is authorized. A $0 observed in an authenticated full ledger is not the same as an UNKNOWN ledger.

## Prespecified A/B hypothesis

A: accessible text-only independent guide. B: **same** product descriptions, objections, free preference exercise, CTA position, disclosure and no sales pressure, plus original *optional* 40-second educational film about monitoring a thought. No video autoplay; static poster and full readable transcript in no-JS path; optional MP4/WebM only if later produced from rights-cleared assets. WCAG 2.2 AA review and responsive 360, 390, 768, 1440 and 1920 checks; keyboard, focus, color contrast, captions, touch target, reduced-motion, no-JS, mobile performance and CSP. If optional film increases LCP or confuses buyers, remove it.

Random assignment only after an authorized earning link and founder release; no retroactive significance fishing. Define primary KPI as net revenue/1000 qualified sessions; secondary metrics are diagnostic only; record attribution gaps and asymmetric refund windows. With zero or tiny paid transactions, outcome = **INCONCLUSIVE**. Do not claim that storyboard placement is evidence of A/B success.

## Exact proof required for go-live

- Signed/traceable partner approval and link terms OR authenticated owned Payhip paid product/rights/checkout record.
- Exact seller offer, bundle, final current buyer price/returns and privacy treatment confirmed.
- Source and claims ledger reviewed by Mind, non-product health guarantees removed.
- Merchant CTA with nearby disclosure and normal outbound controls `rel="sponsored noopener noreferrer"` for approved external earning links only; do not cloak link; safe `target` if used.
- Real-browser QA by independent Site QA and founder/Claude release review; site nav ownership remains art lead; no changes to PR #49 or PR #172.
- Real asset IDs in TASK-008 and native analytics test proving no duplicate scripts or personal data capture.
- Authoritative settlement proof before claiming a sale.

**Current decision: COMMERCIAL HARD HOLD, EDITORIAL DRAFT READY FOR REVIEW.** Do not email, publish, merge, spend or change live CMS/Jetpack/Dispatch/TikTok/YouTube. No downstream success asserted.
