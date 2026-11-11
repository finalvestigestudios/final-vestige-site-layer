# Dispatch R285 — Subscriber-to-customer acceptance, without sending or new tracking

**Owner:** Dispatch Issue #174. **Offer guide / rights owner:** Mind Issue #171. **Signup engineering owner:** Claude/Focus Issue #129. **Commercial KPI coordination:** Issue #820. **Grok asset inventory:** Praxxis-Grok TASK-008 (read only). No ownership transfer.

## Segment hypothesis (not a behaviorally verified audience segment)

A reader comes from a real history-of-suggestion or perception investigation; they may want a modest focus routine. A relevant, accurately described meditation or hypnosis tool can be considered **after** an editorial record, a free practice alternative and provider-confirmed subscription, not as a blanket first email. No subscriber segmentation is live or inferred from clicks or email addresses.

## Funnel evidence contract

1. Social: Grok/Praxxis records each **actually published** `asset_id` and source link; there is no assumption that a caption is clickable or a social impression is a session.
2. Landing: Claude must establish privacy-safe qualified-human visits from existing analytics; preserve platform's `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<real_asset_id>`. No duplicate pixels.
3. Focus: The existing Jetpack signup provides the only list. `?subscribe=unknown_state`, displaying the download panel, initiating a confirmation request, or downloading a PDF do **not** prove consent. Emit **one** `confirmed_signup` event only on an authenticated provider-confirmed AND email-eligible transition, using a private opaque provider event key for idempotence. Never expose an email or its hash in analytics or URLs; do not conflate Reader followers with email subscribers.
4. Welcome: The configured 52-page Fieldbook link is **configuration evidence only**; actual received welcome and successful file delivery remain unverified. No new tests that contact real subscribers or change settings.
5. Issue05: only if the guide is actually live, the partner has explicitly allowed **email** promotions for FV's account, earning link and creative are authorized and price/refund claims audited, and legal send footer is verified. Otherwise **HOLD**, not a fallback sales blast.
6. Settlement: a merchant/Payhip independently reported **paid and settled** order (minus refunds, fees and chargebacks) is the earliest revenue proof. Affiliate outbound clicks, checkout views and email opens are separate diagnostics, never paid purchases.

## Non-deployed, proposed issue05 CTA tag

`utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_issue05_total_focus`

Attach only to a permitted, reviewed first-party guide URL after complete release approval; NEVER to a placeholder or subscriber-specific token. Do not infer per-person Grok-to-sale journeys from aggregate data. Existing analytics owners decide whether native tracking can observe the CTA; do not introduce measurement scripts.

## Cohort scorecard

7 and 30 days, report raw values and provenance: real qualified-human sessions; source asset ID; newsletter **eligible** audience; consented confirmed leads; guide CTA clicks; independently settled paid orders; gross, refunds, chargebacks, processor/affiliate fees; realized net revenue. KPI `1000 * verified_net_revenue / qualified_human_sessions` only when both verified net revenue and a positive, privacy-safe qualified-human session denominator exist. Else **NOT COMPUTABLE**. Tiny denominators prohibit statistical A/B claims. No synthetic events counted as production.

## Release safeguards

Every potentially commercial newsletter needs FTC primary-purpose assessment. Verify sender name/address, valid actual publisher physical postal address, visible unsubscribe in the *actual Jetpack-generated email*, functioning opt-out, merchant channel terms and source-specific affiliate disclosure adjacent to the commercial recommendation. Use native WordPress **non-sending preview** where authorized, but clearly label its limitations versus a real inbox message. New-post default OFF is not equivalent to locking per-post sending OFF. Founder final approval is required for sending, audience and timing.

Official FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
Official WP: https://wordpress.com/support/newsletter/send-newsletter-emails/

**KPI denominator definition:** Qualified-human sessions are privacy-safe, bot-filtered, distinct eligible visits, not impressions or all Jetpack views. When population provenance is unverified, the KPI remains NOT COMPUTABLE.

**Audience arithmetic rule:** Jetpack diagnostic total/confirmed/unconfirmed and WordPress Reader/email follower measurements are not additive; eligible current recipients remain unknown until provider confirmation.
