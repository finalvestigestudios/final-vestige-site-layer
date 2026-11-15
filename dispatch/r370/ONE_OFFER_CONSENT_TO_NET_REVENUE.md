# R370 — Consent to customer, one verified-offer journey

Draft-only: Grok controls video and social posting; Praxxis handles actual asset-id coordination in the existing [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit). Claude owns core analytics/website changes, Mind/Commerce owns approved offer + source-grounded buyer guide, Dispatch owns its single existing Jetpack consent/newsletter lane, founder approves all sending/commerce/release.

## Proposed funnel with real evidence gates

1. Verified live Grok asset with unique real asset_id and truthful hook → matching historical investigation (not merely pageviews).
2. Interested visitor → existing [Focus](https://finalvestige.com/focus/) Fieldbook. Download click is not consent or delivery.
3. Same existing Jetpack list. Define one **confirmed_signup** event only on distinct provider-authoritative transition to **Email Subscription = Subscribed**, deduplicated over repeated attempts. Exclude Reader-only, bounced, paused, suppressed, and unconfirmed. No raw subscriber address in any shared report.
4. Actual post-confirmation welcome and complete 52-page PDF receipt, verified through authorized inbox and successful guest download; configured welcome alone is insufficient.
5. Evidence-led editorial nurture; optional Issue 03 Zen12 guide only for relevant, appropriately consented readers and only if an independent guide, publisher-specific EMAIL rights and founder release approval exist. No blanket affiliate blast.
6. Approved warm-up guide → authorized earning URL and merchant referred checkout → **independently settled** paid commission, less refunds/reversals/fees.

Proposed email attribution after authorization: utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_mind_pilot_2026, utm_content=issue03_zen12_guide. Reuse Claude-owned existing measurement; preserve Grok asset_id where privacy-safe first-party context permits. No duplicate scripts and no false cross-device attribution.

**Core metric:** 1000 × (verified settled direct-sale receipts + settled affiliate commissions − refunds − reversals − fees) ÷ verified qualified human sessions, for 7/30-day cohorts. Both numerator and denominator require independently validated sources; if unavailable, report **NOT COMPUTABLE**, never invented zero or A/B uplift. Opens, clicks, signup attempts and cart views are NOT sales.

As of 2026-11-15 04:31 UTC the authenticated Jetpack status was total 3, confirmed 3, unconfirmed 2; [WordPress documentation](https://wordpress.com/support/subscribers/) says unconfirmed is not counted in total. Categories cannot be added to infer five. WordPress.com followers 3/direct-email 0 similarly do not establish inbox eligible count. An aggregate filtered to Email Subscription=Subscribed remains required.

## Offer → step → blocker → change → PASS evidence → owner

| Offer / step | Blocker | Change or experiment | PASS proof | Owner |
|---|---|---|---|---|
| Zen12 guide → buyer | No named email rights, issued link or live buyer guide | SKU-specific claims and independent guide; no release yet | Merchant named approval, approved link, real referred checkout and settled payout | Mind/Commerce/Founder |
| Focus → unique lead | Provider status unknown | Filter provider to Subscribed and deduplicate | Timestamped privacy-safe aggregate without recipient addresses | Claude/Focus |
| Fieldbook → reader | Configured welcome not delivered proof | Authorized receipt, guest PDF 52-page read test | Genuine post-confirmation welcome/PDF delivered | Focus/Founder |
| Dispatch → compliant inbox | No native preview, FV physical mailing address or functional unsub | Verify without sending where possible, later explicit founder-approved controlled test | Exact rendered valid publisher postal/footer/opt-out proof | Dispatch/Founder |
| Grok → paid buyer | Source events and settlement not joined | 7/30-day qualified human-to-settlement reconciliation | Verified real asset ID, settled receipts, fees and refunds | Grok/Praxxis/Claude/Commerce |

No send, test message, subscribers contacted/exported, WordPress writes, merchant outreach, deployed analytics, new list, PR merge or expense.
