# R452 — Three WordPress audience views disagree on classification (private-data-safe)

**As observed:** 2026-11-18 17:35 UTC (09:35 Pacific). Authenticated, read-only WordPress connector, one site `https://finalvestige.com` (blog 256784396). No subscriber email, ID, name, or raw provider response is included.

| Independent surface | Query/filter | Reported count | Meaning in provider description |
|---|---|---:|---|
| Newsletter diagnostics | total | 3 | Newsletter-facing summary |
| Newsletter diagnostics | confirmed | 3 | Confirmed within newsletter diagnostic |
| Newsletter diagnostics | unconfirmed | 2 | Additional pending records; **not addable to total** |
| Stats Subscribers | `all` | 3 | Three rows with `status=Subscribed,email_subscriber=true` |
| Stats Subscribers | `email_subscriber` | 3 | Same subscribed email-eligible classification |
| Stats Subscribers | `reader_subscriber` | **0** | No Reader-only rows in this filtered list |
| Stats Subscribers | `unconfirmed_subscriber` | 2 | Two `Not confirmed` records, excluded |
| Stats Followers | `email` | **0** | Aggregate email followers per Stats definition |
| Stats Followers | `wpcom` | **3** | Aggregate WordPress.com Reader followers per Stats definition |
| Stats Followers | `total` | 3, `partial=false` | Sum of source categories reported by that endpoint |

**Newly isolated contradiction:** the two Stats endpoints disagree about both classes, not only the email count: filtered subscriber rows classify three as email-subscribed and zero as Reader-only; the Followers rollup classifies zero email followers and three WordPress.com followers. Neither endpoint is known to be authoritative for real delivery. These are *provider surface classifications*, not evidence of three independent external humans or successful inbox delivery. We cannot assume the same three identities overlap across the two views without a private, authorized, source-to-source identity reconciliation.

**Do not fix with arithmetic:** `3 confirmed + 2 unconfirmed` is NOT five deliverable people. `wpcom=3` does NOT prove three distinct non-email followers. `email=0` does NOT erase three `Subscribed,email_subscriber=true` rows. `site_can_send=true` is a site capability, not permission to send or deliverability evidence.

**Corroborating configuration:** Newsletter enabled; `email_new_posts_by_default=false`; `email_content_format=full`; reply-to `no-reply`. The five recent posts are `never_sent_opted_out` with `send_subscription flag is false`. The welcome has the 52-page Fieldbook PDF URL configured. The received welcome, native Jetpack Preview, publisher postal address and actual unsubscribe footer remain **unverified**. The published /dispatch/ page says investigations arrive when published, which is stronger than the present default-off practice. The /focus/ page offers the same one subscription list and direct free PDF.

**Private, non-sending investigation for Focus/Claude:** (1) in the authenticated subscribers UI, compare provider subscriber-category definitions and timestamps to Stats Followers; (2) determine whether Reader and email metrics reflect separate underlying datasets, stale caches or migrated classifications; (3) document only aggregate outcomes and a screenshot with addresses obscured; (4) if authorized independently, witness a genuine *new* confirmation and received welcome without contacting an existing subscriber or importing addresses; (5) observe real native post-editor Preview without triggering any email. No test-send authorization is inferred.

**Metric rule:** `confirmed_signup` is a *new confirmed transition*, deduplicated by the provider under a private scope, not a present inventory row, Reader follow, form attempt or PDF click. `merchant_paid_conversion` requires independently settled merchant reporting; deductions for refunds and fees and a verified qualified-human-session denominator before net revenue/1,000. Both remain **NOT COMPUTABLE**, never zero by assumption.

**Sources:** read-only first-party WordPress Newsletter status/settings, Stats Subscribers (all/email/reader/unconfirmed) and Stats Followers at timestamp above; [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). This report publishes **aggregate figures only**, not private subscriber data. No WordPress write, send or testing contact occurred.
