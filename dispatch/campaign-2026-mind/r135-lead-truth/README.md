# Dispatch R135 — native signup truth and conversion-first visitor proof

**DRAFT / DO NOT DEPLOY / DO NOT SEND.** Stacked on Dispatch R134 draft PR #1072, preserving original master #175 (4 editorial / 2 commercial), WordPress production, subscriber list and frozen homepage PR #49. Owns only Dispatch/Focus consent, attribution and editorial QA. Merchant eligibility belongs to Mind #171; site engineering to Claude.

## Verified source findings (2026-11-05, authenticated WordPress)
- Published `/dispatch/`, page ID 523: WordPress `pages_get` returned a Subscribe-block HTML projection containing an anchor to `https://finalvestige.com/?post_type=page&p=523`, not an email input or form.
- Published `/focus/`, page ID 1579: same projection pattern: an anchor back to page 1579 labelled “Send me the fieldbook”; no input/form inside its returned Subscribe block, although page CSS styles an email input.
- **Caution:** neither projection proves broken signed-out visitor behavior. Native Jetpack permits button-only subscriptions that open a modal, and WordPress may alter output by authentication context. Public fetch was inaccessible, local network DNS unavailable. Actual visitor DOM and modal behavior **NOT VERIFIED**.
- Clear source-level behavioral defect on Focus: inline `<script id="fvf-gift-v2">` reveals the free PDF gift prompt for **any truthy** `subscribe` query value not in `['invalid_email','error','blocked_email','opted_out','blocked']`. Consequently `?subscribe=pending`, `?subscribe=false`, `?subscribe=unsubscribed` or `?subscribe=garbage` are treated as success for gift-panel display. This is misleading UI, not evidence of a sent email, purchase or paid bypass (the PDF is public). A CSS `is-subscriber` class alone does not prove an eligible new email lead.
- Existing welcome text includes the free 52-page Fieldbook PDF URL; actual received welcome, working unsubscribe and publisher postal address remain unverified.

## Proposed, NOT LIVE solution
- `focus-gift-v3-PROPOSAL.js`: allow exactly one `subscribe=success` URL result for a public gift UI prompt. A native subscriber UI class can also reveal the public gift, but **neither emits confirmed_signup**. The exact allowlist is a conservative proposal pending signed-out WordPress verification of legitimate native outcomes; it is not release-approved.
- `signup_truth.py`: offline CMS-projection classifier; source-safe return-state classifier; pseudonymous deduplication of independently verified native status transitions; recipient eligibility only from `Email subscription = Subscribed` provider filter. Unknown aggregates return null, not zero.
- `test_signup_truth.py`: 16 native Python guard tests; `browser_gift_qa.py`: 16 offline Chromium behavioral cases comparing the **observed original snippet** with proposed v3. These are synthetic/browser-local checks, NOT native live signup or inbox evidence.
- `reviewer.html`: accessible offline evidence board for cross-workstream review.

## Precise QA runbook — zero sends
1. Open both live pages in a NEW, signed-out browser (no site owner cookies) at 320, 390, 768 and 1440px; inspect the actual Subscribe form or button-only modal, focus and keyboard label. A same-page link without usable form/modal is a P1 acquisition blocker. Record sanitized screenshot/DOM without subscriber addresses.
2. Inspect harmless GET-only `?subscribe=success`, `?subscribe=pending`, `?subscribe=false`, and random token states **without entering an address or submitting a form**. Distinguish “submission acknowledged” from confirmation. Do not count public gift displays or downloaded PDFs as leads.
3. Privately filter Jetpack → Newsletter → Subscribers by `Email subscription = Subscribed`; retain **only an aggregate**. Distinguish `Not subscribed`, `Not confirmed`, `Bounced`, `Emails paused`, and `Not sending`. Aggregate total=3 / confirmed=3 / unconfirmed=2 is nonadditive and is **NOT** email recipient eligibility.
4. In WordPress's native editor, review a **non-sending** full/excerpt email Preview. Verify the visible CTA link, subject and preheader, disclosure beside 03/05 commercial offers, proper sender identity, Final Vestige's *own* valid physical postal address, and functioning unsubscribe. No test email without explicit final approval.
5. Define `confirmed_signup` ONLY for independently verified native first transitions with checked consent provenance and non-PII surrogate; deduplicate repeated attempts. A new subscriber is not a sale. Compare 7/30-day qualified-human sessions to independently verified settled Payhip orders / authorized merchant-paid commissions, refunds and fees. If missing, net realized revenue per 1,000 human sessions is NULL.

## OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
| Offer / step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Fieldbook → confirmed lead | CMS projects same-page links on both pages | Signed-out native form/modal + keyboard QA | **Projection verified; live behavior UNKNOWN** | Claude / Site QA / Dispatch |
| Fieldbook → welcome | Truthy query can fake gift-panel success | Exact-token allowlist, never issue lead event | **Local Chromium 16/16, native Python 16/16; NOT LIVE** | Dispatch / Claude |
| Dispatch → first-party guide | Excerpt modeled to truncate all 6 primary CTAs | Native preview, retain opt-out, no settings change | **Earlier source model only; no inbox** | Dispatch / Claude |
| Zen12 or Total Focus → buyer | Named accepted affiliate, email channel rights, exact live guide missing | Mind #171 merchant entitlement / checkout verification | **HOLD_MERCHANT** | Mind Studio |
| Grok → realized revenue | No reconciled paid orders, fees, human sessions | Source-tagged 7/30-day cohorts | **NOT COMPUTABLE** | Praxxis / Claude |

## Compliance and original historical identity
Retain 4 history/evidence-first editorial issues and just 2 conditional offer issues. Commercial messages require honest subjects, near-offer commission disclosure, independently verified Final Vestige postal address and unsubscribe. The 2026-10-25 Automattic confirmation email does **not** establish Final Vestige's legal mailing address or a received Fieldbook welcome. Partner approval, email marketing authorization, exact earning link, pricing, checkout, refund and scientific efficacy remain unverified. No messages sent, subscriber data exposed, list imported, merchant activated, WordPress content/settings changed, or analytics scripts added.

Sources: [Jetpack Subscribe form and modal](https://jetpack.com/support/jetpack-blocks/subscription-form-block/), [WordPress email subscription statuses](https://wordpress.com/support/subscribers/), [WordPress Newsletter and preview](https://wordpress.com/support/newsletter-settings/), [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [Zen12 seller](https://zen12.com/hnp), [Total Focus seller](https://hypnosislive.com/mental-skills/total-focus). Seller-specific efficacy claims are advertising, not independent proof.

**RELEASE: ALL SIX HOLD_UNSENT. 03/05 ADDITIONAL HOLD_MERCHANT.**
