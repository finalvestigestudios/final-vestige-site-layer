# Dispatch R343 — offer → funnel step → blocker → evidence → owner

**Priority is net realized revenue from real customers, not email volume or clicks.** This file is a read-only implementation handoff and evaluation contract, not authorization to deploy tracking, send mail or change a page.

| Offer / audience | Funnel step | Blocking truth | Proposed change or non-sending experiment | Acceptance evidence | Owner |
|---|---|---|---|---|---|
| Zen12 Premium / subscribers who engaged with evidence-based attention | Email #03 → approved first-party buyer guide | FV partner acceptance, explicit **EMAIL** promotional rights, authorized tracking destination and guide live state NOT VERIFIED | Compare accurate text-only guide CTA with no-offer fallback, after permissions | Partner account proof privately inspected, approved live guide, current seller terms, independently tracked settled commission | Mind & Affiliate / Commerce, Founder |
| Total Focus / hypnosis history & careful buyers | Email #05 → product-specific guide | Product claim proof, individual refund conditions, permitted email channel and live guide NOT VERIFIED | Preview a Total Focus-specific evaluation with free practice instead of catalog-level pitch | Merchant document, permitted creative/link format, guide exact URL, current refund policy, settled earnings if any | Mind & Affiliate / Commerce |
| Free Fieldbook / qualified social visitor | Grok asset → /focus/ → signup | Unconfirmed signup vs free PDF download indistinguishable in existing aggregate | Verify existing platform's confirmation lifecycle in privacy-safe read-only mode; never create new list | Provider-authoritative consent evidence for exactly ONE `confirmed_signup` keyed by a private opaque subscriber identity, no PII in issue | Claude / Focus |
| Fieldbook welcome / valid newly confirmed subscriber | Confirmation → welcome → usable PDF | Welcome configured, real delivery and working download inside received email NOT VERIFIED | Authorized owner-only read of an existing delivered welcome; no new test emails | Timestamped redacted real MIME/screenshot showing delivery and working link; sender, opt-out policy checked | Focus / Founder |
| The Dispatch / consented established reader | Original 01-06 → own web content | Recipient count unknown; legal address, native preheader, functional unsubscribe, actual inbox HTML unknown | Use native **Preview email** without Send test; only with explicitly authorized controlled non-sending view | Device screenshots, correct subject, actual publisher postal, native opt-out verification in authenticated inbox after authorization; owner approval | Dispatch / Founder |
| Grok → first-party content → transaction | Attributed qualified session → checkout → settled order | Actual asset IDs, qualified human sessions, fees/refunds/orders not supplied | QA existing UTM path, `utm_source`, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<Grok_asset_id>` | Source-qualified session and independently settled sales ledger with refunds and processor fees | Grok / Praxxis / Claude / Commerce |
| FV rights-cleared own digital products | Editorial content → existing commerce | Approved sellable offer + actual order/refund reconciliation not furnished to Dispatch | If Commerce verifies one rights-cleared higher-intent FV product before Inspire3 approval, compare offer relevance without swapping original commercial slots or issuing an email | Catalog rights, live checkout, receipt/settlement ledger, explicit founder scope | Commerce / Founder, not Dispatch |

## Single-offer progression (hypothesis, not live)

1. Visitor encounters Grok's cited perception/history content; unique immutable `asset_id` routes to a context-matching first-party page, never a generic shop link. Grok owns creation, Claude owns instrumentation.
2. A visitor downloads the free Fieldbook or confirms Dispatch subscription. **Download ≠ subscriber**. Existing WordPress.com previously verified path can be a legitimate confirmation without new challenge; the provider is source of truth.
3. A genuinely consented Dispatch reader receives four deep editorial letters and, subject to **separate merchant permission**, two optional buyer-evaluation letters. Commercial disclosure in same issue and adjacent to qualifying recommendation. No multiple-offer blast.
4. Offer page demonstrates exactly what is sold, buyer objections, evidence limits, price if fresh, refund conditions, and a clear optional choice; no promises of clinical success, fabricated urgency, fake scarcity or unverified testimonials.
5. Only merchant-confirmed settled paid transactions/earned affiliate payout, less refunds, fees and reversals, count as commercial conversions. A click is an experiment observation, never revenue.

**Measurement:** Use 7-day and 30-day cohort periods. `qualified_human_sessions` must be provider/authenticated analytic evidence deduplicated by source asset; `confirmed_signup` is counted once per provider-authoritative qualified subscriber. `net_revenue_per_1000_qualified_sessions = (settled_revenue - refunds - platform/payment_fees) / qualified_human_sessions * 1000` only when both numerator and denominator are complete and credible. **Current value is NULL/NOT COMPUTABLE**, not zero. No A/B statistics on a ~3-person aggregate. Do not collect subscriber emails/tokens in GitHub.

## Cross-team boundary

- [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174): Dispatch final editorial and consent/release gate.
- [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171): Mind/Commerce authorizations and independent guides; **do not** activate their links.
- [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129): Focus signup and genuine delivered welcome.
- [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820): Claude analytics, qualified visits and independently verified revenue.
- Grok/Praxxis use [TASK-008 Drive coordination](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit); never change task queue, publish or spend.
- Founder owns campaign and spend/release. Homepage #150/frozen PR #49 untouched.
