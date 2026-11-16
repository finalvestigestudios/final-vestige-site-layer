# R405 Native Jetpack non-sending acceptance card — HOLD / REQUIRES WITNESS

Read-only authenticated status at **2026-11-16 18:34 UTC**: newsletters enabled, site_can_send=true, new-post emails OFF, sender name Final Vestige Studios, reply-to no-reply, email content format full, welcome points to 52-page Focus Fieldbook. Newsletter dashboard total3 / confirmed3 / unconfirmed2; follower stats wpcom3 / direct-email0. The displayed classes overlap or represent different concepts and must **never** be summed into a supposed five-recipient list.

## Native preview — what actual evidence is still missing

WordPress.com has a native **Preview email** button under the editor's Jetpack Newsletter panel. Official instructions: https://wordpress.com/support/newsletter/email-appearance/ . Preview email **is not** the same as **Send test email**. The present connector does not expose the editor Preview email DOM, and opening a site screenshot is not equivalent. **No real subscriber, test inbox or merchant was contacted.**

Under an authorized, non-sending editor preview:
- Confirm the prospective newsletter post title becomes subject. Do not presume draft Markdown \`Preheader:\` becomes a mail-client preheader.
- Capture preview of **desktop, tablet, mobile** in the genuine WordPress newsletter preview, including actual subject/sender, top of message, main CTA, near-CTA disclosure, research links, and footer. Redact personal data.
- Check that emails do not leak internal release markers such as \`[[VALID_POSTAL_ADDRESS_REQUIRED]]\` or \`[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]\`. A draft that still contains them must never send.
- For commercial primary-purpose email, require a valid **Final Vestige's own** physical postal address and an unsubscribe mechanism allowing an ordinary recipient to opt out of all marketing messages. The seller's Inspire3 UK address and Automattic mail-routing address do **not** stand in for the publisher address. CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- A preview can show an unsubscribe link but cannot itself prove a real user can opt out and have the suppression honored. A separate, **explicitly authorized**, controlled functional test with real consent proof is required later; there was no such authorization here.
- Record actual preview date, tested post/editor revision, WordPress setting snapshot, device choices, rendered subject and footer, publisher mailing address approval reference and accessibility review. **Do not put subscriber email addresses into GitHub.**
- Explicit founder final approval must name the final six creative versions, actual recipients/consent, permitted send times and responsible operator. No schedule is presently authorized.

## Provider-authoritative signup proof — what is missing

The R398 read-only Focus forensic review found \`?subscribe=\` can reveal a Fieldbook download panel; the \`after_signup\` CTA label is **not a verified provider confirmation**. Do not infer \`confirmed_signup_v1\` from a URL query, client-side form event, PDF download or the WordPress follower counters. Require a private, server-authoritative Jetpack accepted opt-in record with suppression/notification eligibility and deduplication; show only aggregate statuses in Issue #129. Actual welcome receipt and PDF access are unverified; a 2026-10-25 inbox **Confirm your subscription** message is only a confirmation request.

**Current conclusion:** All six issues HOLD_UNSENT, commercial #03/#05 HOLD_MERCHANT, historical #04 HOLD_COPY. No native email preview, test email or actual deliverability verification was performed. The reviewed HTML/plaintext set is an OFFLINE specimen only (R404 PR #2765). **Owner** Founder/Dispatch #174, Focus/Claude #129 for provider data; no WordPress writes permitted.
