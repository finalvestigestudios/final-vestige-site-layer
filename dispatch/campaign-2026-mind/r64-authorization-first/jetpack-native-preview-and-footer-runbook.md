# Native Jetpack preview versus actual received email — no-send runbook
**Current status: NOT RUN / NO PREVIEW RECEIPT / NO EMAIL SEND AUTHORIZED.**

## Verified WordPress.com user-interface constraint (2 Nov 2026)
Official October 2026 WordPress.com support says: while editing a **post**, open the Newsletter (paper-airplane) panel. 'Preview email' and 'Send test email' controls appear when **Send this post to subscribers** is on. The visual Preview control displays desktop/tablet/mobile views. The **Send test email** control is a separate outbound action. The post-specific toggle can override a site's default-off setting, so never turn it on just to obtain a screenshot without explicit founder authorization and a documented fail-closed rollback. Merely looking at a public post, creating an offline HTML mock or reading newsletter settings is NOT this preview.

Source: https://wordpress.com/support/newsletter/email-appearance/ (reviewed 6 Oct 2026); https://wordpress.com/support/newsletter/send-newsletter-emails/ (reviewed 19 Oct 2026); https://wordpress.com/support/newsletter/disable-newsletter-emails/ .

**Known production configuration:** site-wide auto-send OFF, excerpt email format, from-name Final Vestige, no-reply replies, welcome Fieldbook configured. Under excerpt mode, a missing post-specific excerpt falls back to the first 55 words. A custom excerpt may put a commercial disclosure first, but cannot guarantee a final native email footer or that readers see the long letter. Jetpack's email is not equivalent to the standalone HTML reviewers in GitHub.

## Gate A — ZERO-WRITE REVIEW (permitted now)
- Confirm the actual public subscriber notice on /dispatch/ and /focus/, Editorial Standards, and published CTA destinations using authenticated read-only WP.
- Independently inspect the proposed exact subject, excerpt, HTML and plaintext for honest product distinction and near-link disclosure. Confirm the only CTA is a published founder-approved first-party destination.
- Record send setting OFF. Do not create/edit a draft post, change send toggle, click Preview in the live editor, or send test mail in this stage.
- Compare campaign source against official merchant sales pages, not a generic affiliate directory.

## Gate B — NATIVE VISUAL PREVIEW (requires a **separate, explicit, limited founder authorization**)
The founder must authorize creating a **draft-only WordPress post** for the named issue and temporarily exposing native visual preview controls. State whether and how to use a per-post send toggle without publishing. Before any action, verify site-wide auto-send remains OFF and the editor target is **draft**. Do not click Publish, Schedule, or Send test email. If preview requires enabling the per-post send toggle, record the exception, observe no publication, and restore it OFF before leaving. If that cannot be verified, STOP and report the blocker.

Capture only redacted proof: exact draft post ID, timestamp, site setting, viewport, excerpt/disclosure visibility, link target, whether Jetpack-supplied footer is visible. A screenshot is **visual preview evidence only**, NOT a received email or functional unsubscribe.

## Gate C — GENUINE RECEIVED MIME (requires a second **explicit founder authorization**)
A controlled test-email send to an authorized account is a real outbound send even if not addressed to the existing subscriber list. Founder must approve target test mailbox, exact creative, and one test email separately; this request has **not** been granted. Never use the current subscriber list or send a post live as a substitute for testing. Obtain an original raw message privately. Scrub actual mailbox addresses, tokens, message IDs and unique unsubscribe URLs from any public logs. Use the existing read-only MIME inspector (PR #545 and later hardening PRs) to check headers, distinct HTML/plaintext disclosures, footer and merchant redirects. Preserve original MIME only in private approved storage, not GitHub.

## Gate D — FUNCTIONAL UNSUBSCRIBE (distinct authorized action)
A URL appearing in a received message does not prove an unsubscribe works. Test only with a separate, founder-authorized **test subscription**; never unsubscribe an actual reader. Confirm the opt-out is accessible, simple, applies to marketing emails, functions without login or excessive PII and is honored. Log PASS/FAIL and timestamp without revealing the token. If full functional verification isn't authorized, retain **UNKNOWN**, never PASS.

## What the final report must distinguish
1. OFFLINE_EDITORIAL_PREVIEW: synthetic HTML/plaintext bytes from GitHub.
2. WP_NATIVE_VISUAL_PREVIEW: screenshot of editor's responsive preview without send.
3. REAL_RECEIVED_EMAIL_MIME: authorized real received message, headers/content/footer inspected.
4. VERIFIED_OPT_OUT_FUNCTION: separately authorized functional unsubscribe test.
5. WELCOME_RECEIPT: delivered welcome message after consent; the 2026-10-25 confirmation request alone is **not** this.
6. ELIGIBLE_EMAIL_AUDIENCE: privately confirmed opted-in and unsuppressed email recipients.

None of items 2–6 is established by this repo. No current action changes production.