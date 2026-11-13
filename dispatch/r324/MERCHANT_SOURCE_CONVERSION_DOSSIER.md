# R324 | Product-specific source alignment, delivery and conversion decision
Date: 2026-11-12 PT / authenticated WordPress read 2026-11-13 07:40 UTC. Classification: **research and offline review, not a campaign release**.

## Why this edition instead of another generic copy pass
Original #05 described the entire Hypnosis Live catalog and asked three generic questions. This alternative selects one coherent audience and ONE exact seller listing: **Total Focus**, for people who wish to evaluate a guided attention recording against their already available free Fieldbook routine. Its subject/preheader accurately describe that subject, and its CTA is a clearly gated first-party buyer guide (not the merchant checkout). It avoids generic guarantees and false evidence of use. No unapproved pricing, referral URL or seller testimonial is adopted.

## Independent source / claim matrix
| Claim | Origin / direct URL | Status | Can appear in email? |
|---|---|---|---|
| Franklin commissioners examined animal magnetism and tested expectation/blindfolded subjects in 1784 | 1785 English report: https://www.gutenberg.org/files/78413/78413-h/78413-h.htm ; FV summary https://finalvestige.com/2026/11/02/mesmerism/ | Primary historical source plus secondary site summary | YES with scope limit: was not testing modern audio |
| Total Focus is a single seller-listed hypnosis MP3, 33 minutes, 47 MB, recorded by J. A. Amos | https://hypnosislive.com/mental-skills/total-focus | Seller-reported format/credits; NOT product use or purchaser proof | YES attributed |
| Seller markets "100% razor-sharp concentration", rewiring, inbox speed, work recognition | https://hypnosislive.com/mental-skills/total-focus | Advertising assertions; independent product-specific efficacy NOT established | Only as attributed, questioned claims; NOT as promises |
| NCCIH has studied hypnosis for conditions including pain, IBS and some anxiety; evidentiary limits vary | https://www.nccih.nih.gov/health/hypnosis | Government research overview. Does not establish Total Focus outcomes. | YES with limitation |
| A 14-day satisfaction/refund claim appears on seller listing | https://hypnosislive.com/mental-skills/total-focus | Seller-stated; written policy and current checkout NOT authenticated | Only attributed, with verify-terms caution |
| Public sales-page displayed prices and bundle variants | https://hypnosislive.com/mental-skills/total-focus | Context-dependent: page inspected 2026-11-12 PT displayed single-session $24.44 and a bundle promotion; a separately indexed older crawl displayed $17.95. Checkout NOT verified. | NO prices in email |
| Inspire3 publisher acceptance, exact earning URL, email channel permissions, approved creative rights, commission/refund accounting | https://affiliates.inspire3.com/ | Public recruitment page does not prove Final Vestige's specific account permissions. No authenticated account proof in this sprint. | NOT VERIFIED, merchant CTA HOLD |
| FTC commercial primary purpose, valid publisher mailing address and functional opt-out | https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business | Legal compliance guidance, not proof of newsletter template | Must validate final received message before release |

## Current real WordPress read-only configuration
Existing Jetpack enabled and site send-capable. Auto new-post emails **OFF**, full content, welcome message contains existing Fieldbook URL, `reply_to=no-reply`, sender "Final Vestige Studios". Subscriber counters: total 3, confirmed 3, unconfirmed 2 (overlapping); distinct eligible email recipients **unknown**. Jetpack follower source 3 WordPress.com / 0 direct-email, but this does **not** prove zero email-eligible people. Latest five post records show `never_sent_opted_out`; cannot extrapolate lifetime sends. Welcome PDF receipt and genuine rendered unsubscribe/postal footer are **unverified**.

No subscriber IDs or addresses collected or exposed. No live signup attempts or emails made.

## Business-defined conversion chain
Grok asset_id/utm_campaign (verified actual publication only) → qualified first-party human session → relevant /focus/ or /dispatch/ visit → consented provider-confirmed signup (WordPress user immediate activation or email-link completion; dedupe existing subscribers) → Dispatch edition → first-party guide CTA → independently reported settled affiliate sale → deduct refunds, reversals and fees → realized net revenue. Do **not** credit clicks, merchant's own opt-ins, form attempts, Fieldbook downloads or attributed UTM alone as revenue. `net_revenue_per_1000_qualified_sessions = 1000 * (settled_receipts - refunds - reversals - fees) / qualified_human_sessions`, only when both sides authenticated; otherwise **NOT COMPUTABLE**. Use 7/30-day cohorts when real evidence exists; no A/B inference at list size three.

## Offer → step → blocker → change → pass/fail → owner
| Offer / step | Blocker | Change | Evidence | Owner |
|---|---|---|---|---|
| Total Focus → buyer guide | Seller email permission + issued earning link + product-specific pre-sell unavailable | Exact-product honest alternative, inactive CTA, source checks | Built / QA-only, NOT LIVE | Dispatch / Mind-Commerce |
| Zen12 → first-party guide | Same merchant permission, distinct product tiers and merchant opt-in | Keep original #03 HOLD and prior #2308 separate | HOLD | Mind-Commerce |
| Focus → confirmed subscriber | Provider transition/eligibility and true welcome receipt missing | Use two-path confirmed-signup contract from #2302, no fake download event | NOT VERIFIED | Claude / Focus |
| Dispatch → inbox | Verified physical FV address, native unsubscribe, final in-client rendering absent | Obtain authorized native received email / sender identity proof | NOT VERIFIED | Founder / Dispatch |
| Grok → qualified traffic | No authenticated asset/session join | Source-tag convention after Claude's existing instrumentation only | NOT VERIFIED | Grok/Praxxis / Claude |
| Settled purchase → net revenue | No merchant settlement/refund records | Read-only independent accounting report | NOT COMPUTABLE | Commerce |

**Gate policy:** `HOLD_UNSENT` for every original issue; `HOLD_MERCHANT` for #03 and #05; this candidate `NOT_ADOPTED`. PR is review only. Production engineering remains Claude's; Grok owns content distribution; Mind owns presell and eligibility; homepage #49 remains untouched.
