# Dispatch R354 — Conversion-first proof contract — NO SEND / SOURCE ONLY

## Confirmed specification mismatch, not an invented conversion

The canonical Grok/Praxxis TASK-008 in the existing shared Google Doc requires:
- utm_source = actual platform (youtube, tiktok, etc.)
- utm_medium = organic_social
- utm_campaign = topic_cluster_pilot_2026_11
- utm_content = actual immutable Grok asset_id.

The earlier Dispatch R353 narrative example said utm_medium = social and unspecified campaign text. That is a **real cross-team specification mismatch** which, if deployed, would partition organic traffic into separate analytics buckets. There is **no evidence** that this has happened in production. No script, public link, campaign, Grok queue or site settings was altered.

Proposed newsletter last-touch convention, NOT ACTIVATED: utm_source=dispatch & utm_medium=email & utm_campaign=dispatch_pilot_2026_11 & utm_content=issue_03 (or the actual 01-06 issue). This requires an actually approved live CTA, eligible subscribers and founder approval. Preserve valid, independent first-touch Grok attribution; do not overwrite it on later email visits.

## Five-step subscriber-to-customer release contract

| Offer → funnel step | Blocker | Change / experiment | Pass/fail evidence; owner |
| --- | --- | --- | --- |
| Zen12 Premium → verified Mind buyer guide | Publisher affiliate acceptance, EMAIL rights, issued earning link, live approved guide, real checkout/terms remain absent | Request authenticated nonsecret authorization, do not activate Issue03 offer | FAIL/HOLD_MERCHANT — Mind / Commerce / founder |
| Actual Grok asset → qualified landing visit | TASK-008 canonical UTM conflicts with R353 narrative; actual source asset inventory unknown | Enforce organic_social and real post URL, timestamp, asset_id, rights and landing route | DESIGN TESTED, production NOT VERIFIED — Grok / Praxxis / Claude |
| Focus / Dispatch → confirmed lead | Provider totals 3/3/2 non-additive and eligible recipient roster unknown | Require provider-side genuine confirmation transition, dedup private opaque event ID | UNKNOWN — Claude / Focus |
| Confirmed reader → Fieldbook welcome | Welcome configured but no independently observed received message | Verify link from an authorized actual received inbox message without a new signup/list | CONFIGURED, DELIVERY NOT VERIFIED — Focus / founder |
| Dispatch → independently verified paid buyer | Legal publisher postal address, true unsubscribe/render, merchant acceptance, live guide, settled affiliate report absent | Native no-send Preview email first, separate founder-authorized received test, exact settled receipt + fees/refunds | FAIL/HOLD — Dispatch / founder / Commerce |

## Source-of-truth observations, November 14, 2026

Authenticated Jetpack read-only at 12:37 UTC: newsletter ON, new-post automatic sending OFF, full email body, Final Vestige Studios sender, existing 52-page Fieldbook welcome configured. Subscriber totals: total 3; confirmed 3; unconfirmed 2; these are overlapping / inconsistent counts, **not five people**. Latest five post send records are never_sent_opted_out. site_can_send does not grant permission to send. Eligible inbox recipients remain unknown.

The live https://finalvestige.com/dispatch/ public rendering shows an input and Subscribe button, while the provider content view shows a self-link. Neither confirms successful submission. The live https://finalvestige.com/focus/ displays a direct PDF download, but PDF access is not newsletter consent. Existing Editorial Standards: https://finalvestige.com/editorial-standards/ require checkable research, visible uncertainty and independent commercial judgment.

Exact Zen12 product site https://zen12.com/ describes Premium as 12 levels and 48 MP3s, a one-year money-back claim, and promotional effects that are seller advertisements, **not independently proven efficacy**. Its multiple public package/promotion prices are not a validated Final Vestige referral checkout price. Exact Hypnosis Live Total Focus remains a separate merchant hold; catalog and sales pages do not establish publisher-specific EMAIL promotion rights.

Official FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . For commercial email, confirm accurate origin, honest subject, appropriate disclosure, the publisher's own valid postal address, opt-out working at least 30 days and requests honored within 10 business days. Automattic's corporate mailing address is not automatically Final Vestige's. Official Jetpack preview workflow https://wordpress.com/support/newsletter/email-appearance/ separates Preview email from Send test email. An offline HTML mock is neither.

## Tests and exact status

The companion native Python validator makes explicit distinctions:
- social_touch: QA-ELIGIBLE only with actual Grok owner evidence and exact TASK-008 UTMs; this is NOT an authenticated session
- provider_counts: aggregate categories are DIAGNOSTIC ONLY; eligible audience always unknown
- confirmed_signup: only one permission-backed confirmation transition; reject repeats, opt-outs and analytics PII
- email_touch: reject preapproval, unsent, unverified CTA and invalid issue IDs
- paid_outcome and revenue_per_1000: independently merchant-attested settled payments in USD minor units, fee/refund deduction, distinct orders, qualified-human denominator; no click as sale
- edition_hold: original six always HOLD_UNSENT; 03/05 additionally held on affiliate rights. No code path grants send permission.

Synthetic positive test fixtures are **not live events**, traffic, subscriber or sales evidence. The founder's four editorial / two prospective commercial pilot remains unchanged. Draft PRs #175, #201 and #2467, frozen homepage #49, existing Jetpack list and Grok TASK-008 remain untouched. Optional crystal-skull Issue02 candidate is NOT ADOPTED, UNSENT.
