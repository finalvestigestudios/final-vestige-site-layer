# Dispatch → confirmed lead → verified purchase: provider and owner contract

**This is a specification, not implemented live analytics.** Conversion is not email volume. Grok retains primary social-acquisition ownership under TASK-008; Claude owns existing event instrumentation; Mind/Commerce owns offer rights and accepted checkout; Dispatch owns editorial/consent verification.

## Narrow first-audience hypothesis
A reader of a Grok change-blindness short who chooses a published experiment explanation may be better suited to the Fieldbook's *no-cost attention journal* than to an immediate meditation product pitch. Hypothesis only—no measured cohorts. The pilot first newsletter must establish evidence-first trust and invite one substantive read, not route straight to checkout. Future issue 03 may offer a Zen12 guide only on named email and guide approvals.

## Single event definition: confirmed_signup
Fire **once** only after the existing provider confirms address ownership and marketing permission and the existing instrumenter can document the confirmation transition. Input: opaque existing provider subscriber ID + confirmation timestamp + consent provenance + public source campaign fields. Do not log raw email/name/IP to GA or GitHub. Dedupe by provider-confirmation ID or a privacy-safe stable internal surrogate; repeat button clicks, pageviews, downloaded PDFs, WP.com follows and unconfirmed addresses are NOT confirmed_signup events. A provider aggregate (3 total / 3 confirmed / 2 unconfirmed) is NOT a count of distinct reachable email inboxes. No parallel list.

## Attribution convention for future approved use
- Grok asset lands on relevant page with vetted `utm_source=<active_channel>`, `utm_medium=social`, `utm_campaign=<campaign_slug>`, `utm_content=<unique_asset_id>`. Grok owns asset IDs and URLs. Retain verified first touch; never overwrite with a later newsletter visit.
- Proposed Dispatch editorial link, ONLY if Claude approves existing analytics convention: `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_pilot_2026&utm_content=issue_01_change_blindness`. No new pixel/JS and no tracking links activated in this offline draft.
- A **landing view** is not a human until bot/exclusion processing. A **CTA click** is not confirmation. A **confirmed signup** is not a paid order.
- Distinct lead and purchase cohorts should be joined by authorized, consent-respecting privacy-safe keys only if supported. No identity joining with raw email in client-side analytics.

## Paid-order acceptance
Commerce provides merchant-authoritative paid order/settled affiliate conversion ID, attribution confidence, currency, purchase timestamp, refunds, chargebacks, commissions, processing/network fees and settlement timestamp. De-duplicate order ID; provisional clicks/leads/pending commissions never count as realized revenue. Reversals update historical cohort net. Report unknown when permission, sales feed, denominator or matching is absent.

**7- and 30-day reporting:** eligible qualified human sessions, observed CTA clicks, provider-confirmed leads, independently confirmed paid orders, gross settled commission or direct sales, refunds, fees, realized net, `1000 × realized_net / qualified_human_sessions` **only when both validated inputs exist**. Suppress tiny-sample rate interpretations, never fabricate A/B significance.

## Ownership and release
Claude/Focus: signed-out guest first-click, consent, welcome/PDF read-only verifications. Dispatch/Founder: native Jetpack preview, confirmed address/unsubscribe evidence and approval of exact issue/recipient schedule. Mind/Commerce: merchant account acceptance, EMAIL rights, earning link and live independent guide. Grok/Praxxis: unique asset handoff and social source integrity. No owner may infer a sale from an intermediate event.
