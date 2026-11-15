# R379 — Native Jetpack verification / double opt-in / source-tagged revenue contract

**Source-of-truth snapshot:** authenticated WordPress on November 15, 2026, 13:32–13:33 UTC. Newsletter enabled; auto-email of new posts OFF; send technically possible; full email content; sender display Final Vestige Studios; no-reply; welcome message contains the 52-page Focus Fieldbook PDF URL. Five latest post notifications were never sent because send_subscription=false. None of these observations is a delivered welcome or actual mail preview.

## Subscriber eligibility: reconcile without exposing addresses

Provider API total 3, confirmed 3, unconfirmed 2, suppressed 0, paid 0. Separately, Jetpack Stats followers reports WordPress.com followers 3, direct email followers 0. These are **different provider populations** and cannot be added to infer five recipients, nor can the Stats email count be substituted for a definitive deliverable audience. Confirmed identities are not automatically eligible receiving inboxes. Record only an aggregate, provider-filtered Email Subscription=Subscribed count after deduplicating subscriber identities, pending verification, stopped/bounced/paused addresses and delivery restrictions. It is currently UNKNOWN.

Proposed event: confirmed_signup_v1 only after **provider-authoritative** double-opt-in confirmation, deduplicated by an opaque provider key and first confirmed transition time. A URL parameter, client panel reveal, free PDF click, social follow, or initial form submit is not consent confirmation. One subscriber, one event. Do not store addresses in campaign analytics or public GitHub.

## Native email acceptance — all checks are NOT YET PERFORMED

- WordPress documentation: https://wordpress.com/support/newsletter/email-appearance/ (last reviewed November 9, 2026), https://wordpress.com/support/newsletter/send-newsletter-emails/. The post title controls notification **subject**. Independently drafted preheaders have NO verified native Jetpack mapping.
- With owner-authorized access to a **non-sending draft editor**, select Newsletter → Email → Preview email. It is **different** from Send test email; do NOT send a test, publish, schedule or change post metadata/settings absent founder final release approval.
- Capture browser desktop, tablet and mobile native-preview evidence, including subject, full/excerpt behavior, images, line wrapping, heading hierarchy, descriptive CTA, near-offer disclosure, source links and actual footer. Offline HTML from PR #2619 or R379 is not native.
- Confirm publisher's **Final Vestige qualifying physical postal address** (not Automattic's office in a WordPress confirmation message), truthful sender and effective opt-out. Real delivered-mail functionality is unverified and requires separately authorized testing on an approved mailbox. Do not fake unsubscribe placeholders as working links.
- Confirm actual received welcome and functioning PDF in an approved inbox after separate permission. A received October 25 subscription CONFIRMATION is not receipt of the subsequent welcome.
- The public /dispatch/ and /focus/ pages show signup messaging; public rendering does not prove an actual successfully submitted form. No form submission, sign-in test or list mutation authorized.

## Non-sending hypothetical progression

A. Grok-owned social asset_id and utm_source/utm_medium=organic_social/utm_campaign/utm_content flow to matching Focus topic page (Claude owns analytics implementation). B. Page CTA click. C. Provider's single deduplicated confirmed_signup_v1. D. Actual welcome receipt + usable Fieldbook (verify separately). E. Relevant editorial issue with one destination; approved offer only for Issues 03 and 05. F. Independent merchant confirmed paid order and net settled affiliate commission, with refund/fee adjustments.

Report 7- and 30-day attributed cohorts only where evidence exists. Denominator: qualified-human sessions (exclude bots/duplicates). Numerator: settled commissions or FV paid product net receipts less refunds/fees attributable under documented policy. KPI net revenue per 1,000 qualified human sessions = net revenue / sessions * 1000 **only if both are verified**. Otherwise mark NOT COMPUTABLE; never substitute 0 or count clicks as orders. Founder controls any production tracking change; Grok controls social distribution; Mind controls product qualification; Dispatch controls draft email QA.

## Stop conditions

Original Issue 04 unqualified fourteen-second subject is HOLD_COPY; new R379 historical candidate NOT_ADOPTED. All original six HOLD_UNSENT; commercial 03/05 HOLD_MERCHANT. Source archive unchanged, no WordPress writes or email contacts. The FTC requires accurate subject/sender, appropriate ad identification, qualifying physical mailing address and effective opt-out when commercial email rules apply: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business.
