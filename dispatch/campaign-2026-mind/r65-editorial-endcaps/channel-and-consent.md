# R65 — The actual subscriber email is NOT the full drafted issue
**Production-contract review for founder, not an instruction to change settings.**

## The new high-impact gap
On 2026-11-02 11:32 UTC, authenticated Jetpack settings say `email_content_format=excerpt` and `email_new_posts_by_default=false`. The six original PR #175 manuscripts were drafted as full issues with in-body evidence, long-running stories, and final CTAs. Under current production settings, those full manuscripts **will not simply appear as full-length messages** in a recipient inbox. Unless a custom excerpt is provided, WordPress documentation says the email uses the first ~55 words, with a link to the post. A separate editable preheader is not verified in WordPress.com's available newsletter settings, so the beautifully written planned preheader is a draft annotation, NOT a promised delivered field.

Documentation: https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/

### Exact editorial decision required (NO changes applied)
- **Path A: Keep excerpt mode.** Make each email an honest short teaser that takes the reader to the full website post. Use a separately founder-approved custom excerpt. Commercial editions 03 and 05 must clearly signal the potential earning relationship in the excerpt before the reader is led to any product evaluation. Verify the exact Jetpack-generated teaser and final CTA; do not assume a late manuscript CTA appears in the email. Still requires valid publisher postal and opt-out where the law applies.
- **Path B: Full-text newsletter.** A newsletter-wide mode change would affect other unrelated posts' outgoing emails and is NOT authorized. Do not execute. If ever proposed, founder must approve the sitewide side effect, then view a native preview and genuine received email.
- **Path C: Post-specific mechanism.** Do not assume any post-specific full-body override or preheader field exists; official documentation reviewed does not substantiate a per-post full-text control. Investigate inside an authorized draft-only editor only, not on production today.

**Current choice:** NONE APPROVED. Even the four purely editorial articles remain HOLD_UNSENT. The two commercial ones remain HOLD_MERCHANT.

## Signup-expectation difference (specific current live copy)
**Published /dispatch/ (#523):** "New investigations and archive finds by email, when we publish them." Its near-form copy tells readers the Focus gift and unsubscribe, but **does not explicitly mention occasional commission-earning recommendations**.
**Published /focus/ (#1579):** Near the Jetpack signup block, the existing disclosure says some emails may contain recommendations that earn commission.
**Published Editorial Standards (#17):** commercial relationships do not determine historical conclusions; relationships disclosed where they exist.

**Proposed founder-review-only improvement for /dispatch/ near the form:**
> The Dispatch brings you original investigations, archive discoveries, and occasional practical guides. Some issues may recommend relevant products, and Final Vestige may earn a commission if you choose to buy through a clearly disclosed link. There is no purchase requirement. Unsubscribe anytime.

This proposal keeps the historical value proposition first, puts the commission possibility where new subscribers make a choice, and avoids claiming retroactive consent. It should not be inserted live without specific production write approval and a visual QA of mobile form and screen readers.

## Merchant and legal fail-closed matrix
| Evidence needed | Current truth | Release effect |
| --- | --- | --- |
| Final Vestige named affiliate approval for Zen12 | Not verified | 03 HOLD_MERCHANT |
| Specific EMAIL promotion permission for Zen12 | Not verified | 03 HOLD_MERCHANT |
| Hypnosis Live Total Focus account/EMAIL rights | Not verified | 05 HOLD_MERCHANT |
| Authenticated earning links and approved buyer-guide page URLs | Not verified; guides are drafts | Both hold |
| Seller-specific price, refund fulfillment, checkout, and audio outcomes | Variable or not verified | Do not promise |
| Valid Final Vestige business physical postal address | Not verified | ALL HOLD |
| Actual Jetpack footer plus *functional* opt-out test | Not verified; no authorized real test | ALL HOLD |
| Confirmed consent/eligible email audience (private count only) | Not verified | ALL HOLD |
| Genuine received email/welcome and excerpt visibility | Not verified | ALL HOLD |
| Exact final founder approval of creative, recipient, date, SEND | Not granted | ALL HOLD |

CAN-SPAM primary purpose is contextual. An "editorial" label is not an automatic commercial-email exemption. The FTC recognizes promotions of commercial products and commercial-purpose sites: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Operational safe sequence
Preserve current site and list; do not switch newsletter settings. When the founder *separately* authorizes a draft-only native preview, verify post type, title/subject, optional actual custom excerpt, link behavior, sender footer, disclosure location on mobile, and toggle rollback OFF. Founder must separately authorize any real test email and test-recipient unsubscribe, then authorize final editorial/recipient/date/send. An offline preview or a 1,000-test suite cannot substitute for any of these.

## This run's source-grounded findings
Gmail read-only targeted search returned marketing/product emails but no affirmative publisher-specific EMAIL-channel grant in reviewed results. It did locate a 2026-10-25 subscriber **confirmation request**, which is not the 52-page **welcome receipt**. Search absence is NOT proof a grant or welcome does not exist elsewhere. No private address, link token, or list export is shared.

No WordPress content/settings/write, subscriber action, partner inquiry, outbound email, tracking, or paid platform occurred.
