# R345 — Real WordPress + consent + outcome release checklist (NO SEND)

**Owner boundary:** Dispatch prepares email and source-integrity evidence, Mind/Commerce owns verified live offer guide and commercial permissions, Claude/Focus owns implementation of one `confirmed_signup` contract, Grok/Praxxis owns media asset IDs, founder owns final release. Homepage Issue #150 / frozen PR #49 are unaffected.

## Authenticated WordPress state (2026-11-14 03:31 UTC)

- Newsletter `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `from_name=Final Vestige Studios`, `reply_to=no-reply`.
- Welcome has direct 52-page Focus Fieldbook PDF URL; this is *configuration*, not a delivered-email receipt.
- Subscriber counts `total=3,confirmed=3,unconfirmed=2`, `suppressed=0`; separate Jetpack followers `wpcom=3,email=0`. Do **not** add as five; recipient email eligibility unknown.
- Five recent posts `never_sent_opted_out`. No recipient counts or demonstrated email delivery.
- Published pages: /dispatch/ ID 523, /focus/ ID 1579; direct PDF publicly downloadable without consent; no verified `confirmed_signup` event from a download.
- Actual merchant permission, published guide and payout all **NOT VERIFIED**.

## Native preview distinction / hard gates

| Evidence | State | Action, not permission to send |
|---|---|---|
| Offline HTML and plaintext | Available as reviewer artifacts | Verify markup, reading order and placeholder non-links; these are **NOT native WordPress emails** |
| Native **Preview email** | NOT CAPTURED | With existing authorized draft/editor, capture desktop/tablet/mobile preview **without** clicking Send test email or Publish. WordPress [documentation](https://wordpress.com/support/newsletter/email-appearance/) explicitly separates these. If no authorized draft exists, remain HOLD. |
| Received raw MIME | NOT CAPTURED | A real test email would contact a mailbox; prohibited until founder separately authorizes it. Inspect subject, envelope, HTML+plaintext, unsubscribe headers, actual publisher address and click behavior only if authorized. |
| Proposed preheader | NOT A VERIFIED FIELD | WordPress full-post email can derive snippets from intro. No confirmed independent preheader input; do not claim preheader rendered. |
| Verified postal address | UNKNOWN | Obtain valid FV legal sender address privately; do NOT substitute WordPress/Automattic/Inspire3 address |
| Working opt-out | UNKNOWN | Native actual received unsubscribe link required; must work with appropriate consent |
| Welcome delivery | UNKNOWN | WordPress configuration alone is insufficient; historical confirmation request in Gmail is not welcome receipt |
| Merchant affiliate EMAIL rights | UNKNOWN | Require named publisher acceptance, brand/offer permissions, issued URL, any email channel restrictions and live approved first-party guide |

## Single confirmed lead and attribution proposal (not deployed)

Treat signup attempts as events of type `signup_attempt`, not leads. Count `confirmed_signup` only on **provider-authoritative enrollment status**, once per provider subscription ID and confirmation transition, with no email addresses in analytics. For previously confirmed WordPress.com accounts, require authoritative confirmed status, not a fictitious new click-through. Maintain consent source, scope, timestamp and evidence reference in a private operational system; do not transmit addresses or identifiers in UTM URLs. Keep WordPress follower-source aggregates separate from provider consent counts.

Conventions for an *approved* future mailing: `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=mind_pilot_2026`, `utm_content=issue03_zen12`. The only destination is a verified first-party, approved guide; **do not activate or construct a tracked public URL now**. Grok inbound source uses its own authenticated `asset_id`, never masquerading as a Dispatch send.

## Conversion-first, smallest viable progression

1. Grok audience → evidence-specific landing article (**asset ID/visit not proven**).
2. Focus/Dispatch → explicit consent and provider-confirmed signup (**not yet measured**).
3. Welcome → Fieldbook actual inbox/delivery (**not yet verified**).
4. Editorial emails 01/02 → relevant historically supported investigations (**unsent**).
5. Issue 03 → *only if account permission and first-party guide approved*, make one qualified evidence-based optional offer (**hard hold**). Otherwise use pre-existing founder-approved editorial program; do not silently substitute copy.
6. Paid conversion → independently reported **settled order/commission**, with refunds and fees. Clicks and PDF downloads are **not sales**.
7. KPI for 7/30-day cohorts: `1000 * verified_net_revenue / qualified_human_sessions` only when numerator and denominator both authenticated; otherwise `NOT COMPUTABLE`. Very small sample => descriptive, never A/B significance.

## Issue allocation

| Edition | Original type | Status |
|---|---|---|
| 01 | Editorial | HOLD_UNSENT |
| 02 | Editorial | HOLD_UNSENT |
| 03 | Commercial (Zen12) | HOLD_UNSENT + HOLD_MERCHANT; optional R345 **NOT ADOPTED** |
| 04 | Editorial | HOLD_UNSENT |
| 05 | Commercial (Total Focus) | HOLD_UNSENT + HOLD_MERCHANT |
| 06 | Editorial | HOLD_UNSENT |

**No send, schedule, draft WP post, WordPress write, affiliate activation, subscriber contact, signup import, social post, merge, or paid service authorized.**
