# Subscriber counter reconciliation — WordPress semantic explanation, not audience verification

**Date checked:** 2026-11-02 UTC. **No subscriber identities, email addresses, screenshots, exports or contacts examined.** This is a non-identifying documentation and API-semantic analysis only.

## Observed authoritative read-only site status

Authenticated WordPress site `256784396`, `finalvestige.com`, Newsletter `status` at **2026-11-02T02:36:06Z**:

```json
{
  "total": 2,
  "confirmed": 2,
  "unconfirmed": 2,
  "suppressed": 0,
  "paid": 0,
  "imported_last_24h": 0,
  "recent_sends": [],
  "email_new_posts_by_default": false,
  "email_content_format": "excerpt"
}
```

Only aggregate counters are recorded. The `email_new_posts_by_default` and `email_content_format` are from the separate authenticated `get_settings` observation at **02:36:03Z**.

## The apparent 2 / 2 / 2 discrepancy is explained

**Official WordPress.com subscriber guidance, reviewed October 26, 2026, expressly states that “Not confirmed” registrations *are not counted toward the total subscriber count*.** It also says `Bounced`, `Emails paused` and `Not sending` subscriptions *still count* in the total despite being unable to receive immediate email. Source: https://wordpress.com/support/subscribers/ .

Therefore **total=2, confirmed=2, unconfirmed=2 is not, on its own, a mathematical inconsistency**. The `unconfirmed` measure is not a disjoint component to add to the total. The prior sprint language calling this an intrinsically contradictory or internally inconsistent result was **too strong** and should be corrected in later reporting. The API counters do not establish that there are exactly four distinct human beings, four reachable inboxes, or even two actively deliverable email subscriptions.

This resolves only the interpretation of the counters. **The unique, consented, immediately email-eligible recipient count remains UNKNOWN**.

## Exact next read-only verification, in private site administration

WordPress officially instructs operators to navigate **Jetpack → Newsletter → Subscribers**, then filter on **Email Subscription** and check which subscribers are opted in and eligible to receive email, not simply follow the total number. This also distinguishes `Not subscribed` Reader followers, `Not confirmed`, `Bounced`, `Emails paused` and `Not sending`. Reference: https://wordpress.com/support/subscribers/ . WordPress's troubleshooting guide also says email delivery preference (instant vs daily/weekly) matters: https://wordpress.com/support/troubleshooting-not-receiving-notification-emails/ .

That private filtered review has **not** occurred. No subscriber export, import, resend-confirmation action or member contact is authorized. If an administrator later performs the review, record only: UTC timestamp, filter definition, number `Email subscription = Subscribed` **and** delivery status eligible, any additional exclusions, and a private source-of-truth proof reference. Do **not** publish emails, names, WordPress usernames, identifiers, row screenshots or tokenized subscription links.

## Decisions this evidence can and cannot support

**Supported:** the counters are nonadditive by WordPress design; `unconfirmed` registrations are excluded from total and are not receiving newsletters until confirmed.

**Still unverified:** which of the two counted/confirmed registrations are email-enabled, non-bounced, non-paused, actually consenting to this campaign scope and reachable; successful delivery of the updated Fieldbook welcome; unsubscribe function; legal address; merchant permissions; final send approval.

**Result:** `SUBSCRIBER_COUNTER_ARITHMETIC_EXPLAINED` but `AUDIENCE_ELIGIBILITY_HOLD`. Do not alter the live subscriber list or re-send confirmation messages to force a metric to change. Under the founder's draft-only approval, **all six issues remain HOLD_UNSENT**, with #03 and #05 also **HOLD_MERCHANT**.

This finding should replace repetitive claims that `2/2/2` is self-contradictory, while retaining the real requirement for private eligibility verification.
