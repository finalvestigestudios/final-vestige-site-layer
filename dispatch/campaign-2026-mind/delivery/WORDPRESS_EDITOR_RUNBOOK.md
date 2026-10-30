# The Dispatch — WordPress/Jetpack editor release runbook (NO SEND AUTHORIZATION)

**Draft QA only, 2026-10-30.** Issue #174; stacked review PR #178. The runbook does not authorize creating/publishing WordPress posts, sending test messages, changing settings or contacting subscribers.

## Verified WordPress state

- Site ID 256784396: subscriptions enabled, sendable, newsletter send-by-default OFF. Current setting `email_content_format=excerpt`. Sender displays `Final Vestige`, reply-to is `no-reply`; welcome copy links to the 52-page Focus Fieldbook; recent sends = none.
- Subscriber totals are not internally consistent: `total=2, confirmed=2, unconfirmed=2`. DO NOT infer four recipients or claim two verified deliverable recipients.
- The public `/dispatch/` and `/focus/` pages are published. No live settings or content were changed.

**Critical newly confirmed behavior:** WordPress.com says excerpt mode with no custom excerpt sends only the *first 55 words*. A custom post excerpt is sent instead when supplied. Thus the six 175–300-word dispatch drafts cannot be assumed to reach inboxes intact. Subject is the WordPress post title; a standalone preheader is not established by the editor API. The existing static HTML previews are NOT actual Jetpack MIME.

Official support references (reviewed in October 2026):
- https://wordpress.com/support/newsletter-settings/
- https://wordpress.com/support/newsletter/email-appearance/
- https://wordpress.com/support/newsletter/send-newsletter-emails/
- https://wordpress.com/support/subscribers/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Preferred mode: full newsletter in the inbox, IF separately authorized

Recommend full-text delivery for the editorial six-issue pilot, because the message includes important evidence and commercial disclosures before the CTA. But `email_content_format=full` is a SITE-WIDE change and could affect unrelated posts. DO NOT CHANGE it without the founder's explicit consent. The chosen per-post newsletter toggle must remain OFF until an independently authorized draft preview or actual send.

## Fallback with zero settings change

Use the six human-edited custom excerpts in `delivery/wordpress_excerpt_copy.json` and let Jetpack's built-in read-more link bring recipients to the full post on finalvestige.com. This is a teaser-first, not full-letter, experience. Do not assume custom excerpts support HTML links or a separately configurable preheader. Issues 03/05 include an affiliate disclosure inside the excerpt, in addition to the disclosure required next to actual merchant earning links on an independently verified guide. Each issue retains one primary reader action.

## Preview path requiring explicit separate approval

1. In the founder-authorized WordPress account, create an UNPUBLISHED post draft. Copy the subject into the post title. Do not schedule/publish.
2. Open the paper-airplane Newsletter panel. WordPress support says turning on `Send this post to subscribers` *for the unpublished draft* exposes Preview email and Send test email. Only do this for approved preview work; return it to OFF before leaving the draft.
3. Use `Preview email` for desktop/tablet/mobile and verify full-vs-excerpt body, source links, disclosure position, primary CTA and footer. That preview is NOT a delivered-email test.
4. DO NOT press `Send test email` unless the founder has explicitly approved a test recipient. For an authorized received test, check MIME/header, sender, mobile/desktop, physical business address, one-action unsubscribe and link targets. Keep a non-sensitive QA record.
5. Do not publish, schedule, change global settings, import subscribers, or activate the affiliate CTA without independent founder approval of content, audience and exact send date.

## Blockers the code cannot solve

- **Postal and opt-out:** The received commercial newsletter must include Final Vestige's valid business postal address (not Inspire3's address) and an actually functional unsubscribe method. No invented home address. The placeholder preview footer proves nothing about Jetpack's real footer. FTC permits appropriately registered US PO boxes or commercial private mailboxes.
- **Real audience:** In Jetpack → Newsletter → Subscribers, filter by `Email subscription` and account for bounced/paused/pending. The connector cannot reconcile those states. Never store subscribers' personal details in this repository.
- **Affiliate permission:** Public Inspire3 recruiting copy does not prove FV approval, email-marketing rights, precise destination or conversion tracking. An October 30 Gmail search showed consumer marketing from related brands but no matching approval; that's NOT conclusive. Verify the authenticated account privately.
- **Offer pages:** Zen12's guide is currently a draft in Mind Studio PR #180; Hypnosis Live guide is not confirmed live. Affiliate URL tokens must remain inert.
- **Founder:** Content/audience/date approval is required separately even if every automated test passes. No autonomous sends.

## Low-count analytics

Use aggregate deliverability, click-through to the site, first-party guide-to-merchant clicks only when privacy policy and partner rules allow, merchant-confirmed orders/refunds, unsubscribes and complaints. Never present open rates as proof of attention or tiny-sample A/B differences as statistical gains.
