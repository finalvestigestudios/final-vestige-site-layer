# Dispatch R208 — one-offer, source-attested conversion bridge (DRAFT / NEVER SEND)
Date: 2026-11-08 03:32–04:00 PT. Owner: FV Dispatch Campaign Studio.
Master campaign [draft #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at d57ccdba3aee8f065e143e101c2945f4f3d01647. Original 6 manuscripts and test suite unchanged. Readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201). Parent [R207 draft #1570](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1570) at 506739cffcba4b565d781921b32caec156594355. Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

### Why another isolated package?
The historical/editorial copy and twelve offline previews already exist. R208 does NOT duplicate or rewrite them. It adds (1) a merchant-specific subscriber-to-buyer friction finding, (2) a one-offer non-sending conversion sequence, (3) a deterministic source-attribution/confirmed-consent regression contract using SYNTHETIC data only, and (4) concrete owner acceptance tests and release blockers. R207's settlement guard remains the revenue authority; R208 does not claim that clicks equal money.

### Original source/execution checks
On THIS run the exact PR #175 head was re-read (still d57ccdba...), and all eight supplied master source blob SHAs matched current GitHub files exactly: six manuscripts, manifest, original test file. Native isolated Python unittest 6/6 PASS. Canonical editorial: 01/02/04/06; commercial-on-hold: 03/05. Original previews are in [R206 draft #1564](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1564), not new HTML produced here. Our isolated Node synthetic contract locally passed 28/28 before committing; see exact committed source/tests for reproducibility.

### Read-only production snapshot
WordPress.com connected read at 2026-11-08 11:34 UTC (03:34 PT): subscriptions enabled, site_can_send=true, auto-new-post OFF, full email body, from-name Final Vestige Studios, reply_to=no-reply, configured welcome with 52-page Focus PDF; counts total 3 / confirmed 3 / unconfirmed 2, suppressed 0 (NONADDITIVE); follower categories WP.com 3 and email-only 0. Actual provider email-eligible recipients UNKNOWN, not 0 and not 3. Five Nov-3 WordPress post entries were 'never_sent_opted_out', NOT successful newsletter sends. Actual provider-confirmed subscriber recipient aggregate, received final welcome, native preview and received test MIME, publisher postal address and functioning opt-out remain UNVERIFIED. No people or recipient email addresses included.

### Revenue consequence
The single provisional product for subscriber-to-customer planning is Zen12, not an endorsement. It cannot be emailed as an affiliate placement yet. The published seller page https://zen12.com/hnp exposes a merchant-owned *free audio* capture dialog that says the visitor will receive **the merchant newsletter**. This is a potential competing opt-in/attribution discontinuity if linked or followed: DO NOT represent such a signup as a Final Vestige confirmed lead, or as a purchased affiliate order. Actual funnel uptake was not measured. Mind Studio owns buyer-guide/live destination and partner email permission. Total Focus remains the second reserved commercial slot, not a second active offer. Current seller FAQ https://hypnosislive.com/faq limits refunds to five sessions per year under its advertised 14-day policy. No pricing/coupons/checkout or efficacy promises are copied into emails.

### Release classification
All six: HOLD_UNSENT, final founder campaign authorization absent. Commercial 03 and 05: additional HOLD_MERCHANT. Never publish, send test email, schedule, subscribe/import/export contacts, toggle Jetpack, install scripts, change WordPress, activate links or incur expenses. Never touch frozen homepage PR #49. No synthetic or static test can authorize a send. This branch is a non-sending research/QA proposal, not production deployable.

### Files
- R208_OFFER_FUNNEL_AND_CHANNEL_LEAKAGE.md — exact seller-page comparison, friction, ethical copy and action.
- R208_NON_SENDING_SEQUENCE.md — six-stage editorial-to-offer journey and source-matched CTA destinations, not new blasts.
- R208_EVIDENCE_AND_OWNER_GATES.md — evidence checklist and owner-specific release tests.
- attribution_contract.cjs / test_attribution_contract.cjs — offline deterministic privacy/attribution guard with invented fixture IDs ONLY.

All unsent, no user contact, no revenue claims.