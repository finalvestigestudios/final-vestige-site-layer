# Dispatch R433 — evidence-to-customer acceptance (unsent, review only)
Date: 2026-11-17 PT. Source baseline: master [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), exact `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Stacked on [R432 #2917](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2917), exact `2f500125dcbf96b94507783a8fa8788254f29049`; preserves [R430 #2906](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2906), [R431 #2911](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2911), readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) and founder [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174).

## Decision: HOLD_UNSENT; no staged changes are permission to send
This branch introduces an **aggregate, consent-sensitive and purchaser-sensitive offline witness**, a synthetic confirmation-to-settlement checker, a separate inspector page and merchant-specific, legally conservative founder acceptance instructions. It creates no subscriber/list entity, WordPress post, preview email, merchant destination, attribution script, pixel, tracking cookie or live analytics event.

## Newly authenticated, narrowly scoped findings
- Connected Jetpack at 2026-11-17 22:39 UTC: Newsletter enabled; can-send capability true; emails for newly published posts default OFF. Full-post mode, featured image ON, **reply_to=no-reply**, sender display **Final Vestige Studios** and no newsletter categories. These facts DO NOT prove an eligible inbox or permission for a campaign. Most recent five post records explicitly `never_sent_opted_out`; this is **not** proof of zero lifetime sends.
- Dashboard totals **3 total / 3 confirmed / 2 not confirmed**, suppressed 0. WordPress explicitly *excludes* not-confirmed entries from total; these numbers are not an arithmetic contradiction. Separate Reader3/direct-email0 stats are not authoritative for eligible recipient count. `Email subscription=Subscribed` aggregate, without addresses, is still needed.
- Jetpack welcome text is configured and contains the free 52-page Fieldbook PDF URL, but received delivery has not been proven. Read-only connected Gmail search found **one** 2026-10-25 WordPress *confirmation* message (no Fieldbook/welcome) and found **no** message with exact phrase "Welcome to The Dispatch" or "Seven Day Focus Fieldbook" in that searched mailbox/time window. It cannot speak for other subscribers' inboxes. A WordPress sender confirmation contains an Automattic postal address; that address does **not** establish Final Vestige's lawful commercial postal footer.
- Live /dispatch/ and /focus/ returned HTTP 200 and an indexable canonical in authenticated read-only rendered-page checks. Their public copy still suggests delivery when posts are published; default sending remains OFF. /dispatch/ holds page ID 523; /focus/ holds 1579. Both pages are unchanged here.
- Existing Gutenberg specimens in R429 start with **EDITORIAL HOLD** content and lack a witnessed native Preview. Do not paste those unchanged into a live email: the warning risks being the first rendered content. R431 documents this. Source preheaders remain *editorial metadata*, not verified Jetpack inbox snippet text.
- No active interest-specific Jetpack segment or approved automated drip exists. Confirmed signup is a **provider-authoritative transition**, not a form submit or the existence of a Reader follower.

## Founder one-offer, one-audience path
High-intent candidate: **a reader of a source-grounded attention investigation** → free Focus Fieldbook → a provider-confirmed subscriber (only if consented) → one relevant, optional Zen12 *independent guide*, eventually an authenticated affiliate checkout → independently reported settled sale minus fees/refunds. It is NOT an existing automation, offer, SKU or verified revenue channel. If any commercial right is missing, remain editorial with a free first-party CTA; do not substitute a seller URL or quietly send a promotional broadcast.

## Six-issue release ledger
| Issue | Allocation | Concrete action | Current release decision |
|---|---|---|---|
| 01 | Editorial | Founder selects original Puységur destination or R427 research-grounded Change Blindness candidate; verify destination and title | HOLD: selection, footer, audience, preview |
| 02 | Editorial | Founder selects historical Puységur manuscript or R427 Franklin/Mesmer candidate | HOLD: selection, footer, audience, preview |
| 03 | Commercial reserve | Zen12 **exact merchant EMAIL rights** + current seller product/claims + Mind-approved LIVE independent guide, issued earning URL and exact checkout | HOLD_MERCHANT; no link |
| 04 | Editorial | Replace unsupported "fourteen seconds" subject through R426 Apollo source adjudication before approval | HOLD_COPY |
| 05 | Commercial reserve | Hypnosis Live **Total Focus** exact SKU, 33-minute MP3 vs bundle, refund policy, EMAIL rights, actual live guide/earning URL | HOLD_MERCHANT; no link |
| 06 | Editorial | Founder selects canonical /focus/ CTA or R426 direct Fieldbook PDF candidate; no duplicate lead claim | HOLD: selection, footer, preview |
No edition may launch solely because other editions pass. Preserve four editorial/two commercial slots; alternatives do not silently replace the original campaign.

## Source-of-truth / independent owners
- Dispatch [#174]: editor, subject/first-paint QA, source-conservative emails, consent-to-revenue rules.
- Mind & Affiliate [#171]: presell pages, creative rights, authorized merchant offers; recent independent [#2919](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2919) still says named EMAIL rights and issued link unknown.
- Focus [#129] and Claude: provider recipient filter, signup dedup, welcome receipt and production analytics implementation. Do not install duplicate scripts.
- Creator growth [#820], [#818], existing Grok/Praxxis [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit): original asset IDs and authorized platform click destinations, not Dispatch-generated posts.
- Founder: explicitly approves final copy, mailing address and actual campaign release only after written evidence.

## Precise revenue boundary
Measure verified settled purchases/commissions and net revenue, not previews, opens, clicks, "confirmed=3", bot visits or checkout starts. 7- and 30-day cohorts require agreed provider/merchant join and human-session evidence; where unavailable, denominator/attribution are UNKNOWN and **net revenue per 1,000 qualified-human sessions = NOT_COMPUTABLE**, not 0.
