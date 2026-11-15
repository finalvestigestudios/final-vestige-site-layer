# R374 · Subscriber-to-customer conversion acceptance (planning only)

**Owner boundary:** Dispatch #174 owns content/consent QA; Focus #129 and Claude own confirmation instrumentation; Mind #171 owns presell guide, merchant permission and commercial link eligibility; Grok and Praxxis retain creator acquisition and QA; founder retains all posting, spending, sending and release approval. Source of truth #820.

## Exact conversion sequence
1. A Grok post with a **verified actual asset ID** provides the reader a factual hook and approved link to a topical Final Vestige article. A channel-profile shared link cannot be attributed to the individual Short; `utm_content=youtube_channel_profile` is the honest fallback. No new Grok assignment or platform content is implied.
2. The relevant /focus/ or /dispatch/ consent form is displayed. A click, CSS state, PDF panel, or submitted email is **not** `confirmed_signup`.
3. Only a provider-authoritative email subscription state marked `Subscribed`, with deduplicated opaque subscriber key and confirmation evidence, may emit `confirmed_signup`. Never log raw addresses/confirmation links. Count only a genuine new confirmation transition; disallow unconfirmed, paused, bounced, unsubscribed recipients. Current total 3/confirmed 3/unconfirmed 2 may not conflict because pending confirmations can be outside totals; WordPress.com followers 3 and direct email 0 are separate counts. Provider-filtered eligible inbox count UNKNOWN.
4. The 52-page Fieldbook welcome is configured, but `welcome_delivered` and `pdf_retrieved` require separate first-party or consented read-only proof. Do not infer delivery from the welcome text or October 25 confirmation email.
5. Four editorial editions deliver primary-source usefulness; #06 R374 is an optional no-offer *retention* hypothesis to a published investigation, not another subscribe call. Two approved-for-drafting editions, #03 and #05, reserve optional merchant pre-sell guide CTAs with near-offer disclosure. No active earning links until named product-specific EMAIL permission and confirmed guide destination.
6. Propose only (do NOT deploy) `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_pilot_2026&utm_content=issue_03_zen12` or `issue_05_total_focus` on vetted internal guide links after approval. Preserve Claude's existing tracking; no duplicate pixels or scripts. Clicks are engagement, not revenue.
7. Independently settled affiliate/commerce records plus refunds and fees are necessary before a paid order or net revenue is counted. Join by merchant-sanctioned opaque referral key if possible. When unavailable, report attribution unknown.

## Acceptance / ROI
**KPI:** `1000 * independently_settled_net_revenue / audited_qualified_human_sessions` across 7- and 30-day cohorts, only when both sides and the settlement lag are known. No cohorts, verified eligible recipient counts, approved merchant links, actual sales or denominators exist in this sprint: NET REVENUE KPI **NOT COMPUTABLE**, not zero.

| Offer → step | Blocker | Proposed experiment or change | PASS evidence | Owner |
|---|---|---|---|---|
| Focus → confirmed lead | Client gift view can masquerade as consent | Provider-only `confirmed_signup`, dedupe | Unique subscribed record, opaque proof | Claude / Focus |
| Welcome → retention | No received Fieldbook proof | Read-only provider/inbox validation; later founder-authorized test only | Actual received welcome and accessible PDF | Focus / Founder |
| Zen12 → paid customer | Email promotion rights and guide not approved | Complete publisher/SKU/email grant then independent guide | Named grant, issued URL, live verified guide and merchant checkout | Mind / Commerce |
| Dispatch → inbox | No true postal / unsubscribe or native preview | Founder-authorized **non-sending** WordPress Preview email review | Native capture of publisher address & opt-out; functional verification when permitted | Dispatch / Founder |
| Grok asset → net revenue | Asset-level link and settled ledger not proven | Reuse existing Claude attribution; tie actual asset to sales | Qualified humans, independent settled orders, fees/refunds | Grok / Praxxis / Claude / Commerce |

No platform, list, sending, WordPress/analytics changes, external outreach, price quotes in email, affiliate activation, merge or spending authorized.
