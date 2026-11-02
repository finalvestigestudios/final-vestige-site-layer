# Private audience, subscriber count and welcome-flow reconciliation

## What the actual API says (2026-11-02 15:41 UTC)
`total=2; confirmed=2; unconfirmed=2; suppressed=0; paid=0; imported_last_24h=0`. All those keys are **independent categories**, not an arithmetic partition. `confirmed + unconfirmed = 4` does **not** mean four deliverable people. Neither does `confirmed=2` prove two eligible email recipients. `recent_sends=[]` means none appeared in the reported recent window; do not claim lifetime no sends. The configured 52-page welcome message has no independently verified delivered instance.

## Official WordPress mechanism — new concrete resolution path

[WordPress subscriber documentation](https://wordpress.com/support/subscribers/) explicitly says *Not confirmed* are not subscribers for the total; Reader follows may not have email notices; users labelled **Bounced**, **Emails paused**, **Not sending** can count toward follower totals but cannot receive new mail. WordPress's recommended method for a mismatch is to filter subscribers by **Email Subscription** status to identify subscribers opted in and eligible for email.

**Authorized, read-only private procedure (no exports):**
1. Jetpack → Newsletter → Subscribers. First capture aggregated filter counts for **Email Subscription: Subscribed** and **Not confirmed** separately.
2. Inside the subscribed cohort only, inspect **Not sending (any reason)** and status **Bounced**, **Emails paused**, **Not sending**; report counts and, if provided, the resulting deduplicated count. Never infer subtraction where WordPress lists overlap; if filter intersection cannot be confirmed, report `unknown`.
3. Review how each retained recipient originally subscribed (Dispatch investigation expectation vs Focus resource), **without compiling names**. A broad two-offer commercial launch is not authorized merely because someone once followed a history feed. Any needed consent and privacy changes require founder review.
4. Store only `{as_of_utc, total, confirmed, unconfirmed, opted_in_email_count, bounced_or_paused_count, eligible_unique_count, method, screenshots_redacted}` in a private secure evidence note; this GitHub PR deliberately stores `eligible_unique_count: null`.
5. DO NOT download subscriber CSV, reveal email addresses, send a confirmation, invite a new test user, modify user subscription or export recipient data from this lane.

## Welcome: confirmation ≠ gift received

Per [WordPress's welcome message documentation](https://wordpress.com/support/newsletter-settings/), a visitor may first receive an uncustomizable confirmation email; the configured welcome follows confirmed subscription. Existing Gmail evidence on **October 25** is specifically the **confirmation** step—not the finished Fieldbook welcome, not an issue from The Dispatch, and not evidence of correct unsubscribe/address rendering. Never paste its message ID, tokens or addresses into a PR. If founder authorizes a controlled private test of the actual welcome in a separate step, check the first party Focus download target, not merely the presence of the URL in the settings field.

## Business and legal limits

FTC requires valid publisher address in promotional mails and a simple, functional opt-out, even with opted-in lists. The automated Jetpack sender may be `donotreply@wordpress.com`; the public sender display name is configurable. Test the *received* message, not the configured site name. No inference that Automattic's physical address represents this publisher. Allowed address formats can include a qualifying PO Box or private mailbox; none has been supplied/verified. No sending in this sprint.

Official: https://wordpress.com/support/subscribers/ ; https://wordpress.com/support/newsletter-settings/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .