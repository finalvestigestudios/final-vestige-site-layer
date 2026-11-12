# Dispatch R311 — non-sending provider preview, consent and revenue proof

**Date:** 2026-11-12. **State:** ALL SIX HOLD_UNSENT; commercial 03 and 05 additionally HOLD_MERCHANT. This is a NEW independent R311 review package. Original master PR #175 (SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`) remains immutable. Existing R310 Gutenberg specimens in draft PR #2228 (SHA `16515e72b0d3d359175271b637d03944507f9f6b`) remain untouched; earlier independent per-edition PR #201 remains separate. Frozen homepage PR #49 untouched.

## Material new finding: a real provider-side NON-SENDING preview path exists

Official WordPress instructions explicitly say that when the per-post **Send this post to subscribers** control is OFF, the pre-publish Newsletter panel displays **“This post won't be emailed”** and still provides a **Preview email** link. The nearby **Send test email** control is NOT permitted in this campaign, nor are publishing, scheduling and creating WordPress posts/drafts. The preview is therefore a feasible *future owner-authorized review path*, not a test that has occurred. [Official sending/preview guide](https://wordpress.com/support/newsletter/send-newsletter-emails/) and [disable emails guidance](https://wordpress.com/support/newsletter/disable-newsletter-emails/) (last reviewed 2026-10-06).

Actual rendered Jetpack preheaders, legal footers, opt-outs and MIME remain UNVERIFIED. PR #175 preheaders are copy proposals, not established native inbox metadata. Post title supplies subject. A WordPress.com host postal address is not proof of the Final Vestige commercial sender's own address.

## Authenticated read-only site snapshot: 2026-11-12 18:30 UTC

- Jetpack newsletter enabled, site_can_send true, **email_new_posts_by_default false**, format **full**, sender **Final Vestige Studios**, reply-to **no-reply**, category targeting OFF.
- Welcome contains the existing 52-page Focus Fieldbook URL. Actual received welcome / accessible download in recipient inbox NOT VERIFIED.
- Subscriber diagnostics **total 3 / confirmed 3 / unconfirmed 2 / suppressed 0 / paid 0**. These populations are not additive. Actual opt-in email-eligible recipient count UNKNOWN. Do not emit real `confirmed_signup` from count, follower number, URL query or gift panel visibility.
- Five recent post send diagnostics: `never_sent_opted_out`. This is NOT evidence of lifetime zero sends.
- `/dispatch/` (ID 523), `/focus/` (ID 1579) and `/editorial-standards/` (ID 17) were authenticated read-only on this run.
- Targeted Gmail queries for account-specific Inspire3 acceptance, EMAIL rights and completed Dispatch welcome found no matching messages; search results cannot prove the private agreement does not exist.

## Business and copy decision packet

| Issue | Type | Most important unresolved blocker |
|---|---|---|
| 01 | Editorial | Duplicates Issue 02 Puységur destination |
| 02 | Editorial | Same CTA as Issue 01; compare R300 alternative, not adopted |
| 03 | Reserved commercial | Zen12 email authorization, issued link and LIVE vetted guide absent |
| 04 | Editorial | Original “Fourteen seconds” subject historically unsubstantiated; compare R302, not adopted |
| 05 | Reserved commercial | Hypnosis Live email authorization, guide and checkout verification absent |
| 06 | Editorial | Existing subscriber routed to /focus/ signup; consider retaining reader directly at PDF, not adopted |

Preserve the founder's 4 editorial / 2 commercial pilot. Do not rewrite original manuscripts or quietly adopt alternate letters. Sources remain aligned with Final Vestige's [Editorial Standards](https://finalvestige.com/editorial-standards/).

**Commercial research:** Seller pages [Zen12](https://zen12.com/about) and [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus) describe respective formats and make product benefit claims; neither independently proves efficacy. [Inspire3 affiliate application](https://affiliates.inspire3.com/) is NOT Final Vestige-specific acceptance, EMAIL-channel permission, earning-link format, royalty statement or approved creative. Price/guarantee snapshots may vary; do not freeze price or refund promises into email. FTC disclosure must be near qualifying paid recommendation; actual publisher postal address and functional unsubscribe require specific verification.

## New independently executed proof

- Native PR #175 Python suite: **6/6 PASS** against eight locally inspected original blobs with exact Git SHA comparison to the GitHub PR #175 HEAD.
- New R311 native `unittest` suite: **16/16 PASS**, using the supplied immutable PR #175 manifest; includes four editorial/two commercial isolation, missing owner approvals, six unsent states, adversarial provider signup proof, duplicate paid orders and gross-minus-refunds-minus-fees synthetic arithmetic, CTA duplication, Apollo source redline and returning-subscriber risk.
- The R311 module has **no network, email, WordPress, browser, tracking, sender or subscriber read/write code**. Even 100% booleans return `send_authorized=false`: passing a gate means only a hypothetical **human review candidate**, never approval to send.
- Read `preview-witness.md` for the safe evidence capture path, `merchant-claims.json` for seller/product limits, and `snapshot.json` for non-identifying observed settings.
- These tests are synthetic/local source-level acceptance tests; they are NOT live customer outcomes or native received Jetpack render evidence.

## Priority-one conversion work

1. Mind/Commerce Issue #171 obtains private verifiable approval for **one** product, email channel, earning URL, first-party guide and independently auditable settlement. Until then commercial issues hold.
2. Focus/Claude Issue #129 privately verifies subscriber's **Email Subscription** status and double-opt-in/welcome transition; one deduplicated `confirmed_signup` event, and no second analytics script or email address leakage.
3. Founder/Dispatch Issue #174 resolves business postal address, true unsubscribe, native Preview email and source/subject corrections, then considers separate FINAL approval for an actual send. Never test send merely to measure.
4. Grok/Praxxis and Claude Issue #820 retain published social `asset_id` → genuine human qualified session → guide CTA → confirmed lead → **independently settled purchase less refunds/fees**; 7/30-day cohort definitions and attribution gaps exposed. Visits, opens, clicks and leads are not paid orders.
5. Net realized revenue / 1,000 qualified human sessions is **NOT COMPUTABLE** from existing evidence; do not report `0` or invented A/B effects.

No WordPress post, page, draft, settings, list, affiliate link, email/test email, social queue, analytics script, production code, merchant checkout, payment or spending was modified. New isolated draft PR and source-only artifacts; **all releases held**.
