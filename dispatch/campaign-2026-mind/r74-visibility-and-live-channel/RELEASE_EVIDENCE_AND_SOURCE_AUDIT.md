# Dispatch R74 — rendered-visible claims, source fidelity and actual-channel acceptance

**2026-11-02, 12:34–13:00 Pacific · reviewer-only · HOLD_UNSENT · NO MAIL ACTIONS**

Master campaign: [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) / [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Stacked parent: [R73 PR #669](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/669) at `83e67c38a0fa7398e07b3265e1ce9268d6326f76`. Parallel buyer-guide owner: [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Homepage PR #49 remains frozen and wholly outside this development.

## The actual defect, not another artificial marketing "win"

R73 correctly required a visible unsubscribe destination and a commercial disclosure/postal address in **both** HTML and plaintext. However, its HTMLParser treated source text inside `<head><title>`, `<template>`, `<span hidden>`, `<div style="display:none">`, and `aria-hidden="true"` elements as visible body text. It could also accept a hidden unsubscribe anchor as visible. A received MIME could therefore appear to have a publisher postal address or disclosure that a reader never sees. **HTML source presence does not equal rendered visibility.**

R74 changes the offline inspector to exclude non-body/inline-hidden material and their associated opt-out anchor labels, while keeping explicit flags indicating hidden nodes and unresolved stylesheet visibility. The existing native WordPress/inbox visual review and independently authorized unsubscribe function check remain **mandatory**: HTMLParser cannot faithfully resolve external CSS, `@media` rules, client-specific rendering, Gmail clipping, post-delivery link rewrites, preheader behavior, or actual click outcomes.

## Exact original PR #175 native Python baseline

The R74 regression test reconstructs eight original files (manifest, six canonical `.md` drafts, original `test_campaign.py`) from **Git SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`** using `git show`, places them in an isolated temporary tree, and executes **the original native six Python unit tests** with `python -I -m unittest discover`. The GitHub workflow now checks out the original PR #175 SHA **in a separate read-only worktree**, and validates that checkout's exact HEAD before running the original six tests. This avoids assuming the original PR SHA is ancestral to the stacked working branch. A missing or mismatched pinned source **fails** the test. This provides independent baseline evidence without rewriting originals or confusing newer expanded drafts with the approved PR head.

The new synthetic-only R74 adversarial cases cover hidden/ARIA/inline-style commercial disclosure, postal-address and unsubscribe evidence; head/template content, MIME behavior, CSS ambiguity and redacted output. Successful execution checks code behavior, **not** WordPress delivery, affiliate authorization, legal eligibility or sender legitimacy.

## Fresh source-of-truth audit — 2026-11-02

**Authenticated WordPress blog `256784396`:** `subscriptions=true`; `email_new_posts_by_default=false`; `email_content_format=excerpt`; `reply_to=no-reply`; sender name `Final Vestige`; `recent_sends=[]`; `site_can_send=true`. Existing welcome message includes a URL to the 52-page Focus Fieldbook. `/dispatch/` (page 523) and `/focus/` (page 1579) remain published; official Editorial Standards page 17 requires source proximity, uncertainty, quote/number checking and clearly separated commercial incentives. NO pages or site configuration were changed.

**Subscriber snapshot `2026-11-02T20:36 UTC`:** total **2** / confirmed **2** / unconfirmed **2** / suppressed **0**. Counters **must not be added together**. Do not infer four people, two deliverable email subscribers, any opening rate or a conversion rate. Use private native WordPress subscription/email-status views (not exports) to establish email-eligible counts only when authorized, and record **counts only** in issue evidence.

**Delivery contract:** WordPress documents that excerpt mode sends a custom excerpt when supplied, otherwise usually the first **55 words**; a proposed preheader is not guaranteed independent Jetpack metadata. Native `Preview email` is separate from a `Send test email` and the latter is an actual message. This run did NEITHER. [Appearance and editor preview instructions](https://wordpress.com/support/newsletter/email-appearance/) and [Newsletter settings](https://wordpress.com/support/newsletter-settings/) reviewed 2026-11-02.

**Seller Zen12 — `https://zen12.com/` inspected 2026-11-02:** seller describes **12-minute** sessions, **12 levels**, **four soundtrack approaches**, premium **48 MP3** collection, and separate **24 MP3** six-level packages. The seller asserts **12 minutes equal an hour of meditation**, automatic brainwave entrainment and broad stress/health outcomes: **unsubstantiated for this named product in our editorial review**. Product formats are merchant descriptions, not Final Vestige user tests. Seller's one-year refund statement does not establish a user's eligibility, checkout conditions, timing or affiliate permission.

**Seller Total Focus — `https://hypnosislive.com/mental-skills/total-focus` inspected 2026-11-02:** seller describes a **33-minute, 47 MB** recorded session by J. A. Amos; statements about changing brain function, getting more done or guaranteed concentration are **seller promises, not independently proven outcomes**. IMPORTANT: fresh live page presented one price/discount, while another search-rendered version retrieved during the same research showed a different price. **No price, discount, value comparison, refund promise or urgency is approved for email.** The page refers to a **14-day** guarantee; caveats and refund eligibility require terms/checkout verification before inclusion.

**Affiliate authorization:** `https://affiliates.inspire3.com/` offers registration but does **not** prove publisher acceptance, tracking-link format or permitted email channel. Public `https://inspire3.com/ll/` offers Limitless Labs-specific copy and says approval is required for that **different product**. Neither authorizes Final Vestige Zen12 or Total Focus campaign creative. A scoped read-only Gmail search on 2026-11-02 surfaced historical **consumer promotions**, not affirmative named-product Final Vestige email marketing permission; an unsuccessful scoped search is not evidence that permission cannot exist elsewhere. NO merchant contacted. NO links activated.

**Compliance:** [FTC CAN-SPAM business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires nondeceptive identity/subject, promotional identification, valid publisher mailing address and meaningful opt-out. An Automattic or Inspire3 address does **not** automatically qualify as Final Vestige's business postal address. Never place a placeholder, merchant street address or home address into publicly deployed copy as a workaround. Affiliate disclosures must be clear in the actual email (including the excerpt and the particular offer) and on the buyer guide, not only on a separate generic disclosure page.

## Six-slot decision ledger (no send authority)

| Slot | Type | Draft-readiness blocker | Destination status |
| --- | --- | --- | --- |
| 01 — perception | editorial | Final approved subject/version, native excerpt+footer and opt-out, audience | Existing historical page; verify final intended CTA |
| 02 — Puységur | editorial | Distinguish recorded 1784 source from later interpretation; final copy, delivery evidence | Existing Puységur research live |
| 03 — Zen12 | commercial | **HOLD_MERCHANT**: account/EMAIL channel permission, approved offer guide, claim/current terms, prominent first-excerpt disclosure | **Not-live guide; no earning link** |
| 04 — Apollo 1 | editorial | **14 vs 17-second subject drift**; founder must approve accurate selected version | Historical article live |
| 05 — Total Focus | commercial | **HOLD_MERCHANT**: account/EMAIL permission, updated offer guide, variable price/terms, prominent disclosure | **Not-live guide; no earning link** |
| 06 — evidence log | editorial | Approved original/current version and accurate Fieldbook statement; rendered email | Existing `/focus/` live |

**One CTA per issue**; do not treat a prospective commission note as an additional CTA. Four historical/editorial letters and two explicitly disclosed commercial slots remain fixed. The R65/R67/R71 alternatives have **not** been approved as canonical replacements. R72 proposed custom excerpts have **not** been installed.

## Required human evidence before changing any of the above holds

1. Independently select and attest the six exact final manuscript/subject/excerpt versions; resolve Apollo 1's disputed number. No unilateral canonical rewrite.
2. Establish publisher-controlled valid US postal address privately; verify it appears in both MIME alternatives of the actually received commercial email, and that Jetpack has not substituted a merchant or Automattic address.
3. Obtain **separate** founder approval before any actual native WordPress email send or test. Inspect native preview without publishing. Verify the received HTML and plaintext, subject and inbox snippet, mobile legibility, link destinations, disclosure, physical address, and unsubscribe mechanism.
4. Verify unsubscribe link functionality only in authorized test using a controlled test recipient; do not click any live subscriber's private token, and do not publish its URL.
5. Privately reconcile actual recipient email-status counts. Never export identifiers to GitHub or assume confirmed = deliverable.
6. For #03/#05 obtain documentary proof of Final Vestige-specific account acceptance, email permission, approved earning URLs/creative rights and published approved Mind Studio buyer guides. Verify current seller policy and pricing at the contemplated date.
7. Only after all items and explicit founder approval of final recipients/timing can there be a send decision. **Repository tests have no power to authorize.**

## Metrics acceptance without false inference

Measurement is dormant until authorized release. After a real send, distinguish known eligible recipients, attempts, accepted delivery, unsubscribes, unique **site** CTA visits and merchant outbound visits; attribute merchant purchases **only** to merchant-confirmed records. Keep anonymized aggregate counts. With a list that may contain only two confirmed registrations, no A/B significance claims, fabricated impressions, attribution cookies or newly paid services.

**Final gate:** `ALL SIX = HOLD_UNSENT`; `03/05 = HOLD_MERCHANT`. No WordPress writes, draft post creation, scheduling, test send, real send, subscriber import, marketing outreach, tracking activation or affiliate links in this R74 change.
