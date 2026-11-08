# Dispatch R69 — channel reality and publisher approval kit (DRAFT / UNSENT)

**Source of truth:** original six-letter master [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) exact `d57ccdba3aee8f065e143e101c2945f4f3d01647`; independent per-issue release gates [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); latest stacked version-drift record [PR #633](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/633) exact `4068e3feaa50aee8174d0f169e9bd05aa3a2c42f`. Campaign Issue #174; merchant-owner Issue #171. This packet is **a new operational synthesis, not a replacement newsletter, not another implementation of the preflight checker, and not a WordPress template**.

## First-mile verification and what is actually new

On Nov 2 at **15:41 UTC**, authenticated `newsletter.get_settings` and `newsletter.status` returned: subscriptions ON, site_can_send true, auto-notify new posts OFF, email content **excerpt**, from-name Final Vestige, reply-to no-reply, welcome message contains 52-page Focus Fieldbook URL, counts total 2 / confirmed 2 / unconfirmed 2 / suppressed 0, and `recent_sends=[]`. A configured welcome is NOT proof it arrived; empty recent_sends is NOT lifetime proof. Two confirmed subscriptions are NOT a deduped eligible-email cohort. In the original 2026-10-30 PR #175, the exact six source documents and manifest were re-fetched, and all six independent Python-suite *predicates* were reproduced against those bytes in V8 (6/6 PASS); **this is not native Python execution**. The last independently reported native-hosted full-suite result on the current stacked head before R69 is [R68 Actions #41465803559](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41465803559), **1,389 tests PASS at head 4068e3fe**. These are repository checks, **not email-delivery proof**.

NEW finding from the official [WordPress subscriber guide](https://wordpress.com/support/subscribers/): the relevant denominator must be filtered by **Email subscription status**, specifically *Subscribed* AND not bounced, paused, or not sending. Unconfirmed entries are excluded from total; Reader-only follows may still appear in the subscriber interface. We have **not** inspected any identifiable subscriber row or exported addresses. The current aggregate does not resolve the unique opt-in count.

NEW documented native preview nuance from [WordPress email appearance](https://wordpress.com/support/newsletter/email-appearance/): with *excerpt* enabled, post-specific custom excerpts can determine email body; without them, WordPress generally uses the opening **55 words**. The proposed custom `preheader` in our manifest is **not** a proven Jetpack-delivery field. WordPress post title is expected to supply the subject; real inbox snippet requires inspection of received message. Preview/test controls appear if the post editor's send-to-subscribers toggle is ON; this procedure requires separate founder authorization and careful avoidance of publishing.

## Hard decision: what The Dispatch actually delivers

Original editorial expectation: a substantial once-weekly historically grounded letter. Current technical setting: only a teaser of a post by default. These are different experiences. Before choosing final text, founder must select **one** of:

- **Excerpt route (recommend as low-risk prototype, NOT APPROVED):** keep site setting unchanged, prepare an *approved specific WordPress post* (not published) plus a carefully written custom excerpt as the email; ensure excerpt itself contains one clear link to the corresponding *published* long-form web article, and for #03/#05 disclosure in excerpt. This is editorial **site-first** delivery, not a six-full-letter inbox series. No default auto-send.
- **Full-text route (requires explicit separate settings approval):** switch Jetpack from excerpt to full only after approval and staging; then verify actual received HTML/plain footer and 6 issue-specific disclosures. Still sends through WordPress posts—not arbitrary HTML upload.
- **Custom post layout/More-block approach:** does not by itself establish a standalone curated six-email campaign. Do not infer compatibility without native preview and received MIME.

The source-controlled .html assets elsewhere are *offline review references*, not approved HTML that WordPress will email byte-for-byte. Any conversion claim on the current list would be noise: N=2 *count* is not denominator, let alone statistical lift.

## What this sprint produced

`release_choices.json`: fail-closed exact original-vs-stacked source selection and per-issue CTA/seller responsibilities (all approvals false).
`release_brief.md`: six detailed editorial/conversion judgments, one source-led call to action each, honest subject/preview reservations and one reader-facing promise.
`subscriber-privacy.md`: WordPress-specific no-PII recipient-reconciliation and welcome-flow protocol.
`merchant-authorization.md`: exact product page claim separation, email-rights evidence hierarchy and purchasing limits.
`received-mail-check.md`: authorization-dependent real-preview and CAN-SPAM footer acceptance criteria.
`review.html`: static accessible offline decision board, no scripts, forms, real subscriber fields, merchant links, or live sends.
`tests/test_r69_channel_reality.py`: native Python static/adversarial guard suite.

## Gate precedence and boundaries

1. Original copy SHA never means final founder approval; six canonical bodies changed on stacked branch. Apollo #04's original “Fourteen seconds” and stacked “Seventeen seconds” cannot be silently treated as a verified event duration. Prefer a nonnumeric exact-subject candidate if founder accepts it.
2. All six remain **HOLD_UNSENT** until exact final copy SHA, channel format, unique recipient consent, actual received mail, sender identity, publisher-owned physical address, functioning unsubscribe, verified accessible CTA and explicit founder approval are evidenced.
3. #03 and #05 additionally **HOLD_MERCHANT** pending separately authenticated **named-product, publisher-specific, EMAIL-channel rights**, approved guide and permitted earning URL. Public affiliate recruitment, personal receipt of an Inspire3 promotion or a general terms page cannot grant those rights.
4. Homepage flagship, frozen PR #49, WordPress production pages/settings, existing Jetpack list and welcome are untouched. No new platform, purchase, tracking, outreach or mail.

Official operational references: [WordPress email settings](https://wordpress.com/support/newsletter-settings/), [subscribers](https://wordpress.com/support/subscribers/), [email appearance](https://wordpress.com/support/newsletter/email-appearance/), [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC endorsement guidance](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).