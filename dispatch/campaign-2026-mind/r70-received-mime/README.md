# R70 — Received-email evidence instrument (DRAFT; UNSENT)

**Final Vestige Studios / The Dispatch · November 2, 2026 · Issue #174**

This is an **additive**, local-only engineering instrument for a future, separately founder-authorized, genuinely received Jetpack newsletter email. It is not another email-letter candidate, another sender, a subscriber importer, an affiliate-link manager, a WordPress change, or an automatic release gate. The original six campaign issues remain in [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); [draft PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) already supplies the separate per-issue gate; this sprint stacks exclusively on [R69 #639](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/639). Nothing touches homepage [frozen PR #49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) or Mind & Affiliate [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171).

## Why this is a materially different deliverable

The older reviewer pages, custom excerpts, and 1,403 passing hosted tests cannot reveal what a real recipient sees. Jetpack is currently in **excerpt mode**; the GitHub manifest's custom preheader has no demonstrated WordPress post-to-email mapping; the commercial disclosure may land *after* the sent excerpt; legal footer and opt-out have not been demonstrated in received MIME. We therefore needed a **machine-usable received-message inspection surface** rather than another hypothetical HTML template.

**New:** r70-received-mime/inspect_received_eml.py accepts a private local .eml that the founder has independently authorized and captured. It parses real MIME structures via Python's standard library and emits only a redacted, structured report. It checks subject presence and an optionally specified exact subject, sender-domain heuristic, actual plaintext/HTML part presence, visible first-55-word commercial disclosure, opt-out labels/HTTPS syntax and List-Unsubscribe headers, a privately supplied publisher address text match, unexpected interactive HTML, remote image references, pending hard-stop text, and merchant-domain links. **It does not open URLs, send mail, click unsubscribe, communicate with WordPress or read a mailbox.**

Its output contains **no message addresses, recipient names, subject text, raw MIME, body text, URLs, private opt-out tokens, file paths, or message hashes**. An address-match boolean is not evidence that the address legally belongs to Final Vestige. A List-Unsubscribe header is not proof the link works. SPF/DKIM/DMARC, actual delivery provenance, native Jetpack preview, footer accessibility, legal sufficiency and WordPress recipient status still require independent approved evidence. A forged local .eml is indistinguishable to this parser from a real sample. **Every output is HOLD_UNSENT and send_allowed=false, by design.**

### Locally repeatable command, only AFTER founder permission for the receipt

Use a secure, local copy of a genuinely received .eml (do not commit or upload it). Optionally prepare separate private text files containing the founder-selected final subject and the exact legally qualified publisher-owned postal address (the program will **never echo their contents**):

    python -I dispatch/campaign-2026-mind/r70-received-mime/inspect_received_eml.py \
      --eml /private/path/authorized_received.eml --edition 03 \
      --subject-file /private/path/approved_subject.txt \
      --publisher-postal-file /private/path/qualified_address.txt

To inspect a local sample without approved subject/address references, omit both optional flags. The output **cannot be interpreted as a pass**: unprovided evidence stays null and blocked. Input files should remain access-controlled locally, not posted to the Issue, PR, third-party CI or public pages. Deleting the local sample is the founder's retention decision; this tool does not delete it.

To run the deliberately synthetic/adversarial suite:

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r70_received_eml.py -v

Tests create in-memory example.invalid addresses, a deliberately fictional address and nonfunctional opt-out tokens. They exercise mail with/without MIME alternatives, email-only HTML, commercial disclosure before/after 55 words, opt-out headers versus visual anchor, bad schemes/userinfo, dangerous markup, merchant-source URLs, wrong/missing subject, private address matching, invalid editions, oversized files, empty content, and privacy redaction. **Passing these synthetic tests never establishes actual mail compliance.**

## Generate actual previewable HTML + plaintext without a real email

A second standard-library utility provides a complete end-to-end **SYNTHETIC** pipeline. It creates an in-memory example.invalid MIME message, applies the inspector, then writes a safe HTML review board, plaintext review and redacted JSON. **No .eml is persisted, and no email is sent.** It demonstrates the rendering and privacy contract for reviewers while making no assertion about real WordPress delivery:

    python -I dispatch/campaign-2026-mind/r70-received-mime/make_synthetic_preview.py --out-dir /private/path/fv-dispatch-preview

Open the generated synthetic-review.html locally at mobile and desktop widths; compare synthetic-review.txt and synthetic-redacted-report.json. Everything visibly says HOLD_UNSENT, including cases where synthetic header/footer syntax is detected. The next step after an independently approved real test is to run inspect_received_eml.py privately and pass only its **redacted JSON** to render_report.py using --report-json, --html-out and --text-out. **Never commit real .eml or subscriber details.**

The additive native tests now include 44 inspector/renderer adversarial tests **plus eight synthetic end-to-end pipeline checks** (52 new tests). Their passing result is software behavior evidence, never receipt, authorization, legal compliance or a campaign send clearance.

## Independently observed upstream state

Authenticated read-only WordPress.com/JETPACK at **2026-11-02 16:46:10–16:46:13 UTC**, blog 256784396:

- subscriptions=true, site_can_send=true; email_new_posts_by_default=false.
- email_content_format=excerpt; sender display name Final Vestige; reply_to=no-reply.
- welcome_message includes the existing 52-page Focus Fieldbook PDF, but delivery and receipt are **unverified**.
- subscriber counters total=2, confirmed=2, unconfirmed=2, suppressed=0; **nonadditive**, not evidence of four people, and not a unique eligible-to-email cohort.
- recent_sends=[] in the returned window. Do not describe this as proof of zero lifetime mail.

Read-only content: /dispatch/ page #523 and /focus/ page #1579 are published; Editorial Standards page #17 requires primary-source rigor, explicit uncertainty and disclosures. Dispatch invites new historical investigations and archival finds; a shift to commerce without a clear opt-in expectation would be a trust mismatch. Focus remains the single 52-page welcome resource. No change to these pages was made.

The linked account's Gmail search returned **FORBIDDEN** for targeted publisher-specific Inspire3 authorization and welcome searches this run. We cannot assert that authorizing mail is absent, approved, or rejected. The prior October 25 "Confirm your subscription" message was a confirmation **not** a verified welcome or campaign mail. No private mailbox contents were accessed in this sprint.

## Named product boundaries, checked on official pages November 2

**Zen12:** https://zen12.com/hnp claims 12 minutes provide an hour's meditation benefit and automatic brainwave effects; describes a 12-level, four-style library and seller-promised one-year refund. The numerical equivalence/efficacy, legal applicability and checkout refund eligibility are **not** independently proven. No price, payout, product-specific endorsement or link activation is approved.

**Total Focus:** https://hypnosislive.com/mental-skills/total-focus advertises a 33-minute, 47-MB audio session; its current page showed $24.44 standalone and $19.95 component pricing in a bundle, and a **seller-asserted** 14-day refund. No stable final checkout price, product-specific efficacy, refund execution, or promotion permission is independently established. No price or guarantee should enter the email.

**Public affiliate portal:** https://affiliates.inspire3.com/ says affiliate members receive individual links, but viewing its recruitment page is not a grant to Final Vestige of named-product eligibility, EMAIL-channel marketing, creative licenses, earning URL, presell routing or payout. Mind's newest Zen12 work, [draft PR #642](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/642), remains **unpublished** and not an approved destination. A seller's public sales page is not a substitute for publisher authorization.

## The evidence sequence (do not shortcut)

**A. Offline sources:** Six source-controlled letters and four-editorial/two-reserved-commercial division are intact, but six current bodies differ from #175's original exact SHA; founder must select final versions. The Apollo 1 "fourteen/seventeen seconds" numerical subject conflict remains an editorial decision. No edited source becomes approved just because CI passes.

**B. Publisher setup:** Establish an owned qualifying physical mailing address, an approved send/no-send per-edition decision, target audience and one delivery model (site-first custom excerpts or full email). Check WordPress's Subscribers dashboard filter "Email Subscription: Subscribed" and exclusions for bounced, paused and Reader-only states, without publishing personal addresses.

**C. Native render:** Only with separate founder permission create a **draft** WordPress post and use its own Preview email UI. Do not publish, schedule, toggle a campaign-wide setting or send a test without that action's specific permission. The native preview does not prove inbox delivery. The campaign's bespoke HTML artifacts are not guaranteed to be transmitted by Jetpack. Official: https://wordpress.com/support/newsletter/email-appearance/ .

**D. Received MIME:** Only after another **explicitly approved single-recipient test send**, privately capture the resulting .eml, run this offline inspector, then review the actual render, link destinations, reply/sender identity, subject, post excerpt, first 55 visible words and legal footer. If the founder provides an address file, match the text but separately verify ownership and legal qualification. Do not put an opt-out token in GitHub or click live recipients' unsubscribe links.

**E. Manual functional/legal verification:** In an authorized safe test context, validate that opting out really works and remains available for 30 days, while requests are honored within 10 business days. CAN-SPAM also requires truthful sender/subject, commercially appropriate labeling and a valid publisher postal address. Functional opt-out acceptance cannot be inferred from a clickable-looking link or header. See https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . FTC endorsement guidance: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .

**F. Named merchant proofs:** For editions 03/05 demand written Final Vestige-specific EMAIL authorization, approved creatives and URLs, a published/approved guide, validated sales representations and clear commission disclosure within the actual mailed excerpt and beside the guide invitation. Do not insert a live affiliate URL into a disabled placeholder.

**G. Final founder approval:** Approve selected six source file SHAs, post-title subjects, delivery settings, audience, postal/footer, CTA destinations, send dates and exactly which of the two commercial placements are eligible. A preview or test authorization **does not** grant permission to send the campaign.

## Current disposition

**01/02/04/06: HOLD_UNSENT. 03/05: HOLD_UNSENT + HOLD_MERCHANT.** No publisher email sent or test-sent; no subscriber, WordPress post, site setting, signup list, paid tool, tracking or commercial link changed. This sprint's source code is a technical diagnostic, **not** a compliance certificate and **not** a send trigger. Homepage work remains outside scope and priority one.
