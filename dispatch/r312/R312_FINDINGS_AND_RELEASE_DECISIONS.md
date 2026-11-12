# Dispatch R312 — actual inbox contract, not another newsletter rewrite

**Date:** 2026-11-12 11:37 PT · **Status:** REVIEW ONLY · UNSENT · UNPUBLISHED · NO MERCHANT LINKS.  
**Source of truth:** Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); master draft [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), immutable head `d57ccdba3aee8f065e143e101c2945f4f3d01647`.  
**This is a new, additive evidence/release contract, not a replacement for R201/R309/R310/R311.** The homepage and frozen PR #49 are outside scope.

## Decision-changing finding: proposed preheaders are not verified inbox preheaders

The master `manifest.json` has six **proposed preheader** strings. Jetpack's current documented settings support full/excerpt content, email byline, sender display and previews. They **do not establish** that a custom, hidden *inbox preview text* can be set from the campaign manifest or a WordPress post excerpt when this site is in **full text** mode. Do not label these strings as confirmed Gmail/Outlook preview text. Do not switch the live site to excerpt mode to make an assumption work.

WordPress says the subject is the post title and the sender address is `donotreply@wordpress.com`, although this site's display name is Final Vestige Studios. With reply-to set to no-reply, do not imply reply-by-email support. The actual Gmail/Outlook snippet, MIME text/HTML, header and footer are **UNVERIFIED**. `Preview email` is documented and may be usable with post sending OFF, but that is a *visual preview*, not a received message or a successful unsubscribe test.

The R310 Gutenberg review fixtures begin with an explicit `REVIEW ONLY` paragraph inside the post content. That is deliberate safety labeling, but if an editor ever imports it as a real post and sends it, the warning could become the email's first visible line and distort the inbox snippet and conversion-oriented opening. **Never promote R310 fixtures directly as publish-ready content**; a separate reviewed release artifact and founder approval are required.

Primary platform sources:
- [Send newsletter emails](https://wordpress.com/support/newsletter/send-newsletter-emails/)
- [Email appearance, Nov 9 2026](https://wordpress.com/support/newsletter/email-appearance/)
- [Jetpack Customize newsletter](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/)

## Authenticated live checks (read-only; 19:37 UTC)

`subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, sender display Final Vestige Studios, reply-to no-reply, segmentation OFF; diagnostic total=3, confirmed=3, unconfirmed=2, suppressed=0. These are overlapping provider classifications, **not five individuals**; the actual eligible email recipient population is unknown. Recent five notifications are `never_sent_opted_out`; **not** proof of lifetime zero sends. Welcome includes the 52-page Focus Fieldbook URL, but actual receipt is unverified. An October 25 connected Gmail confirmation is not a welcome. Gmail searches did **not find** Final Vestige-specific Inspire3 EMAIL authorization; absence is not proof no agreement exists.

The live /dispatch/ page (WP ID 523), /focus/ page (WP ID 1579) and Editorial Standards (WP ID 17) were read; no writes. Editorial Standards requires sourced claims and separates historic record, interpretation and commercial relationships.

## Red-team editorial decision queue: conversion cost before cosmetic polish

| Issue | Purpose | Landing / value risk | Founder decision required |
|---|---|---|---|
| 01 | historical-perception bridge | Duplicate destination with 02. An optional Change Blindness alternative exists (R301) | Approve distinct source-matched route or retain knowingly |
| 02 | Puységur historical documentation | Repeats exactly the 01 archive URL | Approve distinct archive destination or rewrite sequencing |
| 03 | practical meditation + Zen12 guide | Guide is not live/approved; partner email rights and earning link unverified | Keep `HOLD_MERCHANT`; direct through vetted first-party buyer guide only after approval |
| 04 | Apollo 1 evidence | The “fourteen seconds” subject lacks defensible documentary referent | Correct subject with an approved R302 alternative before any send |
| 05 | hypnosis-audio evaluation + guide | Product/current checkout/guide/email rights unverified | Keep `HOLD_MERCHANT`; no active earning or merchant link |
| 06 | attention-log reflection | Existing subscribers may be sent back to an opt-in page | Founder to choose direct guide/fieldbook access; never count page visit as new lead |

**No original copy is adopted or changed by this sprint.** All six remain held; owner review resolves options, not automatic substitution.

## How to establish preview evidence without breaking the no-send instruction

1. Obtain separate founder approval **before any WordPress draft creation**, if that is needed. An offline HTML render is not a native Jetpack preview. No `Send test email` action without specific approval.
2. Use the post editor's **Preview email** with per-post “Send this post to subscribers” OFF. Capture screenshot of *desktop/mobile*, the toggle state, title/subject, actual opening paragraph and whether the commercial disclosure appears beside the CTA. Preview alone does **not** prove mailbox snippet, unsubscribe or postal address.
3. To prove the actual received message, obtain **specific founder authorization** for a safe, clearly identified test delivery to an owned address. Record actual sender/from, subject, opening snippet, footer, unsubscribe link behavior, accessible HTML/text, and whether it was truly delivered. Never include recipient email/PII in Issues.
4. For commercial issue 03/05, obtain the actual merchant account agreement, explicit **EMAIL** promotion rights, issued link and guide eligibility separately. No email campaign may send without a concrete, per-issue founder final approval.
5. The 3/3/2 subscriber status needs a private subscriber-status and notification-frequency review, not a list export or an assumption that 3 are reachable.

**Legal purpose guard:** The FTC categorizes by the *primary purpose* seen by the recipient, including subject and placement of promotions. An editorial title is not an exemption from commercial-email obligations. Verify publisher's lawful postal address, functional opt-out, sender accuracy, placement of disclosure and receipt. Never insert Automattic's mailing address in place of Final Vestige's.

Sources: [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).

## Commercial claim boundaries

Exact [Zen12 seller page](https://zen12.com/) advertises 12 levels / 48 MP3s, with seller effectiveness and refund representations that cannot be treated as independent scientific evidence or locked current checkout terms. Mind Studio's [#2237](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2237) is a **draft** independent guide; it has disabled merchant CTAs. An Inspire3 public recruitment portal is not proof of Final Vestige's acceptance, issued earning URL or permission to market by email. Do not put price/refund claims into newsletter copy until current product-and-variant checkout is verified.

## OFFER → FUNNEL STEP → BLOCKER → ACTION → PASS/FAIL → OWNER

| Offer / step | Blocker | Action | Evidence | Owner |
|---|---|---|---|---|
| Zen12 → guide → independently reported sale | No authenticated EMAIL permission or live guide | Validate merchant acceptance, written email channel, actual tracking URL and independent live guide | HOLD: #171/#2237 | Mind / Commerce |
| Focus → confirmed lead | Page/UI state not provider consent | Provider-origin confirmation transition with durable opaque idempotency; user should still get the public fieldbook | UNKNOWN live; synthetic gate R311 only | Claude / Focus |
| Dispatch → recipient inbox | No native preview or postal/unsubscribe witness | Owner-approved visual preview followed only by separately approved mailbox test | NOT RUN | Dispatch / Founder |
| Grok asset → qualified human visit | Not all real asset IDs/matching landing sessions are verified | Reuse TASK-008 UTM names and existing analytics, no new scripts | UNKNOWN | Grok / Praxxis / Claude |
| Commerce → realized net revenue | Settled orders/fees/refunds and qualified-session denominator unobserved | Use independently reported paid outcomes, source-linked 7d/30d cohorts; reject clicks as orders | NOT COMPUTABLE | Commerce / Claude |

Use `utm_source=...&utm_medium=organic_social&utm_campaign=<topic>_pilot_2026_11&utm_content=<asset_id>` for Grok social links **only once coordinated/approved**. For email CTAs, propose (not deploy) `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_0n_<slug>`. Do not inject tracking into the existing campaign or count recipient-level links without consent.
