# Dispatch R356 — Received Jetpack mail acceptance (PRIVATE evidence only)

**2026-11-14 PT · Issues #174, #171, #129, #820 · HOLD_UNSENT**

## What can be established today

- Authenticated Jetpack newsletter status (2026-11-14 14:58:58 UTC): enabled and technically sendable, but **automatic new-post emails disabled**, last five sampled posts were **never sent / opted out**. No recipient-level send or actual inbox proof.
- Authenticated newsletter settings (2026-11-14 14:58:59 UTC): full body, sender label `Final Vestige Studios`, reply-to no-reply, welcome text configured to point to the 52-page Fieldbook PDF. Configuration is not delivery.
- Subscriber dashboard returns total **3**, confirmed **3**, unconfirmed **2**, WordPress.com followers **3** and direct-email followers **0** (the latter follower classes were obtained in earlier separately labeled diagnostics). These are different/overlapping measures; **do not add or infer three reachable email recipients**. Only provider-authoritative permissions can establish audience.
- The owned Gmail inbox has a **2026-10-25 "Confirm your subscription"** notice attributable to the WordPress signup flow. It requests confirmation. It is **not** a received Fieldbook welcome, final opt-in confirmation, newsletter message, or partner-permission letter. No subscriber address, token, or raw MIME is recorded in GitHub.
- /dispatch/ WordPress editor contains a native Jetpack Subscribe block, and public /dispatch/ renders an email input and button. That establishes a *form surface*, **not** a successful submission or provider-confirmed signup. /focus/ has an existing Jetpack signup and publicly accessible PDF link; downloading alone is not marketing consent.
- PR #2477 provides six HTML/plaintext **offline simulations**, not actual Jetpack-rendered received emails. In particular an original Markdown preheader displayed in an HTML simulation does not prove WordPress can set a separate preheader.

## The minimum safe receipt sequence

**Phase A, read-only (allowed):** Compare native settings; inspect the actual public guest page, WordPress post notification status, default-off send behavior, provider aggregate follower fields, and existing owner-controlled inbox for already received mail. Do not submit a new signup or click unsubscribe.

**Phase B, founder-authorized non-sending preview (not yet evidenced):** In the WordPress post editor, inspect the Newsletter panel and use **Preview email** only on an explicitly approved isolated draft without publishing or changing the send toggle. Capture screenshots at desktop/tablet/mobile; inspect the real preview subject, source link rendering, product disclaimer, visual hierarchy, and actual native footer. Preview does not prove delivery or clickability. WordPress docs: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter/send-newsletter-emails/.

**Phase C, requires the founder's explicit separate authorization:** For an owner-owned mailbox ONLY, approve a single isolated test email, not a campaign or subscriber send. Export the received RFC822 .eml securely to a local reviewer environment; do not commit/upload its content to public GitHub/Drive. Run `python received_email_audit.py private.eml --subject 'The mind is not a camera' --publisher-address 'VERIFIED_FV_ADDRESS'` **only after a real qualifying FV mailing address has been identified**. The script returns booleans/gaps, not mailbox data or URL tokens. Verify the received message's actual sender, title, visible legal address, content links and accessible HTML/plaintext. Independently inspect the opt-out mechanism only under an approved isolated test plan; existence of an unsubscribe URL never proves functionality. Preserve evidence references privately, not actual subscriber identities.

## Hard separation

A confirmation email proves **one confirmation request was delivered to the owner-accessible inbox**; it does not establish that the recipient confirmed, that the welcome was delivered, or that marketing consent was granted to every account. A WordPress dashboard field `site_can_send=true` does not authorize publishing or subscriber contact. A simulated EML, even with a valid-looking List-Unsubscribe header, does not prove that the opt-out URL works. An existing provider address or merchant address is **not** a substitute for the qualifying Final Vestige publisher address.

Required compliance is based on the primary purpose of the email; review the FTC CAN-SPAM guidance for mixed editorial/commercial messages: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . For the two commercial issues, preserve the adjacent affiliate commission disclosure per https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .

**Decision:** Every issue remains HOLD_UNSENT; issues 03 and 05 additionally HOLD_MERCHANT. No sending, test email, subscriber contact, list import, WordPress write, merchant outbound activation or founder release approval was performed.
