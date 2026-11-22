# Dispatch R307 — a client-side "download ready" is NOT a confirmed subscriber

**Read-only production observation** — 2026-11-12 14:39 UTC. This finding concerns `/focus/` WordPress page 1579, last modified Nov 5. No WordPress edits, forms submitted, list exports, email sends, or tests against real recipients.

## Exact relevant current behavior

The published `fvf-gift-v2` script reads `new URLSearchParams(window.location.search).get('subscribe')` and shows the otherwise hidden `#fvf-gift` whenever this parameter has *any non-empty value* other than `invalid_email`, `error`, `blocked_email`, `opted_out`, `blocked`. It can also show the gift when the Jetpack subscription container gains CSS class `is-subscriber`.

**Adversarial proof from the script's own conditional:** `?subscribe=pending`, `?subscribe=0`, `?subscribe=anything` and `?subscribe=BLOCKED` all reveal **“Your fieldbook is ready to download.”** The URL value is not an authenticated provider-confirmation assertion. The `is-subscriber` CSS class is not evidence of a *new* transition. The PDF is publicly linked separately, so the display itself need not be gated, but it MUST NOT be reinterpreted as `confirmed_signup`.

This is a reproducible **UI/analytics interpretation risk**, not evidence the existing analytics actually emits a wrong event. The current page script itself does not emit `confirmed_signup`.

## Conversion-first recommendation; Claude owns live code

Replace success-dependent gift display with an **always-visible, clearly labeled** free PDF download so a reader is never told that clicking or showing a gift confirms their email. Suggested adjacent copy: “You can download the free Fieldbook now. If you subscribed, check your inbox for a confirmation request; the download itself does not confirm or change your email subscription.” Keep the Jetpack signup separate, optional, and use the same list. Do not hide the gift from people who want the PDF without joining the list. If owner prefers gated post-submit display, only use provider-supported *verified status*, not arbitrary URL values, and preserve the public PDF route as currently promised.

Never count the following as `confirmed_signup`: rendering the gift, `subscribe` query values, clicking the PDF, submitting a form, Reader following, a Jetpack welcome configuration string, or a recipient confirmation message that has not been followed by authoritative subscriber-status evidence.

## Non-sending first-party event acceptance

A future `confirmed_signup` requires one independently verified Jetpack email-subscription transition into `Subscribed`, with relevant consent, delivery eligibility and durable deduplication performed in the existing authorized analytics architecture. The offline code produces only `STRUCTURAL_CANDIDATE_ONLY`; actual trusted server source, persistent deduplication and event emission remain Claude-owned and **unverified**. No email addresses or user IDs belong in repo, browser payloads or GitHub issue comments.

Source references: live `https://finalvestige.com/focus/` page + authenticated WordPress page 1579; [WordPress subscribers statuses](https://wordpress.com/support/subscribers/); [Jetpack subscription confirmation](https://jetpack.com/support/subscribe-to-a-site/). Source handling follows `https://finalvestige.com/editorial-standards/`.
