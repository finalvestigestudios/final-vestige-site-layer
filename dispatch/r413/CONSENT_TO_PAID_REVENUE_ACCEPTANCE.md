# Dispatch R413 — one-offer consent-to-customer release contract (SOURCE ONLY)

Owner: Dispatch / Focus QA; source-of-truth [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); commercial claims/guide ownership [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Six canonical issues from draft [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) remain unchanged. R413 Issue03 is optional, NOT_ADOPTED. No live workflow, send, subscription import, email-trigger implementation or duplicate analytics.

## One high-intent audience and ONE hypothetical purchase route

Audience hypothesis: an existing organically acquired reader of FV history-of-attention or first-person focus notes who **chooses** to confirm the existing Jetpack Dispatch newsletter and wants to evaluate paid guided-audio options. This does not establish current segmentation ability or member permission for commercial promotion. The only prospective paid product in this R413 progression is **Zen12**, not Total Focus; Issue05 reserves a separate commercial slot in the founder's original six-issue plan and stays on hold. A reader can access an independent buyer guide directly without being forced to give an email address.

Proposed, NOT live: Grok video with immutable creator asset ID (Grok controls) → relevant FV first-party investigation or /focus/ (Claude controls) → voluntary opt-in using the existing Jetpack list → WordPress provider-authenticated confirmation and actual email eligibility → verified receipt of the 52-page welcome Fieldbook → evidence-first editorial nurture → optional R413 Issue03 buyer-guide CTA, **after its first-party guide is approved LIVE** (Mind owns) → verified authorized earn-out link only if product-specific EMAIL permission exists → referred checkout → independent paid settlement and post-refund/fee reconciliation (commerce owner). The sequence is an ordered hypothesis; Jetpack automation or subscriber-level segmentation has **not** been established. No current event causes an automatic email.

## Single, deduplicated confirmed_signup contract (not yet implemented)

Canonical proposed event name: `confirmed_signup`. Trigger **once** from authenticated WordPress/Jetpack server confirmation, AND proof the identity is currently eligible for email, NOT from a browser `?subscribe=` parameter, local success panel, generic WordPress.com reader follow, Fieldbook click, or aggregate dashboard count. Suppressed, bounced, paused, not-confirmed or opted-out identities cannot qualify. Handle retries using a stable provider enrollment/event ID in a private idempotency store. Store first qualified confirmation timestamp and status; an unsubscribe must stop all further sends; re-confirmation requires provider-authoritative permission and a new explicit eligibility review. Do not expose an address, raw subscriber ID, hashed email, or linkable pseudonymous ID in analytics, GitHub or public logs. Have Claude validate exactly where/how a secure server-side dedup can occur in the existing stack before implementing anything.

WordPress's reported 2026-11-17 UTC snapshot is total=3, confirmed=3, unconfirmed=2, suppressed=0. A separate followers API reports WordPress.com=3 and direct email=0. These categories overlap or represent distinct concepts; neither report establishes the unique deliverable inboxes. `confirmed_signup` count for a cohort is **UNKNOWN**, not 3, not 0, and not 5, until private row-level eligibility+dedup is checked through an authorized provider surface. Avoid subscriber exports or exposing identities in issue comments.

## Attribution contract, no new script

Grok TASK-008: `utm_source=(youtube|tiktok|instagram|facebook|pinterest|x|bluesky)`, `utm_medium=organic_social`, `utm_campaign=<topic_cluster>_pilot_2026_11`, `utm_content=<immutable_asset_id>`. Use only platforms actually active, and never invent an asset ID. This is the creator-to-site dimension, not evidence of a human session or confirmed signup.

Proposed **email-to-site** guide tag only *after approvals*: `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue03_zen12`. The email destination must be an approved live **first-party guide**, never a price-sensitive vendor link. Preserve creator-to-first-party acquisition attribution in existing consented server/analytics records where possible, without injecting personally identifying UTM strings. Claude owns implementation and deduplication within the existing stack. UTM visits/clicks can indicate interest but are **not revenue**. Jetpack subscriber identity must not be joined to behavioral data without a lawful, documented purpose and subscriber privacy safeguards.

## Evidence ladder and revenue denominator

1. Qualified-human session: independently filtered/observed first-party session tied to a legitimate Grok asset `utm_content` when available (bot/replay/no-consent and misattributed traffic separately reported; never guess).
2. Relevant first-party CTA click: optional intent marker, not evidence of opt-in or paid intent.
3. Provider-confirmed eligible newsletter signup: deduped private Jetpack record, not the Focus download display or public URL.
4. Email guide click: anonymous or aggregated event where permitted, NOT an independently verified purchase.
5. Approved commercial outbound click: after owner-approved live guide and verified earning link; still not a purchase.
6. Independently reported paid order: merchant settlement or FV sales ledger, matched to permitted campaign tracking with de-identified joins and timestamp.
7. Net realized revenue: gross paid commissions/sales minus settled refunds, reversals, charges and attributable fees; never compute from clicks or estimated EPC.

Report seven- and thirty-day cohorts by actual event timestamps. Key KPI `1000 * net_realized_revenue / audited_qualified_human_sessions` **only if both independently verified inputs and valid matched windows exist**; otherwise `NOT_COMPUTABLE`, not zero. List confirmed orders/customers, paid conversion rate and lead-to-paid rate only with independently verified denominators. At the current tiny list size there is no valid statistical A/B lift claim; use descriptive QA, not significance tests.

## Explicit exclusions and owner handoffs

* **Founder**: authenticated postal mailing address and campaign release approval; no founder approval inferred from draft acceptance.
* **Dispatch**: truthfully labeled original copy, accurate subject, one primary CTA, commission disclosure adjacent to the offer, placeholder-free HTML/plaintext, genuine Jetpack Preview and witnessed unsubscribe/headers; no sending until independent approval.
* **Mind / Commerce**: Zen12 SKU terms, precise affiliate agreement, named FV acceptance, email permission, issued earning URL, pre-sell guide publicly LIVE after separate approval, checkout/refund and settlement. Public seller swipe copy is not private authorization.
* **Focus / Claude**: consent, email-recipient eligibility, welcome/Fieldbook receipt and privacy-safe event dedup in **existing** infrastructure. Focus browser state alone cannot count a subscription.
* **Grok / Praxxis**: existing TASK-008 creator distribution/asset IDs, no changes to their content queue.

All operational releases remain `HOLD_UNSENT`; this file authorizes NO sending, publication, tracking script, price statement, affiliate activation, or settings change.
