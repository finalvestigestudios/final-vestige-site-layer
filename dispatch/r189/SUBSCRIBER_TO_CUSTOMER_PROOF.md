# R189 — Actual subscriber → authorized offer → settled customer evidence contract

Owner: Dispatch Issue #174 for first-party consent/welcome/email attribution. Mind #171 owns seller-specific offer eligibility and vetted buyer guide. Claude/Site QA own production engineering. Grok/Praxxis TASK-008 owns creator attribution and social work. This is a **proposal, not live analytics or permission to send**.

## As-of 2026-11-07 16:33 UTC: official connected configuration
Jetpack subscriptions ENABLED; new-post automatic email OFF; sender name Final Vestige Studios; `reply_to=no-reply`; `email_content_format=full`. Subscribers total=3, confirmed=3, unconfirmed requests=2, suppressed=0 (NONADDITIVE). **Email-eligible count unknown**: a confirmed WordPress.com Reader follower might not receive email. Subscriber status cannot be inferred from these aggregates. Latest five posts `never_sent_opted_out`. Real email preview and welcome receipt not obtained. One configured 52-page Focus Fieldbook welcome remains intact.

WordPress /dispatch/ page ID 523 published; rendered API block shows an anchor rather than an input, which **does not prove** the public interactive form is broken. A signed-out test and legitimate provider confirmation are still needed. WordPress /focus/ page ID 1579 published; client `fvf-gift-v2` reveals a download after nonblocked `?subscribe` values or `is-subscriber` CSS; this is **not authoritative consent**. Editorial Standards ID 17 requires primary evidence, uncertainty and independent commercial judgments.

## Conversion-first hypothesis
Audience: history/perception readers who voluntarily request the Fieldbook and later choose to evaluate concentration audio. One proposed offer: Hypnosis Live **Total Focus**, subject to named approval and commercial email-channel permission. The full consumer path works **without a forced opt-in** to see the future first-party guide; subscriber nurture is optional and only for authorized recipients.

| Offer → Funnel step | Blocker (as of review) | Change / measurement | Acceptance evidence | Owner |
| --- | --- | --- | --- | --- |
| Focus / Dispatch → legitimate opted-in lead | Query-gated gift and aggregate followers are not consent | Use server/provider-confirmed opt-in and deduped consent provenance only | Provider `email subscription=Subscribed`, timestamp, auditable confirmation; **UNKNOWN** | Claude / Site QA #129 |
| Confirmed lead → 52-page Fieldbook | Welcome content configured, receipt unknown | Inspect existing **authorized**, already-received message & download; do not trigger send | MIME delivery and working PDF link; **UNKNOWN** | Dispatch #174 |
| Editorial nurture → relevant guide | Jetpack native email/footer not actually inspected | Preview without enabling send; genuine recipient unsubscribe only after separately approved real test | Native template + valid FV postal + working opt-out; **UNKNOWN** | Dispatch #174 |
| Total Focus offer guide → licensed earning link | Named FV Inspire3 acceptance, email-channel permission, approved creative, live guide absent | Mind authenticate account agreement + exact permitted URL + offer-specific page claims | Signed/recorded partner permissions, live first-party guide, adjacent disclosure; **HOLD_MERCHANT** | Mind #171 |
| Customer purchase → realized net revenue | No source-linked paid order / commission / fees / refunds and human denominator | Verify merchant or Payhip reconciliation, fraud/robot filtering, seven- and 30-day cohorts | Settled paid orders and attribution proof; **NOT COMPUTABLE** | Commerce / Praxxis #820 |

## Canonical proposed `confirmed_signup` event
- Trigger **only** when an authoritative Jetpack subscription record transitions to **Email Subscription=Subscribed** with appropriate consent documentation. A provider event, NOT browser URL parameters, has final authority. If this is unavailable in the existing site without added expense/credentials, status **NOT IMPLEMENTED** and stop.
- Proposed stored dimensions (no addresses or subscriber secrets): `event_type=confirmed_signup`, `provider_event_id` opaque (not personal), `event_at_utc`, `site_scoped_pseudonymous_contact_key` derived securely on server, `consent_version`, `consent_source` if known, `acquisition_utm_campaign` and `asset_id` only when actually captured with consent. No PII in logs, GitHub or Google Drive.
- Deduplicate by unique `(provider, provider_transition_id, transition_to=Subscribed)`, and separately by current subscriber key plus state transition; attempts, resends, partial confirmations, downloads, Reader follows and duplicate callbacks are not confirmed leads. Re-subscribe after opt-out is a new transition and must have fresh consent.
- No new tracking script in production until Claude's existing #820 event architecture is checked for duplicate analytics tags and privacy implications.

## Attribution convention with creator ownership preserved
Grok social creative links (only actually published/approved) use `utm_source=<actual_platform>`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<real_immutable_asset_id>` with no fabricated IDs. Preserve origin as consented first touch if feasible.

Dispatch's future one-guide CTA uses `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_05_total_focus` **only after guide and approved link exist**. Email click is an intermediate stage, never a paid order or proof of original traffic source. Avoid overwriting true Grok acquisition with email re-engagement. Where multi-touch matching is unavailable, report `unattributed`.

## Net-revenue truth
`realized_net_revenue = verified_settled_gross_receipts_or_earned_commissions - recorded_refunds - merchant_platform_network_fees - payment_reversals`, excluding merely pending/estimated commission. `net_revenue_per_1000_qualified_human_sessions = 1000 * realized_net_revenue / qualified_human_sessions` if independently measured, qualified denominator >0, and settlement evidence exists; otherwise **NOT COMPUTABLE**.

Only paid orders verified by merchant/payment source are sales. Do not invent A/B significance with 3 counted subscribers. Report 7/30-day periods, observed cohort size, attribution gaps and any orders excluded due to returns or inadequate source proof.

## Source of truth and stop conditions
- Founder campaign Issue #174 and master PR #175, review #201; Mind #171; Focus #129; conversion #820; TASK-008 handoff in existing shared Drive.
- Official seller page https://hypnosislive.com/mental-skills/total-focus (format and claims; NO FV affiliate approval evidence).
- Official FTC CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business and endorsement guidance https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking.
- Official WordPress preview docs https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter-email-design/.
- Status: **BUILT_DRAFT**; **NO VERIFIED COMMERCIAL REVENUE**; **NO LIVE EVENT**; **ALL SIX HOLD_UNSENT**; 03/05 **HOLD_MERCHANT**. Do not send, schedule, import contacts, modify settings, publish, activate links, contact subscribers, or spend.
