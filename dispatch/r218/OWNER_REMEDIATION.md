# R218 — release-safe correction proposal (not approved, not live)

**Offer → step:** high-intent Focus reader → download / consent → Dispatch editorial nurture → optional approved Zen12 guide → independently reported paid affiliate sale. Never require a subscription to inspect independent merchant research unless the founder explicitly approves a different reader experience.

## Recommended minimal-scope correction for Claude / Focus #129
1. **Separate fulfillment from subscription status.** Treat the Fieldbook link as a free resource. Its visible availability or click is not `confirmed_signup`. Do not try to make a "verified subscriber" gate from URL params or DOM classes. If the product promise is that the download is available only after double opt-in, that requires a server-side provider-authorized gate and additional approved implementation; client JS does not supply it.
2. **Improve honest on-page language.** Proposed copy: "The Fieldbook download is a free resource. If you subscribed, please confirm through the email WordPress sends. Your welcome email includes the same link. Downloading the PDF does not confirm your subscription." Place immediately near the gift card. This proposal replaces the misleading implication that display itself proves a completed opt-in; do not rewrite the rest of the page or add a new list.
3. **Remove repeat-signup instruction** already proposed in R216: "If an in-app browser cannot open the PDF, open this page in Safari or Chrome, or use the link from your existing welcome message. There is no need to subscribe again." Avoid duplicated consent attempts.
4. **Consistent commercial expectations:** Dispatch page should disclose occasional commission-earning suggestions near the same existing subscribe block, as proposed in R216. Keep factual historical identity and independent sourcing.
5. **Do not instrument client success as a lead.** The only proposed `confirmed_signup` source is a privacy-safe, authenticated provider confirmation event after necessary consent/dedupe. If the platform cannot expose trustworthy per-event aggregates without addresses, mark confirmed lead attribution UNKNOWN, not zero.
6. **No new scripts before analytics review.** Claude should inventory existing events/UTMs before proposing changes. Respect Grok `asset_id`, `utm_campaign`, `utm_content` without personal identifiers, and site consent constraints.

## Reviewer acceptance criteria (no production write authorized here)
- Unit: `?subscribe=pending`, `?subscribe=failed`, arbitrary query and class-only state all produce **no `confirmed_signup` event**; gift visibility may remain free.
- Integration: exact URL and signup form stay intact; no new subscription provider, account, list or paid service.
- Copy: plainly distinguishes Fieldbook access from provider confirmation; link, PDF and existing welcome message remain functional. No repeated signup.
- Privacy: keep subscriber addresses, tokens, event receipts and backend secrets outside branches/comments. Only aggregated counts are posted.
- Provider: compare actual unique confirmed/eligible recipients against follower report privately; account for pending/unconfirmed and digest preferences. A public count is not a received-message proof.
- Delivery: true Jetpack email subject/snippet, legitimate publisher address, working unsubscribe, mobile rendering and real welcome arrival require **separately authorized** preview/received-message procedures. A local HTML preview cannot verify them.
- Commercial: Mind verifies named approval, EMAIL permission, earning URL and published guide; founder final approval. Issues 03/05 on HOLD_MERCHANT.
- Attribution: only independently settled orders/partner commissions minus fees/refunds count toward revenue. 7/30-day cohort KPI uncomputable without orders and qualified session denominator.

## Order of work, not a release authorization
1. Claude checks feasibility of small copy-only fix against current WordPress revision, with before/after screenshots and rollback.
2. Founder separately approves any live page change.
3. Focus/Dispatch verify provider-defined confirmed_signup and Fieldbook welcome using available read-only evidence; controlled test only with explicit approval.
4. Mind obtains merchant proof; **then** Dispatch may review the commercial placements and the founder may consider newsletter sending.
