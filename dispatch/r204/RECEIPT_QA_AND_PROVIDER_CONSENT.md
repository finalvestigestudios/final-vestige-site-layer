# R204 — first real receipt and subscriber authorization protocol (READ-ONLY; HOLD)
Current evidence: authenticated Jetpack status/settings 2026-11-08T07:38:29–30Z. Master campaign PR #175 at d57ccdba3aee8f065e143e101c2945f4f3d01647; prior review PR #201 ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6; parent R203 PR #1544 ea3d27c49cd61f368f030b44aa0e3e77a6fe085d. Issue #174 is the canonical approval record. **No send authorization exists.**

## Source of truth: subscriber transition, not browser success
The live /focus/ #1579 `subscribe` query and client `is-subscriber` state can reveal a PDF panel before an authoritative provider transition. The PDF display is not `confirmed_signup`. Do not log a conversion there.

**Important WordPress-native exception:** WordPress.com documents TWO legitimate paths: an email-only subscriber is sent a confirmation email and must confirm before receiving welcome; an already authenticated WordPress.com account can skip that email-confirmation step and receive welcome immediately. It would be wrong to require a confirmation-link click for every subscriber. Both paths still require the authoritative provider "Email subscription = Subscribed" or equivalent verified eligibility, and separate documented consent to The Dispatch. A Reader/follower count by itself is not that evidence. See https://wordpress.com/support/newsletter-settings/ .

Read-only provider reconciliation — permitted:
1. Obtain time-stamped Jetpack subscriber admin filtered **Email subscription: Subscribed**, plus pending/suppressed/unsubscribed counts, without copying subscriber addresses into GitHub, analytics, logs, or public artifacts.
2. Normalize the same underlying account by a local-only provider identifier; do not sum `total=3`+`confirmed=3`+`unconfirmed=2` as 8 people. The status API totals are different categories and cannot be arithmetically combined.
3. Attribute only a **new provider-confirmed transition**. Event `confirmed_signup` is emitted once per provider-local subscription transition ID, deduped privately; aggregate only `day, channel, campaign, asset_id, confirmed_count`, never email, IP or subject. A confirmed follower who did not newly subscribe is not a new lead.
4. Do not imply opt-in to unapproved affiliate solicitation merely because a PDF was downloaded; check the form's contextual promise and channel consent.

## First received-email audit (NO sending)
A genuine delivered Jetpack email is still missing. An October 25 connected Gmail **Confirm your subscription** request is not the final welcome. A configured welcome message is not proof of its receipt.

WordPress documents **View > Email preview** on an existing published post, but its static visual preview is not a delivered inbox message. For drafts, the preview controls may require an email-send toggle; do not toggle, create, publish, email a test, or change settings without explicit separate approval: https://wordpress.com/support/newsletter-email-design/ and https://wordpress.com/support/newsletter/email-appearance/ .

If a previously received, properly authorized raw `.eml` becomes available, inspect it **locally** with:
`python -I dispatch/r204/receipt_review.py path/to/local-previously-received.eml`
It parses MIME parts and returns ONLY booleans. Do not commit/upload a real `.eml` or subscriber data. Synthetic unit tests are in `test_receipt_review.py`. No network access, no message delivery, no mutation.

Manual reviewer must independently compare received HTML AND plaintext: actual sender/header, subject/preheader, visible commercial classification, exact FV **valid business postal address**, near-offer FTC disclosure in qualifying commercial copy, accessible link label, functioning opt-out from the email (tested only with explicit authorization), and whether the 52-page welcome link was actually received and opens. Header `List-Unsubscribe` alone is NOT functional proof; postal address printed by Automattic or Hypnosis Live is NOT FV's address. Every issue stays **HOLD_UNSENT** until reviewed by founder; #03/#05 additionally **HOLD_MERCHANT**.

Relevant FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .