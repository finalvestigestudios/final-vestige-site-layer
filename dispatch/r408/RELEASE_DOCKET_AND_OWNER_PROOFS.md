# R408 — Recipient truth, inbox compliance and commercial conversion docket

**Status:** DRAFT / HOLD_UNSENT. Read-only evidence only, 2026-11-16 21:38:56 UTC. Owner: Dispatch Campaign Studio. Parent: [R407 draft #2784](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2784). Canonical six-issue master: [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), campaign [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); Mind owner [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Do not edit the frozen flagship homepage PR #49.

## What was actually observed

Authenticated WordPress.com Jetpack Newsletter **status**: newsletter can send technically, zero platform send blockers, but last five post notifications all `never_sent_opted_out`; site-wide default for emailing new posts **OFF**. **Settings**: subscription enabled; full post content; From name Final Vestige Studios; reply mode no-reply; welcome text configured with the existing 52-page Fieldbook PDF. None of those settings was changed.

The subscription-status API reports total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**. The separate Jetpack Stats followers API reports WordPress.com **3**, direct email **0**, comment **0**, aggregate total **3**, partial=false. **These APIs use different reporting categories; the values are NOT additive, nor is the distinct deliverable email audience proven to be zero.** Public dashboard metrics are not sufficient to deduplicate identities, prove per-subscriber email consent, show that the welcome email actually arrived, or establish a valid commercial-recipient segment.

The existing /dispatch/ and /focus/ pages were inspected read-only; the [Editorial Standards](https://finalvestige.com/editorial-standards/) require source fidelity, correction accountability, and independence of historical conclusions from affiliate commerce. An earlier connected Gmail email is a **subscription confirmation**, not proof of welcome/Fieldbook receipt; promotional Inspire3 mail received as a customer is **not** evidence of Final Vestige affiliate program acceptance or authorization to promote products by email. We do not include or publish any subscriber email addresses or account identifiers.

The committed [aggregate witness](./WP_JETPACK_READONLY_20261116.json) redacts PII and records unavailable proofs as `null`; `null` is *unknown*, not false. The [recipient_truth.py](./recipient_truth.py) reducer deliberately returns `HOLD_UNSENT`, never produces a confirmed_signup count from aggregate totals, never computes revenue without independent settlements, and has **no sending or network code**.

## Decisions against the six canonical emails — unchanged

| # | Canonical subject | Channel | Current gate | Primary action |
|---|---|---|---|---|
| 01 | The mind is not a camera | Editorial | HOLD_UNSENT | Source-check live editorial CTA and actual inbox subject |
| 02 | Before hypnosis had a name | Editorial | HOLD_UNSENT | Preserve investigative history; avoid duplicate issue 01 CTA |
| 03 | The twelve-minute meditation question | Commercial opportunity 1/2 | HOLD_MERCHANT + HOLD_UNSENT | Zen12 named EMAIL rights and approved warm-up guide |
| 04 | Fourteen seconds. A much longer explanation. | Editorial | HOLD_COPY + HOLD_UNSENT | Evaluate NASA event-clock correction from optional R400 |
| 05 | Before you press play on a hypnosis audio | Commercial opportunity 2/2 | HOLD_MERCHANT + HOLD_UNSENT | Total Focus exact SKU, refund limit and email rights |
| 06 | What did seven days of attention reveal? | Editorial | HOLD_UNSENT | Avoid repeated welcome-download CTA; consider R407 source-led alternative |

The four-editorial / two-commercial composition is protected. Optional R399–R407 alternatives remain **NOT_ADOPTED**, never direct substitutes. No new post, newsletter list, platform, paid tool, scheduled email, active affiliate CTA or tracked redirect is authorized.

## Conversion-first path and per-owner evidence request

**Audience hypothesis:** a person arriving from a *specific* Grok YouTube/TikTok historical-perception clip may prefer a concrete evidence exercise before exploring a meditation recording. The funnel is **Grok asset_id + campaign → qualified-human visit → /focus/ opt-in → provider-authenticated distinct confirmation → received welcome/Fieldbook → source-led editorial guide → APPROVED Zen12 buyer guide → allowed earning link → referred checkout → independently paid commission less refunds/fees**. The last three steps are proposals, not a live earning path.

1. **Claude / Focus**: In the existing consent layer, specify the *single* `confirmed_signup_v1` event only after provider-authoritative confirmation and email eligibility, with privacy-safe opaque deduplication key. Never fire it from `?subscribe=`, PDF downloads, front-end submit clicks, WordPress.com follower totals or raw-email strings. Document a safe proof of actual received welcome and 52-page PDF retrieval. No new tracking script or changes without founder approval.
2. **Dispatch / Founder**: Witness genuine non-sending WordPress **Preview email** at desktop, tablet and mobile for each approved issue; record actual subject (= post title unless independently established otherwise), preheader behavior (UNKNOWN), unambiguous sender, single CTA, legible sources and actual legal footer. The WordPress connector does not expose editor-native Preview email; offline HTML is **not proof**. Never click **Send test email** without explicit final campaign permission.
3. **Founder**: Verify a real **Final Vestige Studios publisher physical postal address** appropriate for commercial mail, not the Automattic address in a provider confirmation and not the merchant's address. Confirm genuine per-email unsubscribe link/functionality and suppression propagation; do not put a guessed address or mock unsubscribe URL in an actual email.
4. **Mind & Affiliate Studio #171**: Confirm **Final Vestige named affiliate acceptance**, permission **specifically for the email channel**, approved exact SKU and earning-link form, copy/creative restrictions, actual reader-facing buyer-guide route, product and checkout/refund terms, then provide evidence to Dispatch. Public affiliate portals and received consumer advertisements are insufficient.
5. **Grok / Praxxis / Claude #820**: Reuse existing creator and first-party analytics infrastructure only. Use genuine asset identifiers; attribute campaigns to consenting humans, not bot visits; independently reconcile paid orders, fee deductions, refunds and attribution windows. Revenue per 1,000 qualified-human sessions is **NOT COMPUTABLE** until both audited numerator and denominator exist.

## Specific official seller claims checked (not adopted by FV)

- [Zen12 official offer](https://zen12.com/secret/) advertises a coupon price on a particular public funnel, twelve levels and forty-eight MP3 recordings; other official pages present different offers. **No price is included in any approved email**, because the intended referred checkout is not attested. Claims of superior meditation outcomes or ancient proof remain vendor marketing.
- [Hypnosis Live: Total Focus](https://hypnosislive.com/mental-skills/total-focus) describes one 33-minute, 47 MB recording and promotional personal-effect promises. These have not been independently established.
- [Hypnosis Live official FAQ](https://hypnosislive.com/faq) describes a 14-day refund window **and a maximum of five refunded sessions per year**. Any future buyer guide must present the complete terms and verify the exact referred checkout; avoid volatile dollar figures.
- The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires honest headers/subject, valid publisher physical address, clear opt-out, honoring unsubscribe within 10 business days, and commercial identification. Affiliate disclosure adjacent to any qualifying offer is additionally necessary for editorial trust; a generic footer link is not enough.
- [WordPress native Preview email documentation](https://wordpress.com/support/newsletter/email-appearance/) distinguishes **Preview email** (non-sending) from **Send test email** (sends mail). Neither was executed here.

## Release checklist — fail closed

Before even *reviewing* an email for final approval: site still new-post auto-send OFF; canonical subject and CTA match actual editor; email-specific proof of distinct eligibility, welcome, received PDF, current named email permission for commercial entries, accepted guide and issued tracking URL, FV physical address, verifiable unsubscribe and mock-free/native preview all witnessed. Founder approval for each intended send remains a **separate action** and is not granted by passing any automated validator.

**Reporting:** No genuine sends, experiment sample, verified paid orders or qualified-human sessions are established. Do not report open/click figures as sales, and do not divide by zero or fill missing commission figures with guessed zero. Report `NOT_COMPUTABLE` for realized net revenue/1,000 qualified human sessions in 7-day and 30-day cohorts.
