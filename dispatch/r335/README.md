# Dispatch R335 — provider confirmation and Fieldbook evidence (NO SEND)

**Purpose.** Preserve all six original weekly drafts while closing a conversion-truth gap. The live /focus/ page exposes a direct PDF download without proof of Dispatch subscription; WordPress.com has two valid confirmation paths. A previously verified WordPress.com account can skip the new email challenge; other email subscribers receive a confirmation request. PDF access, confirmed opt-in and witnessed welcome delivery are distinct events.

**Read-only WordPress evidence — November 13, 2026, 18:03 UTC.** Jetpack newsletter enabled, can send technically, automatic new-post emails OFF, full content, sender Final Vestige Studios, 52-page welcome configured. Counts: total 3 / confirmed 3 / unconfirmed 2. Separate followers: WP.com 3 / direct email 0. Do NOT add or subtract overlapping classifications to infer eligible recipients. Five recent posts were individually never_sent_opted_out, which does not prove zero historical sends. /dispatch/ and /focus/ remained unchanged.

## New work versus R334

R334 already checks synthetic consent-to-revenue provenance. R335 closes the provider-specific false-negative risk (requiring a confirmation click even for a preverified WP account) and false-positive risk (counting a PDF download or follower as an opted-in inbox lead). New synthetic-only Node module, 36 adversarial tests, independent source audit, non-sending receipt protocol and offline review board. Not a new mailing platform or production analytics script.

Run: node --test dispatch/r335/signup_boundary.test.cjs

Never run on real subscriber exports. The test gate accepts only synthetic- prefixed identifiers, rejects unexpected/PII keys and always reports actual subscriber count, paid sales and net revenue as unknown. It cannot authorize sending under any conditions.

## Evidence required for a legitimate confirmed_signup

1. Read actual WordPress provider Email subscription state for site 256784396 privately: Subscribed, with proper Dispatch consent, not Not confirmed, Bounced, Emails paused or Not sending. Follower count is not an opt-in list.
2. Non-WP accounts: evidence the provider's link confirmation completed. Preverified WP accounts: independent proof of verified account path and explicit site newsletter subscription; no invented second confirmation click.
3. Deduplicate by a provider-issued opaque identity only within private authorized infrastructure, not GitHub or a new contact list. Only a verified transition creates a new confirmed_signup event. An old known subscriber is an eligibility snapshot, not a newly acquired lead.
4. A configured welcome containing the 52-page URL does not establish arrival. Verify a genuine, separately authorized received message without sharing recipient PII. The on-page PDF link is not a consent or delivery proxy.
5. Merchant Zen12 free gift opts into the seller's own newsletter. Email click and checkout start never equal a paid sale.

**Commerce:** One hypothesized Zen12 Premium guide, but actual email affiliate permission, issued earning link, current claims/checkout and live guide are unverified. Without independently settled commissions and real qualified-human sessions, net revenue / 1,000 remains NOT COMPUTABLE. No A/B lift claims with tiny samples.

Official sources:
- https://wordpress.com/support/newsletter-settings/
- https://wordpress.com/support/subscribers/
- https://wordpress.com/support/newsletter/send-newsletter-emails/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

Related: original campaign PR #175, gate #201, preceding R334 PR #2372, Issues #174/#171/#129/#820; frozen homepage PR #49 untouched.

**Release:** Six HOLD_UNSENT; Issues 03/05 also HOLD_MERCHANT. No test email, real email, CMS write, list contact/export, affiliate activation, social post, deployment, merge or expense.