# Dispatch R246 — Merchant-specific price identity and conversion proof packet

**DRAFT / HOLD_UNSENT.** Issue #174; original campaign PR #175 at d57ccdba3aee8f065e143e101c2945f4f3d01647; prior QA #201 and R245 #1824. This branch adds separate review files, changes NO original manuscripts, homepage PR #49, live site or email settings.

## Material commercial finding: Zen12 has two different merchant-controlled offers

On November 9, 2026 the seller-controlled https://zen12.com/hnp showed the Zen12 Premium program (12 levels, 48 MP3 recordings) at an advertised $87.99. The seller-controlled https://zen12.com/secret/ showed a $37 price subject to a displayed coupon and countdown. Neither is authenticated checkout pricing or a proven identical transaction, SKU, buyer terms, commission, or approved Final Vestige earning destination. Do not copy coupon, countdown, false urgency or implied discount into newsletter. Specific offer identity must be authenticated before any commercial CTA activates.

Both pages describe strong cognitive benefits. They are seller assertions, not independent proof that twelve minutes equals an hour of meditation. The official sales pages do not demonstrate named Final Vestige affiliate acceptance, issued links or EMAIL-channel permission. Mind Studio remains owner. Issue #171 newest R256 PR #1826 agrees the two pages must not be presumed equivalent.

## One purchase-intent hypothesis, not another email blast

Audience: existing consented readers who voluntarily engage with the Focus Fieldbook's evaluation of meditation audio. Do not assume historical investigation readers want paid meditation products. Journey: Grok asset_id and utm campaign → qualified human visit → Focus → provider-confirmed signup → editorial Dispatch story → optional approved Zen12 buyer guide → merchant-issued earning URL → independently reconciled paid commission. The approval-dependent Issue 03 CTA should lead to the vetted *Final Vestige guide*, not directly to an arbitrary seller page. Commercial issue 05 remains distinct and blocked. Four other newsletters stay editorial.

R246 includes an optional source-grounded Issue 03 manuscript and email-safe HTML review specimen. These are alternatives only, NEVER substituted without founder approval. Near-CTA prospective commission language must clearly explain the potential financial relationship, not merely say affiliate.

## Subscriber diagnostics — verified config vs undelivered proof

At 2026-11-10T02:36:07Z an authenticated Jetpack read returned newsletter ON, post auto-send OFF, format full, Fieldbook welcome configured, total=3, confirmed=3, unconfirmed=2, suppressed=0. Five recent post notifications were never sent, intentionally opted out. Counts are nonadditive; actual email-eligible people remain UNKNOWN, not 3 or 0. Configured welcome does not prove receipt.

Official WordPress guide https://wordpress.com/support/subscribers/ (last reviewed Nov 4 2026) distinguishes Email subscription status Subscribed from Reader-only Not subscribed, Not confirmed, Bounced, Emails paused and Not sending. Action: in private Jetpack → Newsletter → Subscribers filter Email subscription=Subscribed; record only the aggregate filtered count and date, never export identities. For any confirmed_signup conversion event require a provider-observed confirmation transition, one per privacy-safe opaque provider ID. A form submit, PDF click, email-only follower count or Reader count is not a confirmed lead.

Existing /dispatch/ (WP page 523) does not explicitly mention commission-bearing recommendations, but /focus/ (page 1579) does. Proposed non-live consistency wording is in SIGNUP_DISCLOSURE_ALIGNMENT.md. No legal violation is inferred from this mismatch.

## CAN-SPAM, publisher identity, preview

FTC business guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires truthful subjects/senders, valid sender postal address, and clear usable opt-out on applicable commercial messages. FTC endorsement guidance https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking emphasizes a conspicuous disclosure CLOSE to paid recommendations. Automattic's corporate address in a subscription-confirmation message does not prove Final Vestige's valid postal address.

WordPress official preview guidance last reviewed November 9, 2026 https://wordpress.com/support/newsletter/email-appearance/ says native Preview email can be used with the per-post sending toggle OFF. A visual preview does not prove final received-email MIME, physical address, unsub link or actual welcome delivery; separate founder authorization is needed for WordPress draft creation or any test send. No native preview/test was performed.

## Revenue evidence contract and owner work plan

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Zen12 → guide and checkout | Named affiliate EMAIL permission, issued URL, two inconsistent seller offers | Authenticate issued URL, exact SKU, seller checkout and refund; approve live guide | FAIL/HOLD_MERCHANT, two seller-page displays are not checkout proof | Mind Studio |
| Focus → confirmed lead | Subscriber eligibility/double opt-in unknown | Record redacted aggregate Subscribed status and provider transition; deduplicate | UNKNOWN; counts nonadditive | Focus / Claude |
| Dispatch → inbox | Received postal footer, opt-out and MIME unverified | Separately authorized native preview then actual received test | NOT TESTED | Dispatch / Site QA |
| Editorial → voluntary buyer | Unapproved conversion copy/offer guide | Test source-aligned optional CTA only after partner and founder approvals | BUILT DRAFT / NOT LIVE | Dispatch / Mind |
| Qualified session → net revenue | No authenticated paid orders or qualified denominator | Settlement, refunds, fees, 7-/30-day cohort source joins | NOT COMPUTABLE | Commerce / Praxxis |

Net revenue per 1,000 qualified humans, paid orders and verified commissions are NULL/UNKNOWN, NOT zero. Clicks, impressions, downloads, signup attempts and anecdotal feedback are not paid sales; tiny samples prohibit meaningful A/B inference.

## Global release lock

No emails or test messages, scheduling, WordPress drafts/posts/settings, list imports/contacts, affiliate links, live landing pages, scripts, paid tools, social publishing or deployment. Final separate founder approval for recipient/audience, content, timing and sending is indispensable even after every gate can be documented.