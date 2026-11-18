# R454 — private WordPress/Jetpack provider discrepancy escalation (DRAFT ONLY; NOT SENT)

## Evidence at 2026-11-18 19:32 UTC — same site 256784396

| Read-only WP source | Observed aggregate | Semantics we can assert |
|---|---|---|
| Newsletter diagnostic `status` | total=3, confirmed=3, unconfirmed=2, suppressed=0, paid=0 | Vendor diagnostic buckets; unconfirmed may be additional but cannot sum to a unique 5 |
| Stats Subscribers `filter=email_subscriber` | total=3 | Vendor-list source shows three email-classified records |
| Stats Subscribers `filter=reader_subscriber` | total=0 | Vendor-list filter shows no Reader-only records |
| Stats Followers `partial=false` | email=0, wpcom=3, comment=0, paid=0, total=3 | Summary source calls three WordPress Reader and zero email |
| Stats Emails | posts=[] | No campaign post-email performance rows; does **not** establish welcome receipt or customer activity |
| Newsletter `recent_sends` | Five statuses `never_sent_opted_out`; sent fields null | No post notifications sent for those five; **not** a zero welcome delivery assertion |

**Classification conflict:** Email bucket mismatch (Stats Subscribers 3 vs Stats Followers 0), Reader bucket mismatch (Stats Subscribers 0 vs Stats Followers 3). Different endpoint definitions, caching and user-state projections may be involved; we do not know which. Do not subtract one source or invent migration into the other. The reported total of three is not proof of three independently acquired external humans. The 2 unconfirmed are excluded and must not be counted as deliverable.

## Exact questions for private WordPress.com support (no ticket created)

1. Do Newsletter diagnostic `total` and `confirmed` count the same population as Stats Subscribers filtered `email_subscriber`? When `total=confirmed=3` but `unconfirmed=2`, are the two unconfirmed *inside* or *outside* total? Which cohort is deliverable?
2. Is the Stats Followers `email=0,wpcom=3,partial=false` summary sourced from a different cache or subscription-type rule than Stats Subscribers `email=3,reader=0`? Do existing WordPress.com Reader users who opt for emails appear in both types depending on API route?
3. What read-only property, without exposing email addresses, is authoritative for **eligible recipients** for a manual single-post newsletter send? Is there a provider-side aggregate breakdown of `email opt-in vs Reader follow vs delivery frequency`?
4. Does `newsletter.status.site_can_send=true` signify only service availability or actual recipient eligibility? How may a non-sending user preview expose postal address and unsubscribe?
5. Can the founder witness the true rendered welcome (without sending a new welcome or creating a new subscriber) in an authenticated admin UI, and which read-only delivery evidence is available?
6. Is a true user-controlled **preheader** supported by the native Jetpack Newsletter for this site? Or does the inbox preview derive from the post body?

**Support data policy:** Only site ID/domain, UTC capture times, provider screen names/paths, aggregates, error codes and redacted screenshots. Do NOT put subscriber emails, names, IPs, consent tokens, private status entries or account screenshots into a public GitHub issue. This document authorizes no external communication.

**Acceptance:** Written provider explanation linked privately; repeat three aggregate read-only calls within same minute after explanation; record changed vs unchanged; never mark a real confirmed_signup solely because one count went up or one WordPress list changed. A **new provider-confirmed transition** and consent evidence are needed. No list imports or settings changes.
