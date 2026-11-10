# R265 Conversion Acceptance / Owner Handoff — DRAFT, NOT LIVE

**Decision:** Zen12 remains the *intended* primary Mind affiliate candidate, not an authorized sellable FV offer. Named approval, issued earning link, approved social/email channels, current seller cart/returns and payout evidence are missing. Gmail narrow search on 2026-11-10 returned historical promotional emails rather than named publisher acceptance; absence in that search does not prove rejection. No rights-cleared, currently sellable FV-owned paid Mind SKU, Payhip fulfillment and refunds was authenticated in this sprint. **Do not activate commerce on either hypothesis.**

## Offer → Funnel step → blocker → change / experiment → pass/fail → owner

| Offer | Step | Blocker | Experiment/change | Evidence threshold | Owner |
|---|---|---|---|---|---|
| Zen12 Premium | affiliate activation | No named approval, issued URL, channel or tracking agreement | Request documentary partner acceptance, permitted landing/campaign terms, exact allowed offer; no URL until verified | FAIL/HARD HOLD; authenticated account documents required | Founder + Mind |
| Zen12 | buyer decision | Seller standard and coupon propositions differ; current cart/return fulfillment unchecked | Compare actual allowable offer, seller receipt and delivery against historical descriptions | HOLD; merchant checkout proof and refund policy version needed | Mind + Merchant |
| FV-owned Mind SKU | first paid order | Rights, live SKU, price, taxes, merchant fulfillment and refund policy not authenticated | Inspect existing authenticated Payhip dashboard and rights ledger, then use only eligible item | UNKNOWN; no qualifying item confirmed | Commerce |
| Change blindness -> article | qualified visitor | Grok asset_id, actual platform URL and mobile tag unknown | Verify already-published asset only, don't issue content brief | PENDING documented public URL/rights/hook + signed-out mobile proof | Praxxis/Grok |
| Invisible gorilla -> article | landing | R264 article unmerged/unpublished | Hold any live destination claim until published/reviewed | NOT LIVE | Mind + Editorial |
| Attentional blink -> article | landing | R263 manuscript unmerged/unpublished | No fake canonical URL | NOT LIVE | Mind + Editorial |
| Any topic -> existing Focus | confirmed opt-in | Query-triggered gift UI is not Jetpack-provider evidence | Accept only provider-confirmed opt-ins after explicit consent; do not submit test PII | UNVERIFIED | Claude + Dispatch |
| Guide A vs B | verified purchase | Partner clearance and staged real video/accessibility QA absent | A text guide vs B same guide with optional 42-second native video only after approved asset hosting; keep no-JS captions and poster | NOT TESTED in production; compare **merchant-confirmed paid order rate**, refunds and net rev; outbound clicks secondary | Mind + QA + Founder |
| Paid order or affiliate settlement | revenue | Merchant receipts, fees, refunds and 7/30-day qualified-session denominator missing | Reconcile independently reported settled orders using lawful aggregate cohorts | NOT COMPUTABLE; don't report zero | Commerce |

## Experimental hypothesis and guardrails

**Audience:** already interested in choosing guided meditation audio after watching a factual Mind clip. **One offer:** Zen12 Premium only if partner authorization clears; otherwise existing free Fieldbook is an educational continuation, *not* a paid-conversion substitute. **A/B:** text-only sourced offer guide vs identical guide plus truly optional original 42s film. Randomize only on founder-approved hosted staging/production with a privacy-safe permitted experiment; do not introduce new analytics libraries. Primary outcome: settled attributable paid conversion and realized **net revenue per 1,000 qualified-human sessions**. Secondary: confirmed consented leads; diagnostics: guide-to-CTA, affiliate_outbound, session duration. 7 and 30 day cohorts, denominators and tiny-sample confidence flags compulsory. No conclusion on uplift until independently measured outcomes; do not confuse clicks and purchases.

## Privacy-safe attribution contract

Use pre-existing first-party analytics if present, not a new script. Accept only standard allowlisted UTM parameters (`utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=authenticated_asset_id`); do not send email, IP, browser fingerprint, precise person-level ID or unconsented cross-site identifiers. Explicitly distinguish: `qualified_campaign_landing` (human-classified where defensible), `resource_click`, `confirmed_signup` (Jetpack provider receipt, not gift UI), `affiliate_outbound`, `merchant_confirmed_order`, `merchant_cleared_commission`, `refund`, `fees`. A partner click is not a sale. Net revenue = settled recognized proceeds − refunds − merchant/platform fees − attributable campaign costs, with policy on costs documented. Denominator cohort = qualified human sessions with documented exclusions; absent trustworthy sessions or paid order matching, result **NOT COMPUTABLE**. No made-up or negative zero.

## Navigation plan

Keep homepage PR #49 and art lead Issue #150 untouched. Canonical Mind hub PR #172 untouched. Subject to future release approval: existing Explore/Library -> /mind/ -> four sections; perception articles link to each other and to original experiments; historically oriented path links Puységur; practice path links existing /focus/; optional tools path links independent buyer guide, then near-link FTC disclosure and authenticated approved earning URL only. Existing /dispatch/ and Jetpack welcome message preserved. No seventh legacy tile added. At 360/390/768/1440/1920 widths require actual browser proofs, keyboard/touch, focus indicator, contrast, no-JS, reduced-motion, safe external link and WordPress sanitizer checks. Current source preview is **not** a CMS draft.

## Creator fit matrix — research-only, no queue or publishing changes

| Candidate existing clip | Underlying evidence | Landing | Resource | Commercial fit |
|---|---|---|---|---|
| Change blindness | Simons/Levin door study; verify exact original media citation before use | Existing https://finalvestige.com/2026/11/02/change-blindness/ | Existing /focus/ | Zen12 only a separate, cautious optional practice guide; weak direct product-specific connection |
| Invisible gorilla | Drew et al 2013 radiology expert inattentional blindness https://pubmed.ncbi.nlm.nih.gov/23863753/ | R264 manuscript UNPUBLISHED, no canonical URL | /focus/ | Weak buyer intent; do not force offer |
| Attentional blink | Raymond et al 1992 https://pubmed.ncbi.nlm.nih.gov/1500880/ | R263 manuscript UNPUBLISHED, no canonical URL | /focus/ | Weak buyer intent; make research path first |

Ask Praxxis to crosscheck already-published Grok assets and provide media_id/date/rights/original caption/mobile destination **or NO MATCH**. Do not create or post any asset, modify Grok queue, edit Dispatch issue drafts, mail subscribers, change WP, spend or merge.

## Evidence reviewed and blockers

- Official catalog https://inspire3.com/; standard https://zen12.com/?no-popup=1 vs promo https://zen12.com/secret/ are **seller**, not publisher permissions.
- FTC endorsement https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and health claims https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance.
- Original science https://pubmed.ncbi.nlm.nih.gov/21442007/ and https://pubmed.ncbi.nlm.nih.gov/23620547/.
- Source-of-truth Issues #171, #820, #818; Dispatch #174; site QA #126; homepage #150.
- Source-generated prototypes are unmerged, unpublished. The earlier R257 locally rendered silent video exists but remains unhosted. No native Node full-checkout, real-browser QA, WP sanitizer QA, actual partner transaction or production UTM verification has been performed for R265.

**Release: HARD HOLD. Founder retains all production, posting, spending and commercial release approvals.**
