# R16 Dispatch: Subscriber-count reconciliation and release-proof gate

**DRAFT, UNSENT, NO WORDPRESS WRITE, NO EMAIL SEND.** Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Parent: draft [PR #274](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/274). Mind & Affiliate owner: [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Master six editions: draft PR #175.

## Verified new finding — stop calling the 2/2/2 counters inconsistent by arithmetic alone

Official [WordPress Subscriber guidance](https://wordpress.com/support/subscribers/) (reviewed **October 26, 2026**) explains that **not-confirmed subscriptions do not count toward the overall subscriber number**. Authenticated newsletter status **2026-10-31 09:32 UTC** showed `total=2`, `confirmed=2`, `unconfirmed=2`. These are **consistent with documented non-overlapping buckets**, e.g. two counted confirmed subscriptions plus two additional pending confirmations. It was misleading for earlier sprint notes to claim a mathematical contradiction or four recipients.

**But** this is NOT proof that two messages can or should be sent. Confirmed WordPress user accounts, WordPress Reader follows, email-eligible subscriptions, suspended/bounced delivery, paid subscriptions and unsubscribed states are not interchangeable. The aggregate connector does not prove which of those two confirmed records is actively opted into email. The program deliberately returns `actual_email_eligible_recipients=null` and `HOLD_UNSENT` even when counts look normal.

## Private, read-only reconciliation (not executed)

In the existing WordPress dashboard, filter **Subscribers** by `Confirmed`, then use email subscription status `Subscribed`; inspect the non-identifying state counts for delivery paused, bounced and email opt-outs, avoiding duplicate classifications. Review `Not confirmed` separately—**never count pending as reachable**. Record aggregate counts and timestamp only in the private review ledger. Do **not** export, upload, print or commit names, addresses, confirmation URLs, IDs, or screenshots that disclose PII. Do not import or invite any new subscriber. If dashboard does not provide per-recipient email opt-in category, report **UNKNOWN** rather than infer.

## Current production settings (read-only)

Authenticated WordPress at **2026-10-31 09:32 UTC**: `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `recent_sends=[]`; configured welcome message still includes the 52-page Focus Fieldbook. The live Gutenberg pages [Dispatch](https://finalvestige.com/dispatch/) (ID 523) and [Focus](https://finalvestige.com/focus/) (ID 1579) both contain native Jetpack Subscribe blocks. This does **not** verify logged-out clicking or welcome receipt. Existing [Editorial Standards](https://finalvestige.com/editorial-standards/) remain historical evidence-first.

## Reproducible source test

```sh
python -I -m unittest discover -s audience-semantics-r16/tests -v
python audience-semantics-r16/audience_guard.py audience-semantics-r16/wordpress_aggregate_20261031.json
```

Run from `dispatch/campaign-2026-mind/`. The auditor accepts **aggregate-only** JSON, returns no PII, rejects invalid input, and never transforms a count into permission to send. **19 adversarial local Python tests** passed in the R16 development container (Python 3.13). Campaign parent R15 previously had **15 exact-SHA-matched locally executed Python tests**, and 13 deterministic preview assets passed the existing Node preview check. These are NOT a full PR checkout, NOT Jetpack-delivered MIME and NOT green GitHub CI.

## Release sequence

First establish genuine public signup browser proof without registering an address; identify Final Vestige's actual valid physical mailing address and inspect opt-out rendering in a founder-authorized **received WordPress email**; reconcile permissioned reachable audience privately. Ensure /focus/ welcome arrived rather than merely configured. Verify WordPress actual subject, excerpt, CTA, disclosure and unsubscribe in message body. FTC commercial-content classification applies as appropriate, including editorial content that promotes a commercial website. Obtain founder-specific campaign approval before any send. No test-send has been authorized.

For commercial #03/#05, Mind Studio must publish the exact-SKU independently sourced warm-up guides and verify written **Inspire3 account acceptance, product-specific program rights, promotional permission by email, authorized link/creative, current offer and checkout claims**. No direct affiliate or publisher CTA is activated in this branch. Original 4:2 allocation preserved and all six **HOLD_UNSENT**. The flagship homepage #49 is untouched.
