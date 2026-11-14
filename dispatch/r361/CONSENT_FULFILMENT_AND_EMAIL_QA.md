# Read-only consent → welcome → receipt QA; no use of subscriber identities

## WordPress source of truth (2026-11-14 19:39–19:40 UTC)

Authenticated `wpcom_jetpack_newsletter(status/get_settings)`: enabled and technically able to send; `email_new_posts_by_default=false`, `email_content_format=full`, sender display 'Final Vestige Studios', `reply_to=no-reply`. Configured welcome contains the exact Fieldbook complete-edition PDF URL. Recent five post notification records say `never_sent_opted_out`; recipient fields are **null**, not 0.

Subscriber dashboard gives total=3, confirmed=3, unconfirmed=2, suppressed=0. Follower surface gives WordPress.com=3, direct-email=0. These are different reporting views and appear overlapping; don't sum counts, assume who is reachable, or infer that 0 email followers means no inboxes. Query authenticated provider lifecycle privately: invitation requested, confirmed timestamp, address type (WP.com user vs external), current opted-in state, suppression, bounce/reachability, eligible audience for this specific post. Deduplicate stable opaque subscriber IDs. No list exports or email addresses committed to GitHub.

**Connected mail:** read-only Gmail searches located a 2026-10-25 *Confirm your subscription* request. This alone does not prove completion, the final welcome, any campaign render or affiliate authorization. Other targeted searches yielded no independently identifiable actual welcome, but absence in the queried mailbox is NOT evidence that no other mailbox received it.

**New physical asset check:** WordPress media-library exact-title search found attachment **ID 1737**, `application/pdf`, 599,946 bytes, URL:
`https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf`
This matches the configured welcome and the /focus/ page's download destination. It proves the media item is listed, **not** that an anonymous visitor or confirmation recipient actually retrieved the bytes. A public web PDF fetch failed with a cache miss; classify actual browser download as **UNKNOWN**, not 404 or success. Don't tell existing subscribers to sign up again until duplicate/consent behavior is clarified.

The public /dispatch/ page currently presents a Jetpack email-input/Subscribe control in the web retrieval; the WordPress `view` API represents its block as a same-page Subscribe link. Those render representations differ. A real no-submit guest-browser inspection remains required; neither representation proves subscription completion.

## Owner-only acceptance steps without sending

1. Claude/Focus: use WordPress's actual private subscriber administrative UI to reconcile categories and confirmation state, report **aggregates only** and one deduplicated `confirmed_signup` event contract, never upload subscriber PII. Snapshot existing settings and avoid mutation.
2. Focus/Founder: inspect the original welcome message/template. A known existing message can be read privately to verify Fieldbook content and sender; a confirmation **request** is not welcome receipt. Actual received welcome cannot be claimed without the recipient's independent evidence and permission.
3. Site QA: in authorized browser, test the public PDF GET/download in mobile Safari/Chrome and direct desktop browser, checking response, size, PDF page count, download affordances and accessible fallback. Do not submit a real email or create a duplicate registration.
4. Dispatch/Founder: inspect a real WordPress **Preview email** in the native editor (desktop/tablet/mobile), preserving send OFF. This is not the same as a genuinely received email. An actual 'Send test email' is a send and remains expressly unauthorized.
5. Founder: provide a legitimate FV publisher business postal address via protected settings/release workflow (no fabricated address, no addresses in public issue). Verify actual final rendered footer includes it, honest sender, and conspicuous opt-out. A WordPress/Automattic address in a confirmation email is **not** FV's business postal address.
6. Site QA with express future authorization: independently verify the opt-out destination functions and suppresses future commercial messages, without touching uninvolved subscriber accounts.

## Regulatory and publishing boundary

[FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): applicable commercial messages need truthful headers/subjects, a valid *publisher* postal address and clear opt-out; opt-outs must be honored within statutory requirements. Subscriber membership does not automatically exempt marketing emails. [WordPress Preview email guide](https://wordpress.com/support/newsletter/email-appearance/): 'Preview email' and 'Send test email' are distinct operations, and only the latter transmits mail. Even a technically sendable WordPress site is not legally/editorially ready to contact its audience. All editions stay HOLD_UNSENT.