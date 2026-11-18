# Private provider witness checklist — no PII in GitHub

This is an internal procedure, not a request to send an email. Do not enter subscriber names, addresses, subscription URLs, login tokens, browser screenshots containing identities or raw confirmation links in source control.

1. Capture Jetpack Newsletter settings/status and Jetpack Stats Followers at the same visit. Record time and snapshot identifier. Distinguish total, confirmed, excluded unconfirmed, Reader and direct-email follower counts.
2. In Subscribers, filter to **Email subscription: Subscribed** and record *only the aggregate count*, timestamp, filter name, and opaque private proof reference. Also count aggregate Not subscribed, Not confirmed, Bounced, Emails paused, Not sending, if safely visible; counts across labels may not be additive due UI filter semantics. Do not export the list.
3. If zero direct email followers but positive filtered Subscribed, mark discrepancy; investigate rather than overriding either value. If filtered zero, record verified zero at that snapshot, not universal lifetime zero.
4. Check existing opted-in mailbox for the actual Fieldbook welcome and PDF URL without generating any new mail. A WordPress confirmation message by itself is NOT the configured welcome.
5. In post editor use **Preview → Email Preview**, if available without changing content, to inspect title-derived subject, preheader/snippet, actual first paint, sender, FV publisher postal address, unsubscribe, contrast and mobile clipping. **Do not select Send test email, Publish, Schedule, or Email subscribers.** If preview requires a draft write, ask founder for separate authorization; this sprint does not authorize it.
6. When Mind owner supplies *account-specific* Inspire3 email-permission letter, approved exact SKUs/links, seller checkout terms and live warm-up-guide URLs, record approved aggregate proof references in private ledger; not just a generic public partner page.
7. Do not mark any email RELEASE_READY; even satisfactory receipts qualify for human editorial review only and require founder explicit final campaign approval.

**Known observed example:** newsletter 3/3/2, follower email 0, Reader 3, filtered Subscribed UNKNOWN; all send/rights/revenue attestations false. `provider_snapshot.json` is an inert example, not an authoritative future fixture.
