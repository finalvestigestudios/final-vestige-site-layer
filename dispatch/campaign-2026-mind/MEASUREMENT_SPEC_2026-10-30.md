# The Dispatch — Privacy-first measurement specification

Status: proposed only, zero deployed trackers, zero actual newsletter sends, zero verified conversions. Owner: Dispatch Studio, Issue #174 / PR #178, coordinating with Mind Studio #171.

## Funnel
Actual Jetpack campaign delivery → opted-in email click → independent Final Vestige warm-up guide page view → disclosed approved merchant click → merchant-confirmed affiliate order (if approved).

WordPress currently reports total=2, confirmed=2, unconfirmed=2, which is inconsistent. No unique audience count can be inferred. Email open rates are biased by privacy proxy and should not be treated as evidence of reading.

## Proposed aggregate events
- newsletter_delivery: actual WordPress-supplied delivery count, when available.
- guide_view: canonical FV guide path, event day and coarse source/campaign tag.
- approved_outbound_click: product, destination guide and event day, only after affiliate authorization and privacy review.
- merchant_confirmed_order: product, merchant report day, number of confirmed attributed purchases and refunds, only if permitted by account reporting.

Proposed non-personal dimensions: event_day_utc, edition_id (03 or 05), product (zen12 or hypnosis_live), source (wordpress_aggregate / first_party_aggregate / merchant_dashboard), verification (not_available / observed / merchant_confirmed), count. Do not publish subscriber emails, IP addresses, individual click IDs, user-agent strings, session identifiers or personal purchase records in the repository.

Optional tracked link tags ONLY IF appropriate after privacy and real email checks: utm_source=dispatch, utm_medium=email, utm_campaign=mind_pilot_2026, utm_content=issue_03_zen12 or issue_05_hypnosis. Do not add identifiers or tracking to merchant URLs unless Inspire3 explicitly approves.

## Definitions
- Email-to-guide CTR: confirmed unique FV-guide clickers / delivered commercial emails, only if both comparable counts exist.
- Guide-to-merchant click rate: approved outbound click events / observed guide sessions over same time period; label click-through, not sale conversion.
- Merchant conversion: merchant-confirmed attributable orders / eligible outbound clicks, only if account reports compatible measures. Otherwise report confirmed orders with a caveat.
- Unsubscribes and complaints are trust guardrails. Preserve 4 editorial + 2 commercial-review-pending cadence, and no more aggressive sending without separate approval.

At this audience size, do not use significance claims or A/B statistics. Run preview/copy quality audits, grow a consented list, then revisit tests. Retain baseline data for only the minimum needed and follow the site's Privacy Policy.

## QA before activation
Confirm the welcome message, exact recipient count and consent. Verify WordPress's excerpt-vs-full email rendering, real sender headers, full commercial footer and unsubscribe. Publish reviewed FV guide only after approval. Validate offer/link and terms, then use test deliveries only with founder-authorized recipients. Never imply that a click is a sale.
