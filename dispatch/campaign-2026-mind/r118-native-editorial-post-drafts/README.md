# Dispatch R118 — Native post-draft bridge (HOLD / NO SEND)

2026-11-04. Stacked on draft PR #962, parent commit 39f00a8701ac22903188e4831e6623c81b724e86. Master PR #175 at exact d57ccdba3aee8f065e143e101c2945f4f3d01647. Owner evidence: Issue #174. All these files are added only within a new R118 subdirectory; no WordPress, published post, homepage, or subscriber data is changed.

## The actual gap

R116 supplied offline HTML/plaintext, and R117 provided six excerpt candidates. Neither supplied controlled, origin-traceable WordPress post-body candidates to pair with those excerpts under the site's native Jetpack excerpt delivery. This R118 bundle adds four original-source editorial post-body candidates in Gutenberg paragraph/list markup with exact SHA custody and one first-party CTA each. Two commercial editions have NULL post bodies and explicit merchant hard holds. These are OFFLINE candidates, not API-ready payloads or WordPress editor previews. Their display subject must be the WordPress post title in the eventual real send; a distinct native preheader capability is not verified.

## Verified live snapshot — November 4, 17:31 UTC (read-only authenticated WordPress)

Newsletter enabled, new-post send default OFF, email format excerpt; five latest post notifications 'never_sent_opted_out', site_can_send true but reachable audience unknown. Diagnostics: total=2, confirmed=2, unconfirmed=2: DO NOT ADD these figures. Published Focus page ID1579, Dispatch page ID523 and Editorial Standards ID17 were inspected; both signup pages use native Jetpack Subscribe block. Dispatch's promise 'when we publish them' does not align automatically with intentional opt-out defaults. No settings or content changed. No valid publisher postal address, true received email or working unsubscribe was verified.

The 52-page Fieldbook welcome message is configured. Media record ID1737 identifies a 599,946-byte PDF at the same public URL, but actual PDF transfer, final page count and inbox receipt remain UNKNOWN. Issue 06 proposes this URL to existing readers to avoid another subscribe loop, with an explicit delivery-verification HOLD.

## Copy and editorial safeguards

Issue 04 originally says 'Fourteen seconds'. Its underlying measurement is not defensibly established; the candidate post title is 'Apollo 1: what the fire record actually says', with the original retained in an audit field, NOT approved replacement. Original investigative and evidence distinction is preserved. Issues 01/02/04/06 were converted only from manuscript content between source separators; the unsatisfied legal footer placeholders are NOT put into a public body. Every output draft remains HOLD_UNSENT.

Issues 03 and 05 are reserved (not replaced). Their source manuscripts are untouched. The seller pages https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus describe formats, seller claims, and time-sensitive offers. Zen12's 12-minute equivalence and Hypnosis Live's 'reprogram' concentration promises are SELLER claims, not independently verified product-specific outcomes. Public merchant pages and an affiliate portal do not establish Final Vestige partner approval, email-promotion permission, final pricing/refund applicability, creative rights, proper tracking or actual paid commissions.

## Consent, newsletter, and commercial legal gate

Official FTC CAN-SPAM business guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . For commercial promotional messages, use truthful subject/from headers, clear advertising nature, valid FINAL VESTIGE physical postal address and functional opt-out; opt-out must remain possible and timely. Automattic's address does not satisfy the publisher's. A native WordPress editor preview cannot prove receipt, unsubscribe token operation, welcome delivery or final checkout. Do not submit actual signup, publish, send a test email or alter Jetpack settings without founder's specific final approval.

## Run independent candidate code checks

node --test dispatch/campaign-2026-mind/r118-native-editorial-post-drafts/tests/test_native_post_bridge.mjs

This source package does not include a CMS-import script or any network calls. Passing local source tests is NOT actual WordPress rendering, hosted CI, browser proof or deliverability. Real editor staging/browser inspection must remain with Claude and Site QA; require exact Gutenberg content, title, explicit excerpt, per-post send OFF, preview with REAL native WordPress output, postal/unsubscribe checks and mobile widths 320, 360, 390, 768, 1440 before any release.

## Conversion-first funnel admission (one eventual purchase, not newsletter volume)

Social video and channel work stay with Grok/Praxxis in TASK-008. Claude owns analytics/commerce. Dispatch owns consent, welcome, source-tagged link and honest email follow-up. A candidate journey is source asset_id to /focus/ to authoritative confirmed signup to actually received welcome/download to one evidence-rich Dispatch issue to ONE vetted first-party buying guide to a seller-authorized commercial link to independently reported paid order minus fees and refunds. Product choice remains unapproved until Mind Studio verifies exactly one authorized offer and buyer terms.

Proposed attribution nomenclature only: utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_mind_pilot_2026_11, utm_content=issue_01..06. WordPress auto-generated read-more link and native attribution must be independently validated; this release does NOT append or deploy UTMs. A click, subscriber or checkout start NEVER counts as a paid order. All 7/30-day monetary KPIs require qualified-human session denominator plus merchant verified paid orders, refunds/fees and privacy-safe customer deduplication. Current net revenue per 1,000 qualified sessions = NOT COMPUTABLE (not zero).

## Top blockers and owners

1. ONE commercially sellable offer, authorized email channel, exact permitted link/creatives, live first-party buyer guide, current checkout/refund, privacy-safe partner payout reporting — Mind & Affiliate Studio.
2. Authenticated reconciliation of WP followers vs actual email-eligible subscribers; received welcome MIME and successfully retrieved PDF; genuine Jetpack email excerpt/CTA preview and opt-out — Dispatch + Claude + Site QA, read-only unless specifically approved.
3. Business postal address and explicit approval of exact six messages, audiences, schedules — Founder.
4. Qualified Grok asset IDs with native link affordances; source-to-sale attribution and independently confirmed orders — Grok/Praxxis/Claude.

RELEASE: ALL SIX HOLD_UNSENT, Issues 03/05 EXTRA HOLD_MERCHANT. No emails, test sends, CMS posts, account spend, affiliate link activation, subscribers, or commerce changes were performed.
