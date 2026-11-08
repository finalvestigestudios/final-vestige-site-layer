# R189 — safe WordPress email and legal inspection (NO SEND)

This is a reviewer runbook, not permission to operate a live subscriber workflow or a legal signoff.

## Read-only evidence gathered (2026-11-07 16:33 UTC)
- Newsletter: enabled, can send, automatic new-post mail **off**, full-content format, sender display name Final Vestige Studios, reply-to no-reply. Last five posts marked `never_sent_opted_out`, no actual mail recipients or successful sends reported.
- Counted subscribers 3, confirmed 3, pending requests 2, suppressed 0; NONADDITIVE. Actual email-eligible audience UNKNOWN, needs provider-filtered status `Subscribed` without exporting identifying fields.
- Welcome already configured with 52-page Fieldbook PDF; **genuine recipient delivery unknown**.
- Current published source pages: `/dispatch/` page ID 523, `/focus/` page ID 1579, `/editorial-standards/` page ID 17.
- Exact source seller Total Focus: https://hypnosislive.com/mental-skills/total-focus , seller describes 33-minute/47-MB and promises 100% concentration, neither efficacy nor checkout verified.
- No Final Vestige-specific affiliate email permission or validated live first-party guide observed. Prior connected Gmail search found a WordPress *subscription confirmation request*, NOT a delivered welcome email or merchant terms. New targeted Gmail searches have not produced qualifying partner approval.

## Highest-value verification in genuine UI — never click a send control
WordPress documentation current October 2026 describes `View → Email preview` for **an already published post** in the Email Design editor; this route might reveal actual native markup without altering a per-post send flag. Investigate using a read-only connected browser that is already authorized. DO NOT toggle "Send to subscribers" merely to make the preview appear; do not click "Send test email," "Publish," "Schedule," or configure a list.

Record whether a preview actually opened for *this site*, what subject it uses, whether the proposed preheader appears (Jetpack's separately editable preheader has **not been verified**), actual sender identification, branding/dark-mode/mobile wrapping and visible merchant/source disclosures. Native preview may not contain a recipient-specific unsubscribe token or actual delivered MIME: record that as UNVERIFIED, not PASS.

The Email Design interface may alter persistent styles. **No edits or saves**. The fact that `reply_to=no-reply` is configured is not a legal failure by itself; unsubscribe must be independently provided and operative.

## Genuine received-message and mailing address gate
- Do not email a subscriber or send a real test without the founder's **specific final permission** for that test and its recipient. Account owner mailbox receipt is not implicit consent to deliver a new message.
- Once authorized later, compare delivered HTML/text, sender fields, explicit commercial advertising identification, valid **Final Vestige physical postal address** (not Automattic's in its subscription confirmation nor merchant's), opt-out UI and unsubscribe functionality. Avoid logging actual addresses, message IDs that expose private links, unsubscribe tokens, raw recipient MIME or campaign subscriber data to GitHub.
- CAN-SPAM primary-purpose analysis depends on email presentation, not only its 4:2 editorial plan. Commercial Issue 05 must clearly disclose its relationship immediately beside the prospective recommendation. Under FTC guidance a valid postal address and opt-out are required for commercial mail: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Test one authorized **existing confirmed subscriber** whose consent permits promotional email, if available, not a fabricated email address and not an imported list. Proof must be privacy-safe and minimal. **Never send now.**

## Current release table

| Fact | Status |
| --- | --- |
| Original six-issue pilot 4 editorial / 2 commercial | BUILT/UNSENT; PR #175 unchanged |
| Independent per-issue QA #201 | BUILT/STATIC_TESTED; not production email |
| R189 optional alternative / source claims | BUILT; REVIEW_ONLY |
| Publisher acceptance, email-channel rights, permitted link | UNVERIFIED / HOLD_MERCHANT |
| Live Mind buyer guide | UNVERIFIED / NO ACTIVE CTA |
| Genuine Jetpack preview and delivered footer | UNVERIFIED |
| Valid Final Vestige address and working opt-out | UNVERIFIED |
| Provider consent/opt-in and delivered welcome | UNVERIFIED |
| Verified settled commissions and qualified humans | UNAVAILABLE / NOT COMPUTABLE |
| Founder final creative + exact audience + schedule approval | NOT GIVEN |
| SEND ALL SIX | **HOLD_UNSENT** |

WordPress references: https://wordpress.com/support/newsletter-email-design/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ .
