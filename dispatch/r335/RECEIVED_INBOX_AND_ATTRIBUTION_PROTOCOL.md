# R335 native welcome-receipt / subscriber-eligibility acceptance protocol

**Read-only specification; NO EMAIL SEND AUTHORIZED.** No new list, subscriber exports, WordPress edits, analytics pixels or test messages. The configured welcome and the on-page PDF download already exist. A genuine received message is still unverified.

## Source-of-truth for consent
- Site 256784396. Inspect private WordPress.com Subscribers → Email subscription status, not just combined follower count. A status such as Not confirmed, Bounced, Emails paused or Not sending cannot be counted as deliverable.
- Mode A: non-WordPress verified account completes provider email confirmation. Mode B: previously verified WordPress.com account skips a new challenge, but still needs explicit enrollment in **Final Vestige Dispatch** and provider Subscribed status. Do not invent a second link-click requirement.
- A confirmed_signup is a *verified provider transition* into subscribed/consented state. If the transition timestamp is unknown, retain an eligibility snapshot, not a fabricated new lead. Dedup privately using the provider's opaque stable identity in authorized infrastructure, not a GitHub email/hash.
- Public on-page Fieldbook download does not show sign-up, and a merchant's Zen12 gift sign-up gives no permission to email from Final Vestige. WordPress.com follower classification alone is not a deliverable email subscriber count.

## Existing welcome vs actual inbox acceptance
1. Confirm settings show the expected 52-page PDF URL and accurately report **CONFIGURED** only.
2. Inspect an *already received* welcome email privately only if a founder-authorized inbox specimen exists. Verify actual arrival, link accessible to that recipient and correct site sender. The 2026-10-25 confirmation request found in prior Gmail inspection is not this welcome.
3. No recipient address, screenshot showing subscriber identity or MIME raw headers may be written to GitHub. Only a coarse, source-dated **PASS / FAIL / NOT RUN** with approved witness may be reported.
4. A WordPress native preview does not establish delivery. After the founder explicitly authorizes a safe test email, compare the final post title-derived subject, rendered full content, visible near-offer commercial disclosure, valid publisher *physical* mailing address, and functioning unsubscribe in an actual received message. Test opt-out only for a specific founder-controlled test account with approval.
5. A visible unsubscribe link or hypothetical List-Unsubscribe header alone does not prove the mechanism actually works. A merchant or Automattic postal address is not the verified publisher address for Final Vestige.

## Attribution discipline
Proposed convention, subject to Claude's existing implementation and privacy review: event confirmed_signup + first-party campaign identifier dispatch_pilot_2026_11 + issue_id + primary CTA ID. No per-recipient token; Grok asset_id from verifiable actual published media only. Confirmed leads, PDF clicks, merchant signups, email clicks and paid orders stay separate.

| Observable | Can demonstrate | Cannot demonstrate |
|---|---|---|
| Signup form click | Interest | Provider-confirmed consent |
| Provider Subscribed status + verified path/consent | Eligible state; new signup ONLY if provider transition proven | Inbox delivery or customer |
| Fieldbook download | Reader accessed a useful resource | Dispatch consent or welcome delivery |
| Received welcome | Delivery to the specifically witnessed inbox | Delivery to all subscribers |
| Email/guide/affiliate click | Interest in next step | Merchant settlement |
| Independent settled order + fees/refunds | Realized revenue | Attribution without a legitimate join to qualified traffic |

### Release-critical checklist
- [ ] Founder approval of exact six final manuscripts, recipient eligibility, schedule and SEND.
- [ ] Final Vestige-owned valid postal mailing address in received commercial email.
- [ ] Legal sender identity, truthful subject, conspicuous disclosure and functioning opt out.
- [ ] Exact Inspire3 account acceptance and EMAIL marketing rights, issued URLs and two live first-party guides.
- [ ] Real WordPress received-email HTML/plaintext rendering and no unfilled placeholders.
- [ ] Privately verified consent+Fieldbook welcome; no co-mingling merchant opt-ins.
- [ ] Paid orders and net revenue verified by settlement records; denominators human-qualified.

**Current outcome: HOLD_UNSENT all six, HOLD_MERCHANT 03/05, real qualified-session denominator UNKNOWN, net revenue per 1,000 NOT COMPUTABLE.**

Source documentation: https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/subscribers/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .