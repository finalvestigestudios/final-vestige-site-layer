# R87 — exact-consent alignment proposal (DRAFT, not applied)

**Observed 2026-11-03 09:36 UTC** via authenticated WordPress. Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), merchant owner [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Source PR [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); first release gates [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); R86 [#755](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/755). **NO LIVE CMS/SETTINGS/MAIL MODIFICATIONS.**

## New concrete defect

The two public signup pages use **the same Jetpack list** but set different reader expectations. `/dispatch/` (WordPress page #523, last modified 2026-10-29) describes investigations, archives, the free 52-page Fieldbook, confirmation and unsubscribe; it **does not** disclose potential affiliate guides before signup. `/focus/` (page #1579, last modified 2026-10-30) explicitly states: "Some emails may include recommendations that earn us a commission." The Jetpack welcome message also frames the mailing solely as investigations and archive finds, without an affiliate expectation. A new reader may subscribe via one page and receive the same future commercial-reserved issues as someone who subscribed via the other.

**Finding:** copy parity needs founder-approved coordination before promotional issues. A legally sufficient commercial-email disclosure is independently required *inside* a commercial email and *beside qualifying offer links*; the signup notice alone never replaces it.

## Surgical proposed copy (not yet authorized)

### A. /dispatch/ — add immediately after the existing form and before its "Unsubscribe anytime" sentence
> **What you’ll receive:** The Dispatch sends occasional original investigations, archive finds, and evidence-led Mind & Perception reports. Some editions may include an optional product guide; if you purchase through a qualifying link in one of those guides, Final Vestige may earn a commission. The 52-page Focus Fieldbook is free, and no purchase is required to subscribe. You can unsubscribe anytime.

Keep the current headline, published copy, single Jetpack block and Fieldbook CTA intact. Use visible paragraph text, not a tooltip or tiny legal overlay. Confirm sufficient color contrast against the site's dark background and keyboard access to privacy disclosure. **Do not add any new form or list.**

### B. /focus/ — no essential change needed; optional consistency edit in its existing .fvf-consent paragraph
> Get the free 52-page Seven Day Focus Fieldbook and join The Dispatch, our occasional email with new investigations, archive finds, and evidence-led Mind & Perception reports. Some editions may include optional product guides; if you purchase through a qualifying link in a guide, Final Vestige may earn a commission. The Fieldbook requires no purchase. Unsubscribe anytime. Privacy Policy.

This is the SAME commercial expectation and SAME list, not a second marketing preference or an implied vendor opt-in. Preserve the existing free direct-PDF flow and native Jetpack confirmation.

### C. Jetpack welcome message — optional founder-reviewed *future* addition only; original remains configured
> We'll share original investigations, archive finds, and occasional Mind & Perception research. Some future editions may include an optional product guide. Where a qualifying affiliate link appears, we’ll disclose that Final Vestige may earn a commission. The Fieldbook is free and buying anything is never required.

Do not replace the 52-page PDF URL or rest of the welcome instructions. This proposal is **NOT evidence** a recipient received the welcome message. Never change newsletter settings on this branch.

## Release procedure — still a hard HOLD

1. Obtain founder authorization for the **specific** signup/welcome copy separately from campaign send approval.
2. If separately authorized, re-fetch *live* pages #523/#1579 and welcome settings; compare against this dated observation. Abort any surgical patch if source text or structure differs—no blind overwrite.
3. Change only the approved text; preserve the Jetpack subscribe block and PDF delivery. Review each page at 320/360/390/768/1440px, with zoom, keyboard, and reduced motion; then re-fetch production to verify.
4. Reconcile reader eligibility privately in the native Subscribers filter. Aggregate diagnostics `2 total / 2 confirmed / 2 unconfirmed` do NOT mean four recipients; another follower surface shows `0 email / 2 WordPress.com`. No exported addresses.
5. Verify a qualifying **Final Vestige** postal address and effective unsubscribe in an explicitly authorized genuine received test email. Automattic's postal address in its own confirmation is not publisher proof.
6. Obtain Final Vestige-specific Zen12 and Total Focus affiliate acceptance, EMAIL-channel promotion permission, correct private link syntax, exact current seller claims/offer terms, and Mind-owned published buyer guides. Public affiliate recruitment or seller promotions are not authorization.
7. Founder must separately approve exact six editions, audience, timing and sending. Until then: **ALL SIX HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT.**

## WordPress product reality

Jetpack is `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`. The setting is **not** a sitewide mechanical send lock; a post can be individually switched to email. Five recent posts have `never_sent_opted_out`, not an all-time zero-send certificate. Proposed preheaders in manuscripts are not proof that WordPress will use them as inbox preheader text. WordPress calls for a **native Preview email** inspection; a genuine received message demands a separately approved test send. Neither has occurred here.

**Evidence:** [WordPress send workflow](https://wordpress.com/support/newsletter/send-newsletter-emails/), [WordPress email appearance/preview](https://wordpress.com/support/newsletter/email-appearance/), [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC endorsement FAQs](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).
