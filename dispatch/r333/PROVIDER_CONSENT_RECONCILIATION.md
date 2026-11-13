# Provider truth: consent and subscriber-count reconciliation
**Read-only provider evidence at 2026-11-13 16:29–16:30 UTC. No subscriber addresses read or exposed.**

## Three different metrics — do not add them
- Jetpack Newsletter diagnostics: `total=3`, `confirmed=3`, `unconfirmed=2`, `suppressed=0`, `paid=0`. Since `confirmed + unconfirmed > total`, these counters are *overlapping, stale, differently scoped or otherwise semantically non-additive*. No exact number of unique email-eligible recipients can be established.
- Jetpack follower aggregate: **WordPress.com=3**, **direct email=0**, **comment=0**, `partial=false`. These are different aggregate categories, not a recipient-level reconciliation. Neither "zero eligible" nor "three eligible" follows from them.
- Signup mail observed in a connected inbox: **2026-10-25 "Confirm your subscription"**. It proves an email requesting confirmation existed; it does **not** prove a confirmation click, final welcome email, download receipt or enrollment of every follower. Fresh targeted Gmail searches through Nov 13 did not identify a received Fieldbook welcome. No addresses leave the connected inbox; search results are private evidence, not exportable subscriber rows.

## Existing live WordPress settings
Newsletter `subscriptions=true`; `site_can_send=true` and `send_blockers=[]` indicate capability **not** approval. `email_new_posts_by_default=false`, `email_content_format=full`, `from_name=Final Vestige Studios`, `reply_to=no-reply`, `newsletter_categories_enabled=false`. The five recent example posts were each `never_sent_opted_out` (not a proof of zero lifetime sends). The welcome body contains the full 52-page Fieldbook PDF URL, but *configured is not delivered*. On /dispatch/, a subscribe block and conditional-confirmation explanation are published; /focus/ is published. Editor preview differs from received-email proof.

## Exact event contract, without a second tracker
- `signup_attempt`: interaction with existing Jetpack form; never a lead. Do not retain email or a new unconsented client ID.
- `confirmed_signup`: only a provider-sourced unique confirmed enrollment for the existing Final Vestige subscription and a valid permission state. Event time uses provider confirmation, not click/request/download time. Deduplicate on a *private provider token* under provider access controls; **no hashes of emails in public repo or analytics**. If provider cannot expose permissible confirmation records to Claude/Focus, output `unobservable`, not `0`.
- `welcome_delivered`: requires provider sent/delivered artifact or a **separately authorized** recipient's actual received message. Configured welcome text, a Gmail confirmation prompt and an HTTP 200 PDF response are three different facts.
- `fieldbook_download`: optional, nonproof of enrollment and not a sale. A merchant Zen12 gift signup and checkout SMS are each **merchant-controlled consent**, never Final Vestige confirmed signup.
- `unsubscribe`: requires an actual Jetpack message opt-out mechanism and verified processing. A placeholder or generic settings page is not proof.
- `merchant_confirmed_purchase`: recorded only from authentic seller/affiliate settlement evidence (transaction ID, paid date, commission, refund/fees); an affiliate click or mere order intent is not a purchase.

**Privacy:** Report totals or tiny-sample-suppressed counts, not per-recipient histories, email addresses, IPs, email-derived hashes, receipt message headers, or private merchant earning URLs in a public PR. For counts this small, avoid cohort percentages and A/B inference.

## What would actually reconcile the counts
A qualified owner with legitimate access must inspect WordPress/Jetpack's **private** subscriber-management statuses, eligibility for post notification (WordPress.com Reader vs direct email and notification-frequency controls), possible pending invitations/import statuses and confirmation-state semantics. Only compare same-time unique, permission-scoped provider records; supply a *redacted summary* with separate counts and methodology, not the list. Until those records can lawfully be reviewed, retain **eligible recipients: UNKNOWN**. The campaign cannot be released on aggregate arithmetic.

## Legal and actual inbox witness
Commercial sends require Final Vestige's verified legitimate postal address, lawful clear affiliate/ad disclosure and an actually operable unsubscribe in the provider-delivered message. Inspire3/Automattic addresses are *not* Final Vestige's address. The FTC explains postal and opt-out duties: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . WordPress explains *Preview email* is available with Send toggle OFF; preview is **not** receipt: https://wordpress.com/support/newsletter/email-appearance/ . WordPress docs say the post title supplies the email subject and the sender address normally is `donotreply@wordpress.com`: https://wordpress.com/support/newsletter/send-newsletter-emails/ and https://wordpress.com/support/newsletter-settings/ . No WP native preview/real received email was obtained or test message authorized this run.

**HARD HOLD:** Founder must separately approve any inbox test, audience, schedule and final creative; even an authenticated preview must never be mistaken for permission to send.
