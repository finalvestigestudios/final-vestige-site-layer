# Dispatch R329 — genuine received-email acceptance protocol (NO SEND AUTHORITY)

**Evidence state 2026-11-13 12:31 UTC: HOLD, not a test invitation.** This is a source-controlled protocol for a founder-authorized future verification only. It does not grant permission to create a WordPress draft, send a test email, alter subscribers, enable automatic sends, add tracking or contact anyone.

## Why another preview renderer is not the solution
PR #2337 already has 12 deterministic original-copy HTML/plaintext previews and 30 offline Chromium viewport checks. Those checks cannot witness (a) actual Jetpack substitution of a per-recipient unsubscribe link, (b) WordPress-generated sender/subject/headers, (c) a legally valid Final Vestige physical mailing address, (d) delivered welcome or PDF, or (e) the actual user's opted-in delivery eligibility. **A screenshot of a preview UI is not a received message.** The post title, not the proposed manifest preheader, is the currently documented subject control; no separately configurable preheader has been verified.

## No-send read-only preparation
1. Record original #175 SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647` and R328 #2337 SHA `6bf50815fcdd6f170bd30e963d6d9140c4cc120b`. Do not modify either. Confirm live WordPress newsletter settings before each later authorized QA.
2. Current confirmed/subscriber counts from the newsletter status API must be treated as **non-additive classifications**. On this snapshot total=3, confirmed=3, unconfirmed=2, paid=0, suppressed=0; no authenticated unique email-eligible recipient count is available. WordPress.com Reader followers are a different denominator.
3. Inspect WordPress editor's documented *Preview → Email* using an already authorized non-sending setup only. Since no CMS draft is authorized here, this workflow remains unexecuted. The native preview and the final received email are DIFFERENT evidence.
4. Only after the founder separately authorizes a dedicated controlled test, record its exact scope, approved personal test mailbox, planned content, and safeguards that exclude the actual audience. Never treat this protocol or a draft PR as authorization.
5. For the authorized received copy, use a **private** original inbox RFC822 MIME source with preserved original headers. Do not commit, paste, publish, post to GitHub, or expose recipient addresses, per-recipient URLs, authentication tokens, message IDs or subscriber exports. Locally execute `node --test dispatch/r329/receipt_guard.test.cjs` against synthetic fixtures first. Running `inspectReceived(mime,{...})` yields only booleans and named missing gates. Never log `mime`.
6. Verify the *rendered* unsubscribe element AND the provider-owned List-Unsubscribe mechanism. An unsubscribe-like string/header is not proof the destination works; only separately authorized, isolated functional checks qualify. Avoid clicking a real subscriber's unsubscribe link without express authorization.
7. Final Vestige must separately substantiate a valid publisher postal address (street, registered PO Box, or qualifying private mailbox). **Automattic's address in the October 25 confirmation email is not Final Vestige's mailing address.** Do not show an unapproved founder home address in files or draft email.
8. Validate WordPress preheader appearance, actual subject, From identity, visible adjacent affiliate disclosure if relevant, semantic message order, plain-text readability, line wrapping, taps/contrast, source links and two actual email clients when a future authorized receipt exists. None are assumed.
9. For the already configured 52-page welcome, prove actual completed delivery and PDF opening only with consented test evidence. A 2026-10-25 Gmail **confirmation request** did arrive; reading it does not establish acceptance or subsequent welcome delivery. Its original MIME did not contain the Fieldbook.
10. Never derive `confirmed_signup`, opt-in, purchase, earned commission or net revenue from an inbox screenshot. Those require authenticated provider events and independently settled commerce records.

## Confidentiality and artifact checklist
Keep only a private evidence locator, observation date, boolean attestations and reviewer role. No names, addresses, mailbox usernames, raw email, token URLs, full HTML or contact data in GitHub. The guard deliberately returns `HOLD_UNSENT` **even when all evidence booleans are set to true**, because only final founder approval can authorize dispatch.

## Current open defects
- Physical address: **no publisher-verified address.**
- Real Jetpack rendered received commercial message: **no authorized receipt.**
- Functional unsubscribe and sender-specific email footer: **unverified.**
- Welcome delivery and active recipient enrollment: **unverified.**
- User-facing preheader behavior: **not established.**
- Zero claims of delivered campaign / paid orders from this QA.

Source references:
- https://wordpress.com/support/newsletter/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://www.ftc.gov/legal-library/browse/rules/can-spam-rule
- https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174
- https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2337
