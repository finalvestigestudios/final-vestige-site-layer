# R459 — Live first-party audience / consent / delivery witness

**Observation:** November 18, 2026 Pacific / November 19, 2026 00:32 UTC, authenticated WordPress read-only. No subscriber addresses saved.

| Source of truth | Observation | Correct interpretation |
|---|---|---|
| Jetpack Newsletter status | `subscribers.total=3`; `confirmed=3`; `unconfirmed=2`; suppressed0, paid0, imports_last_24h0 | The tool's `total` is not the sum of confirmed and unconfirmed; do **not** manufacture five people |
| Stats Subscribers filtered records | `all.total=3`, three returned `status=Subscribed`, `email_subscriber=true`; separate email filter returns three | Three provider-marked subscribed email-eligible records; external reach and consent provenance unproven |
| Stats Followers | `email=0`, `wpcom=3`, `partial=false` | Contradicts Stats Subscribers by classification, not proof of three additional people |
| Newsletter settings | `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`, sender `Final Vestige Studios` | Technical send ability is NOT consent, founder release permission or legal compliance |
| Last five email notifications | `never_sent_opted_out`, `dispatched_at=null`; never sent by site setting | Zero evidenced newsletter post sends on latest five, not proof future delivery |
| Welcome | Configured 52-page PDF link at `https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf` | Configuration only; receipt, attachment/open, delivery and attribution unverified |
| Live landing copy | `/dispatch/` and `/focus/` promise mail “when we publish”; current defaults OFF. `/focus/` recovery suggests re-signup for download difficulty | Accurate live site copy and consent are unresolved; prepared redlines remain in earlier R458; owner Claude/Focus must approve and deploy separately |

### Reconciliation method, read-only
Ask WordPress/Jetpack to explain the disjoint `Stats Followers` / `Stats Subscribers` definitions for this blog ID **256784396**, including whether the same three rows are Reader+Email simultaneously, and what `total=3,confirmed=3,unconfirmed=2` means. Recheck privacy-safe per-record *status transitions* privately, never export addresses or IDs into issue comments. Do **not** add the 0/3 + 3/0 cells, and do **not** claim three newly acquired external subscribers.

### What would prove an actual `confirmed_signup`?
A genuinely new, independently witnessed Jetpack subscription record transitions from unconfirmed to confirmed **with consent to Dispatch**, a unique provider-side source-time and allowed channel provenance. Exclude existing subscribed people, Reader-only follows, duplicate form attempts, unconfirmed submissions and PDF downloads; deduplicate before emitting exactly **one** `confirmed_signup`. The owner must avoid personal identifiers in the exported aggregate. A received welcome including a working 52-page PDF link is a **separate** witnessed event, not implicit in confirmation.

**No actual subscription test, email send, welcome receipt, browser delivery, settings edit or subscriber export was performed.**
