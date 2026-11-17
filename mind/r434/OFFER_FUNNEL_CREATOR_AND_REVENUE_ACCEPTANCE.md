# R434 | Offer → Funnel → Evidence and experiment acceptance docket

**Scope:** Mind & Perception only. Draft PR, no paid link, no CMS publish, no extra list or analytics script. **Commercial release = HARD HOLD.**

## First decision: no authenticated payable Mind offer

The seller's public Inspire3 affiliate portal and unrelated consumer promotional email do not establish a Final Vestige publisher relationship. Named acceptance, SKU authorization, allowed WEB and EMAIL channels, issued link, terms, price, refund contract and settlement have not been authenticated. There is also no authenticated FV-owned payable/deliverable Mind SKU with rights and refund/delivery proof. **No live commercial CTA, guaranteed return or revenue claim is permissible.** The existing FREE 52-page Focus Fieldbook remains a useful lead pathway but not a paid sale.

## Prioritized owner contract

| Offer | Funnel step | Blocker | Proposed change/test | Actual proof in this sprint | Owner |
|---|---|---|---|---|---|
| Zen12 | Approved affiliate offer → paid merchant conversion | FV named partner acceptance, permitted SKU/web/email channels, issued URL | Reconcile partner account with seller's exact referred order and refunds; disable unless fully verified | Public catalog and sale page checked; account-specific approval NOT AUTHENTICATED | Founder / Commerce |
| FV-owned Mind digital | Checkout → delivered paid order | No demonstrated rights-cleared, deliverable paid Mind SKU | Verify seller legal entity, item ID, checkout, delivery and refund process | No qualifying SKU verified; HOLD | Founder / Claude |
| Zen12 A/B | Guide → completed paid conversion | No payable checkout; B film unencoded | A text-only vs B same substantive copy + original optional 42s film, random assignment ONLY after consent and QA | Static HTML and VTT built; no real-user exposure | Mind / Site QA |
| Existing Fieldbook | Article → confirmed lead | Jetpack delivery and confirmation not tested | Reuse single existing /focus/ landing; validate confirmation/dedup via provider | Live public offer verified, provider conversions UNKNOWN | Claude / Dispatch |
| Grok assets | Qualified session → matching live article | No matched real media IDs or rights verification | Independently authenticate 3 existing videos and correct destination | Candidate links grounded; actual media IDs UNKNOWN | Praxxis / Grok |
| Merchant sales | Verified payout → realized net revenue | No settlement, fees, refunds, qualified human denominator | Reconcile merchant order IDs into anonymized cohorts | NOT COMPUTABLE | Commerce / Claude |

## Three truthful prospective creator-topic pathways (NOT confirmed published matches)

1. **Door-swap / change blindness** → existing **LIVE** https://finalvestige.com/2026/11/02/change-blindness/ → optional current https://finalvestige.com/focus/ → potential **held** Zen12 buyer guide. Asset ID, actual hook, post URL/date, rights, mobile destination and UTM: **UNMATCHED** pending Praxxis verification.
2. **Franklin 1784 blinded magnetism test** → existing **LIVE** https://finalvestige.com/2026/11/02/mesmerism/ → Puységur primary archive → Focus Fieldbook → optional **held** product evaluation. Media evidence: **UNMATCHED**.
3. **Puységur consent and documentary failures** → existing **LIVE** https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ → source dossier → optional free Fieldbook → **no merchant claim** unless relevant and independently approved. Media evidence: **UNMATCHED**.

**Do not** redirect social to the new unpublished chronostasis manuscript or pretend unrelated history clips are a match. Grok owns writing, rendering and posting; Praxxis independently checks existing assets through TASK-008; this lane only supplies source/hook/article/offering evidence.

## Measurement contract — no new scripts without Claude review

First-party, permission-compliant event schema only for potential integration with existing analytics:
- `qualified_landing`: cohort_date_utc; landing_slug; published_asset_id/utm_campaign when authenticated; coarse source; consent_state; bot_qualified yes/no per documented method; no IP/email/device fingerprints.
- `focus_cta_click`: only actual user activation to existing `/focus/`, not verified lead.
- `focus_confirmed_lead`: only provider-confirmed opt-in, deduplicated; no email address in analytics.
- `affiliate_click`: real disclosed, user-initiated approved outgoing earning link event; not transaction or commission. Zero while gate held.
- `affiliate_paid_order`: merchant-reported unique order reference in restricted reconciliation, de-identified public aggregate; account for cancellation/refunds/fees.
- `owned_paid_order`: payment processor-confirmed settled order; inventory rights and fulfillment verified.
- `net_realized_revenue` = actual settled commissions + owned-product receipts − refunds − transaction fees − chargebacks; currency and dates aligned.

**KPI:** `1000 * net_realized_revenue / qualified_human_sessions` for both 7-day and 30-day attribution windows. If either term absent, output **NOT COMPUTABLE**, not zero. Also report paid conversion rate, confirmed customers, gross/net, confirmed lead-to-order ratio. Warn for tiny sample sizes. Do not infer purchase from an outbound link.

## A/B decision design

**Population:** Qualified, consent-aware adult visits to one eventually approved landing route; bots excluded by documented nonintrusive criteria; no fingerprinting. **Variants:** A and B differ only by optional 42s original film, fully playable after separate QA, with same source/offer/disclosure/CTA, mobile markup and no forced playback. The complete transcript always appears via native `details`, and no-JS supplies the whole buyer guide. No third-party iframe. Lazy-load video only after user requests playback. If B is not encoded, do not call it a video test. Assignment and inference need Claude's existing tooling; do not install another service or bypass consent.

**Primary outcome:** Independently reconciled net revenue/1,000 qualified sessions. Secondary: paid order rate and verified lead-to-customer. Diagnostics only: mobile exits, video plays, CTR, pageviews. Freeze hypothesis and sample interpretation before seeing results; do not declare a winner from a handful of clicks. Test 360/390/768/1440/1920 layouts, keyboard, focus visibility, reduced motion, CSP, captions, script-off and Core Web Vitals.

## Affiliate block conditions

When and only when all required gates pass, display near the actual earning link: **“If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.”** No merchant outbound checkout href currently exists in either variant. No click-cloaking, misleading urgency, unsafe guarantees, testimonials of personal use or exact affiliate commission claims.

## Source and release trail

- GitHub issue #171 (Mind) and #820 (revenue/attribution): source of truth; #818 business charter; #174 Dispatch owns newsletter.
- FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
- Seller https://inspire3.com/ , https://zen12.com/about , https://zen12.com/secret/ , https://hypnosislive.com/mental-skills/total-focus , https://brainwaveshots.com/focus-shot .
- Existing live article https://finalvestige.com/2026/11/02/change-blindness/ , Mesmerism https://finalvestige.com/2026/11/02/mesmerism/ , Puységur https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ , Focus https://finalvestige.com/focus/ .
