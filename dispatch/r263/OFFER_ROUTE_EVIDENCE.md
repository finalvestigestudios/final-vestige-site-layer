# R263 — The hidden second newsletter in the Zen12 offer path

**11 November? No: observed November 10, 2026 UTC 19:35 — DRAFT ONLY / NO SEND.** This release-risk review is scoped only to Dispatch. It does not replace any of the founder's six original drafts, edit /focus/, claim merchant approval or deploy new analytics. Master PR #175; readiness PR #201; base PR #1935.

## Important new conversion finding

A seller's so-called "free audio" may not be a free, no-follow-up product sample. The official Zen12 /welcome landing page explicitly states **"You will receive our newsletter."** The separate /freeaudio route says the same. This means a person following that offer may initiate a **new relationship with the seller**, not just obtain audio. That signup must never be counted as a confirmed Final Vestige Dispatch subscriber, cannot be assumed to inherit Final Vestige's existing Jetpack consent, and should be mentioned plainly if the Mind Studio ever elects to recommend the route. Nobody visited a live form or subscribed during this review.

### Exact vendor evidence (marketing, not endorsement)

* https://zen12.com/hnp — seller describes 12-minute recorded meditation sessions and asserts "an hour" equivalence. The format is observable; claimed equivalence is not independent product evidence.
* https://zen12.com/secret/ — a coupon/price/countdown route substantially different from the main presentation. Specific price, coupon, urgency, refund and vendor promise require verification for the exact named approved affiliate link. Do not borrow the timer or use a discount in Issue 03.
* https://zen12.com/welcome and https://zen12.com/freeaudio — vendor free-audio offer also promises the **vendor newsletter**; this is distinct from Dispatch's already-consented single Jetpack list.
* https://hypnosislive.com/mental-skills/total-focus — seller lists 33-minute / 47-MB Total Focus audio, but different snapshots have displayed **$2, $17.95 and $24.44** for the standalone product, plus differing bundles. This is a **price-conflict**, not evidence which consumer would see which price. Reasons could include dynamic offers or caching, but remain unknown. **No price or refund promise** in Dispatch until approved account-specific checkout is verified. The merchant's UK footer address is **not** Final Vestige's postal address.
* https://affiliates.inspire3.com/ — public recruitment page says affiliates receive special issued tracking links and advertises payouts. Does **not** confirm named Final Vestige acceptance, email-channel rights, link format or settled commissions.

The FTC's commercial-email primary-purpose rules cover promotional content in the email, including promotion of a commercially operated website. Two explicit commercial slots do not automatically exempt the other four letters: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . The independent general mindfulness background at https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety does not prove Zen12's product-specific effects.

## Reconstruct the actual acquisition → purchase boundary

1. Grok/Praxxis provides published immutable asset_id and platform. Canonical social tagging is utm_source=actual platform, utm_medium=organic_social, utm_campaign=cluster_pilot_2026_11, utm_content=verified asset_id. Claude integrates existing native analytics, not a second script.
2. Visitors reach documented investigation or Focus. Visible "download" and /focus/?subscribe=pending do not show provider-confirmed subscription. The published Dispatch and Focus opt-in copy do not currently express identical commercial expectations; see R260 draft for proposed, **unpublished** wording.
3. Only the actual provider's confirmed, consented, deduplicated subscriber status supports the confirmed_signup event. Jetpack total 3, confirmed diagnostic 3, unconfirmed requests 2, WordPress.com followers 3, and email-only followers 0 are NOT an additive list. Eligible email recipients remain UNKNOWN.
4. Issue 03, **if eventually approved**, uses exactly one first-party, live, independent guide as its principal CTA. Mind & Affiliate Studio (#171) owns guide acceptance and exact merchant earning link. The guide discloses possible FV commission beside any earning link and separately warns about seller email-list signup if applicable. No direct vendor free-audio link in an unapproved Dispatch email.
5. The vendor separately handles customer checkout. Affiliate outbound click, vendor free-download registration, started checkout and even prospective commission entries are **not** independently settled sales. Commerce reconciles paid transactions, refunds, fees and commissions before reporting net realized revenue, by 7/30-day cohorts. Revenue per 1,000 qualified human sessions is NOT COMPUTABLE without verified denominators and orders.

## High-impact release blockers (owner/evidence)

| Offer → funnel step | Blocker | Change / experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Zen12 → FV guide → merchant | Partner approval, exact earning URL, email permission and live guide absent | Authenticate written named account/email rights, source and buyer guide before authorizing any link | HARD HOLD; official marketing copy alone fails | Mind #171 |
| Zen12 seller free-audio | Second newsletter signup concealed if treated as a free trial | Include vendor-list notice in approved first-party guide | Seller's words verified, downstream opt-in untested | Mind |
| Hypnosis Live → checkout | Contradictory observed prices; product claims not verified | Check exact verified account-specific checkout and terms; omit numbers from emails | NOT VERIFIED | Mind + Commerce |
| Focus → Dispatch | Confirmed recipient and welcome receipt unresolved | Provider-filtered private aggregate plus deduped event contract | UNKNOWN | Claude/Focus #129 |
| Dispatch → inbox | Final Vestige address, effective unsubscribe and actual received rendering missing | Non-sending native preview if safely available; separately authorized MIME test only | NOT VERIFIED | Dispatch / Site QA |
| Creator → paid sale | No reconciled commission/refund evidence | Match actual asset/campaign to independently settled transaction | KPI NOT COMPUTABLE | Praxxis/Commerce |

## Safety and existing ownership

Connected Gmail searches on Nov 10 returned no matched Final Vestige-specific Inspire3 affiliate-approval / email-permission confirmation in the searched messages; this is *absence of matched evidence*, not proof of nonapproval. A previously observed October 25 WordPress **confirmation request** is not proof of Fieldbook welcome receipt. The current WordPress welcome text is configured for a 52-page Fieldbook, auto new-post sending is OFF, and last five posts have not been mailed. No test email or subscriber account was created. Do not use vendor or Automattic addresses to satisfy Final Vestige's sender postal requirement. This R263 branch does not touch homepage PR #49 or Claude/Grok production ownership.

The structured review snapshot and machine-checked guard are in OFFER_ROUTE_CONTRACT.json / route_contract.js. The validator must be run natively with `node dispatch/r263/route_contract.js` and the dedicated tests with `node --test dispatch/r263/route_contract.test.js` before production review. Offline code checks alone are not a Jetpack preview, legal signoff or merchant authorization.
