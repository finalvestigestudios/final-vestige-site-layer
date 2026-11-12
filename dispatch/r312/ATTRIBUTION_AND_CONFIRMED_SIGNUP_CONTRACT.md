# R312 — Consent → content → offer → settled revenue measurement contract (review only)

**Purpose:** Avoid counting a browser confirmation screen, page visit, WordPress Reader follow, editor preview, affiliate click or checkout start as a commercial conversion. There are no asserted live values.

## One canonical confirmed_signup event; no duplicate emitters

**Owner:** Claude / Focus. Implement only after authorization and agreement with currently deployed analytics, never as an additional tracking script.

- Source: actual provider-confirmed Jetpack newsletter email state transition, e.g. pending/unconfirmed → subscribed with email notifications enabled, not a query string or visual success panel. For existing WordPress accounts who skip a new confirmation email, rely on an authenticated provider eligibility transition instead of assuming a fresh double-opt-in link.
- Deduplication: store an opaque, consent-safe provider subscription identity and first confirmed transition. Repeated confirmation clicks, refresh, switching devices or repeat form submissions must not increment a confirmed lead twice. No raw emails, hashed unsalted emails, names, recipients or full referrer URLs in event payloads.
- Event payload: `event=confirmed_signup`, `provider=jetpack`, `consent_state=subscribed_email`, `first_confirmed_at_utc`, `source_campaign`, `origin_asset_id` (when legitimately attributable), `idempotency_proof=opaque` (private server only). Do NOT emit this event from the public Focus page JavaScript. If the provider status is not safely available, **do not emit**.
- Welcome evidence: a provider setting containing the Fieldbook URL proves configuration only. An owned inbox copy (separately authorized) proves delivery only to that address, not all subscribers. A confirmed email address is not the same as recipient receipt.

## Source tagging without duplicate measurement

Grok owns asset IDs/caption+profile placements, under TASK-008; do not modify Grok's posting queue. Proposed canonical source convention, not live links: `utm_source=youtube|tiktok|instagram|facebook|...`, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<immutable_asset_id>`. Preserve a last-known valid source tag in consent-safe first-party analytics with appropriate consent. If a bio link drops a UTM, report unattributed rather than inventing an association.

Dispatch email CTAs after all approvals: `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_mind_pilot_2026_11`, `utm_content=issue_01...issue_06`. No subscriber-specific unique tracking tokens, no active link additions this sprint. A 4:2 campaign does not equal six sends or six independent recipient-cohort sequences.

## Net revenue accounting rule

A commercial conversion is **only** a settled first-party payment order or a merchant independently reported eligible affiliate paid conversion that can be attributed, with refunds, fees, reversals and commissions reconciled. Count customers and orders uniquely. Never substitute click, checkout start, signup, or "sale estimated from traffic." 

For a 7- or 30-day source-linked cohort with nonzero, independently qualified human sessions:

`net_revenue_per_1000 = 1000 * (settled_first_party_net + paid_eligible_affiliate_commissions - refunds - fees - chargebacks) / qualified_human_sessions`

If dates cannot be reconciled, source attribution is missing, denom is zero/unknown, or merchant paid conversions are not reported, the KPI is **NOT COMPUTABLE**, not $0. No A/B uplift percentages with a three-account diagnostic list.

## R312 status at 2026-11-12 19:37 UTC

- `confirmed_signup` event emitted by actual provider: **NOT VERIFIED**.
- Provider email-eligible population: **UNKNOWN**; 3 confirmed WordPress counts ≠ 3 deliverable emails.
- Real received welcome/Fieldbook: **UNKNOWN**.
- Merchant email permission and issued earning link: **UNKNOWN**.
- Settled independent paid orders / commissions / fees / refunds: **UNKNOWN**.
- Net revenue per 1,000 qualified human sessions: **NOT COMPUTABLE**.

All planned actions remain outside production; each owner must link evidence and founder approval before deployment.
