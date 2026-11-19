# R460 — Read-only Dispatch/Focus/merchant acceptance, 18 Nov 2026 PT

**Scope:** source-controlled review only; no WordPress writes, emails, test messages, merchant links, subscriber export, posting or paid services. Preserve original PR #175, safety #201, stacked ancestor #3064, four editorial/two commercial reserved positions, frozen homepage #49.

## Verified new correction to prior status reports

The live Focus page **already says**: "If that happens, copy the download link and open it in Safari or Chrome. **You do not need to sign up again.**" WordPress page ID 1579, last modified **2026-11-16T14:54:58**. The prior R458/R459 claim that the site still instructed repeat signup is **stale/inaccurate**. The copy repair is already live. Do not submit another duplicate redline for this exact statement. Do not infer confirmation deduplication itself works from this copy correction.

WordPress media-library first-party lookup by exact filename located **media ID 1737**, type **application/pdf**, recorded size **599,946 bytes**, uploaded October 29, 2026, URL:
https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf

That exact URL is present in the site's configured Jetpack welcome, and the live Focus download anchor. **This is a genuine three-way URL consistency witness** (media metadata, configured welcome and page), NOT proof of HTTP 200 from an external reader, PDF file integrity, 52 actual pages, or a received email. External web fetch of PDF produced cache miss; do not interpret that as 404 or success.

## Live WordPress 2026-11-19T01:29Z, read-only

* Newsletter enabled and provider says site_can_send=true; default automatic new-post messages OFF.
* Format **full**, sender Final Vestige Studios, reply-to no-reply. Last five notifications all never_sent_opted_out; no send authorized.
* Newsletter diagnostic **total 3 / confirmed 3 / unconfirmed 2** (unconfirmed are an additional category, not an addend). Paid 0. Stats Subscribers filter returns 3 records marked email subscribed. Separately Stats Followers returns email=0 / Reader=3 / partial=false. **Unresolved provider classification disagreement.** Do not add counts or identify individuals.
* A verified provider-confirmed transition for a genuinely new subscriber, actual final Fieldbook welcome receipt, rendered unsubscribe and founder postal address: **NOT VERIFIED**. Gmail search for the exact welcome text after October 20 returned no match, which is not proof of nondelivery.
* Live Dispatch page ID 523 promises investigation emails *when we publish them*. Focus page still says new investigations are sent when published. These **wording promises conflict with the current default-off sending state** and need founder/Claude-approved correction; do not change them here.
* Read-only WordPress remote-ability searches for newsletter/email/preview returned zero matching remote actions. No safe connected native Jetpack Preview API available through that route. **HTML in this PR is offline only.** No fake inbox screenshot.

## Merchant account source-of-truth and seller marketing, 18 Nov

* Targeted connected Gmail search for messages involving Inspire3/Refersion + approved/accepted/affiliate portal/application after Aug 1 found **one PENDING application notice, and no accepted message**. Not proof no acceptance exists in another portal; approval and EMAIL permission remain **NOT VERIFIED**. No merchant email was sent.
* Public Inspire3 affiliate landing page (https://affiliates.inspire3.com/) describes program-wide promotional payouts, but is NOT proof of FV account acceptance, individual commission entitlement, current SKU approval, email marketing rights, payout or checkout. **Do not repeat its conversion/EPC claims as FV results.**
* Zen12 ordinary seller page https://zen12.com/about describes 12-minute sessions, 12 levels and formats, and asserts one session is equivalent to an hour of meditation. The separate https://zen12.com/secret/ page shows a temporary coupon/countdown and other extraordinary claims; these are not current verified checkout terms, rights-cleared creative or independent clinical evidence. No countdown or coupon code imported into newsletter.
* Hypnosis Live FAQ https://hypnosislive.com/faq describes seller MP3 sessions and efficacy claims. Those assertions are not independently proven for a particular product. The general affiliate landing page and retailer FAQ do NOT authorize email promotion or establish Final Vestige partner privileges.
* Public Refersion help https://support.refersion.com/en/articles/4704057-signing-up-with-merchants distinguishes merchant PENDING vs an accepted welcome and portal access. Refersion's own affiliate program terms are NOT Inspire3's account-specific contract.
* FTC CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business: review primary purpose, accurate subjects/sender, physical address and functional opt-out for **each** dispatched commercial-purpose email. FTC endorsement https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking : adjacent affiliate disclosure and no unsubstantiated personal/product endorsement.

## Evidence-to-conversion owner queue (priority, not another analytics script)

| Offer -> funnel step | Blocker | Change / experiment | PASS evidence | Owner |
| --- | --- | --- | --- | --- |
| Candidate Zen12 -> independent guide -> paid buyer | Named accepted partnership, EMAIL rights, issued link, SKU and guide not verified | Owner verifies merchant account and current checkout independently, makes vetted guide actually live only under approval | Account acceptance + channel-specific terms + issued link + vetted live first-party guide + merchant order/settlement and refunds/fees evidence | Mind & Affiliate Studio / Founder |
| Fieldbook -> newly confirmed subscriber | Provider categories contradict; no actual received welcome | Private consent transition witness and document actual welcome and PDF open, no repeat signup | First-party new confirmed event (no PII committed), opt-in timestamp/source, received final message, correct link, no double count | Focus / Claude |
| Dispatch -> engaged subscriber | Actual Jetpack email rendering, postal sender, opt-out and final approval missing | Founder-authorized non-sending native Preview, manual subject/footer and mobile review | Screenshot/record of native renderer, verified publisher address, working unsubscribe, final founder sign-off | Dispatch / Founder |
| Grok asset -> qualified visitor -> independently settled buyer | No reliable human-session denominator or settled order report | Reuse existing Claude analytics schema; do NOT create second collector | Distinct Grok asset_id/utm_content, consent-valid confirmed_signup, paid order/refund/fee settlement with 7/30-day cohort | Grok/Praxxis/Claude |
| Subscriber -> Focus PDF retrieval | Repeat-signup warning previously reported, now already fixed | Retire stale redline; audit first-party media URL consistency only | Media ID 1737 + live CTA URL + welcome URL match; separate actual HTTP and receipt test still needed | Dispatch QA / Focus |

## Required release gates

All six original messages: **HOLD_UNSENT**; optional Issue06: **HOLD_UNSENT**. The new Issue06 is not a substitution and does not activate a commercial offer. Mail subjects are controlled by real WordPress post title in Jetpack; optional specimen's preheader is **not** verified as a native Jetpack setting. Shipping requires actual native WordPress rendering/footers, founder sign-off and all relevant merchant permissions. No mock metrics, mail recipients, paid orders or net revenue reported. Net revenue per 1,000 qualified-human sessions = **NOT COMPUTABLE**, not zero.
