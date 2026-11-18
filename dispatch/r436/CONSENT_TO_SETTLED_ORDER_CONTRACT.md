# R436 — one genuinely confirmed lead and one settled sale, not more clicks
Source-of-truth: [Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); handoffs to Focus #129 and Dispatch #174. **Proposed contract only; not deployed.**

## Event ownership and definitions
**Grok's immutable social asset_id** → utm_source actual platform, utm_medium=organic_social, utm_campaign exact topic pilot, utm_content asset_id → first-party qualified-human landing session (Claude/analytics owner) → focus form intent → one confirmed subscriber transition (Focus/Dispatch provider gate) → one consented editorial newsletter CTA click → approved product warm-up guide → separately merchant-confirmed settled paid order (Mind/Commerce) → refunds/fees → realized net revenue.

- `focus_signup_click`: button interaction, **not** an email submission or confirmed lead.
- `focus_pdf_click`: free download intent; neither subscription nor delivery proof.
- `confirmed_signup`: **one event per unique, provider-verified subscription identity and consent scope**, emitted only on an authenticated Jetpack status transition to email-subscribed and eligible for Dispatch. Dedup by a privacy-preserving stable provider object ID within the server boundary and event timestamp; no raw email, confirmation token, IP or name in telemetry. Do not backfill by treating CSS class or URL query as provider proof. Existing account subscribers may bypass a new confirmation email according to WordPress docs; verify the provider-confirmed state rather than demand a particular email step from every user.
- `dispatch_cta_click`: one user action on a single relevant first-party vetted guide; for promotional issues require partner email permissions and an approved live guide. Never classify as sale.
- `paid_conversion`: merchant/Payhip independently confirmed transaction ID, actual captured/settled amount, correct referral window and SKU; remove duplicates, refunds, fees, reversals. Without that record, mark outcome UNVERIFIED, **not zero**.

## Measurement contract — aggregate only
Minimal event record: `event_type`, `event_time_utc`, `campaign_id`, `asset_id`, `issue_id`, `opaque_dedupe_id`, `provider_receipt_reference`, `consent_scope`, `observability_status`. The provider ID never appears in client-side URL, exported GitHub log or issue comment; publish only cohort totals with k-anonymity/small-N suppression where needed. Do not infer personally attributable source journeys from cookies if consent/retention policies do not permit it.

The 7-/30-day report must distinguish:
1. qualified-human sessions, with bot/referral spam exclusions and denominator method;
2. verified unique eligible subscribers (consent + email delivery allowed, not merely 'confirmed' dashboard aggregate);
3. delivered/received welcome evidence (optional where consented and authorized, never guessed);
4. first-party CTA and approved guide visits **as upstream steps only**;
5. independently confirmed paid customers/orders and net settled revenue after refunds, affiliate clawbacks and fees.

KPI = 1,000 × **settled realized net revenue** / **qualified-human sessions** within a clearly defined same-source window. If either verified numerator coverage or denominator is missing, display `NOT_COMPUTABLE`. A fully reconciled **verified zero** can be reported only if the merchant report is complete, cohort mature and denominator independently validated. With three dashboard 'confirmed' entries and no eligibility denominator, no statistically sound A/B comparison or reliable conversion rate exists.

## Six-issue progression, preserving 4:2
01 change-blindness history investigation (editorial CTA); 02 Franklin/Puységur historical verification (editorial CTA); 03 Zen12 evaluation only after **EMAIL-channel** rights and guide publication; 04 Apollo 1 archival investigation (corrected candidate must be founder adopted); 05 Total Focus buyer's checklist only after independent **EMAIL-channel** rights and guide publication; 06 free Fieldbook practical log. Each one CTA. Product outbound link, price, commission, refund terms and offer availability remain unset until merchant and founder evidence. The two promotional slots are RESERVED, not activated. Prefer testing **one** verified offer, not running both simultaneously with tiny list.

## Planned but unimplemented acceptance
Synthetic replay: a user clicks PDF five times and edits `?subscribe=success`; provider has no eligible transition => 0 confirmed leads. Provider confirms one eligible subscription, six page reloads => 1 distinct lead. Merchant link clicks without independent settlement => no paid conversions. Refund after initial settlement reduces realized net; non-attributed paid transaction must not be spuriously credited to Grok/Dispatch. These are specifications only; existing R435 pure provider gate and R430 settlement gate own executable synthetic coverage. Do not create another GA4 script or override Claude's events.