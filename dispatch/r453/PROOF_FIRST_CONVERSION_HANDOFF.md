# Dispatch R453 — Proof-first subscriber-to-settled-customer acceptance

**Status:** SOURCE ONLY · HARD HOLD · no email, test email, post, list import, affiliate activation, sending schedule, platform change or spend authorized. Owner [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Base [R452 #3026](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3026) at `52c3f79bf4f775e977c3e32ebe6e00bd2075bd4a`. Master six #175, independent release gate #201 and frozen homepage #49 unchanged.

## The actual business hypothesis

A motivated person who arrived from a Grok evidence-based perception/history video can become a real long-term buyer *if* the free Fieldbook is useful, the reader explicitly consents to continuing email, the Dispatch stays consistent with the archive identity, and one relevant independently scrutinized offer is presented only after account-specific partner authorization. Do not pursue a 12-minute-meditation promise or a discount timer as the hook: those are not product-specific scientific evidence or verified favorable commercial terms.

**One high-intent intended offer:** Zen12 only, held in Issue 03. Issue 05 separately reserves Hypnosis Live, but is **not** a second product in this particular first-offer journey. Issue 01/02 provide archival relevance, Issue 03 provides concrete free value before the hypothetical paid guide, Issue 04/06 preserve evidence-first editorial. Weekly six-issue **draft** only; no added autoresponder or actual segmentation capability assumed.

## Read-only first-party observations — 2026-11-18 18:34–18:35 UTC

| Provider surface | Returned | Allowed inference | Disallowed inference |
|---|---|---|---|
| `wpcom_jetpack_newsletter(status)` | total 3, confirmed 3, unconfirmed 2, suppressed 0, paid 0, imported last 24h 0 | Diagnostic provider buckets, separately reported | Five unique readers; three new external leads; three received emails |
| `wpcom_jetpack_stats_subscribers(email_subscriber)` | total 3 | Source-specific classified email records | Verified independent audience or delivered message |
| `wpcom_jetpack_stats_subscribers(reader_subscriber)` | total 0 | Source-specific Reader-only list count | Real Reader count is zero |
| `wpcom_jetpack_stats_subscribers(unconfirmed_subscriber)` | total 2 | Two listed unconfirmed, excluded from confirmed audience | Subscribed audience can be increased by two |
| `wpcom_jetpack_stats_followers` | email 0, WordPress Reader 3, total 3, partial=false | Second source classifies 3 differently | 0 actual email recipients or 3 distinct Reader-only humans |
| Newsletter `get_settings` | enabled true, auto-post email false, full format, from Final Vestige Studios, reply_to=no-reply | No default dispatch on new post | A received native email preview, mailbox deliverability or footer compliance |
| `wpcom_jetpack_stats_emails` | zero post email rows | No recorded post-email performance in response | "Zero successful signup" or "zero sales" |
| Newsletter status latest five | `never_sent_opted_out` | No post email emitted for those posts | Welcomes never delivered |

The welcome message *contains* the real 52-page Fieldbook URL. That establishes **configuration, not actual recipient receipt**. A connected Gmail subscription confirmation dated 2026-10-25 is a confirmation request, not a received welcome. No recipient identifiers or email addresses belong in GitHub.

This double-axis conflict is a **vendor-data interpretation issue**. Escalate privately through WordPress.com/Jetpack support with source names, UTC sampling time, and redacted aggregate results; ask whether Stats Subscribers vs Stats Followers count the same populations/cache and whether confirmation eligibility should be governed by Newsletter vs following mode. Do not change settings as a diagnostic experiment and do not expose private subscribers.

## Source-of-truth progression (no new collection)

1. **Acquisition (Grok owner):** Keep the actual approved platform asset ID + platform + published URL + exact onsite CTA path. Canonical link contract: `utm_source=youtube|tiktok|instagram|facebook|pinterest|x|bluesky`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<unique non-PII asset_id>`. TikTok profile links may prevent direct asset attribution; report that loss instead of attributing source by proximity.
2. **Landing (Claude owner):** An actual qualified *human* session at /focus/ or a source article is not the same as a Jetpack pageview. Use an existing analytics implementation if approved; do not install a second tracking stack. Respect user consent and privacy.
3. **Consent (Focus owner):** A `confirmed_signup` exists only after a **new**, actual Jetpack/provider unconfirmed→confirmed email transition under sufficient consent and legitimate evidence. Deduplicate repeated attempts; Reader follows, downloaded PDFs and already-confirmed publisher/test accounts are not new acquisition. Do not log email, IP, consent-token or subscriber ID into GitHub.
4. **Welcome (Focus/Claude):** Check configured message and PDF URL separately from *actual received delivery* by a **founder-authorized**, privacy-safe recipient test. Do not create a new address or send a test now.
5. **Nurture (Dispatch):** Optional weekly editorial issue 01 → 02, then **held** Issue 03, if and only if per-edition founder content choice, real list permission, legal mail footer, Jetpack's genuine native preview and email-channel merchant approval are witnessed. Native topical segmentation is **unproven**; do not invent behavior-triggered blasts.
6. **Offer (Mind/Commerce):** A real, vetted **published first-party Zen12 buyer guide**, identifiable actual version, and merchant-issued earning URL with named affiliate account + authorization to promote via **email**. The second click to the merchant is an *affiliate outbound*, never a paid conversion.
7. **Paid settlement (Commerce/Claude):** Independent merchant/payments evidence of a settled transaction or settled commission, with fees, refund/chargeback, currency and source linkage. Until verified, `verified_paid_orders`, `net_revenue`, and revenue-per-1000 **are NULL/UNKNOWN**, not zero.
8. **Governance:** Home page priority #150, frozen PR #49; Grok TASK-008 and its Drive handoff stay Grok/Praxxis owned. No overlapping PR merges or publishing.

## Executable proof logic, local only

- [`conversion_proof.mjs`](conversion_proof.mjs) compares three inconsistent provider feeds without conflating populations; rejects non-confirmations and non-source-tagged social events; deduplicates identical settled orders; rejects contradictory duplicate receipts and invalid refunds; returns `UNCOMPUTABLE` when audited session denominators or complete settlement proof are absent.
- [`cohort_math.mjs`](cohort_math.mjs) is a *closed* 7- or 30-day **acquisition cohort** evaluator using opaque qualified-session IDs and independent paid-order settlement evidence. A September cohort cannot be evaluated until its whole follow-up horizon matures; source attribution must have its own proof. It is NOT site instrumentation or a CRM and reads no network/account.
- Tests contain **synthetic** sessions and orders, not genuine FV customer activity. Their example positive net values must never be copied into a KPI report. An order click, provider confirm count, Stripe link, affiliate outbound, email open or discount-page claim does not constitute paid settlement.
- A provenance string is a **required attestation input**, not proof this program cryptographically authenticated a remote vendor. The source must still be independently checked by the owner. This distinction is essential; do not interpret `verified: true` alone as sufficient.
- The R453 model is **not send automation**: no email send function, no network, no data export, no WordPress API client, no merchant checkout action. This code is a review contract for owners and engineering, not production authorization.

## Required OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Offer and step | Primary blocker | Safe next change / experiment (no live activation) | Objective pass condition | Owner |
|---|---|---|---|---|
| Zen12 / warm buyer | No named email affiliate rights, issued URL, live approved guide, exact SKU or current checkout | Product-specific seller email-channel eligibility dossier; vetted guide handoff; avoid different `/secret/` offer being silently substituted | **FAIL/HOLD** until merchant/account proof + guide URL + product/checkout checks | Mind/Commerce |
| Fieldbook / confirmed lead | Three-feed classification conflict and no received welcome | Private Jetpack support reconciliation + specifically authorized inbox witness | **FAIL/HOLD** for delivered welcome and new externally confirmed lead | Focus/Claude |
| Dispatch / lawful inbox | No native Jetpack-rendered email with valid **FV** postal and working unsubscribe | Founder uses WordPress editor Preview **without send**, records screenshot/readback; legal footer witness | **FAIL/HOLD** until genuine render witnessed; offline HTML is insufficient | Dispatch/Founder |
| Grok asset / qualified human session | Asset→website attribution and bot quality unproven | Claude privacy-safe existing analytics audit tied to TASK-008 asset IDs | **FAIL/HOLD** for audited denominator | Grok/Praxxis/Claude |
| Buyer / realized revenue | No independently settled commissions/orders, fees and refunds | Integrate authorized read-only commerce ledger; run 7/30-day *mature closed* cohort acceptance | **FAIL/HOLD** for net-revenue KPI until source-backed settlement | Commerce/Claude |

## Founder decisions still required

1. Select one of each original/alternative six manuscripts in [#2995](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2995) or [#3000](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3000); no selections inferred.
2. Provide or approve Final Vestige's **own valid commercial postal address** and legal identity for email headers; never use the vendor's or Automattic's address.
3. Approve **a specifically scoped non-sending native preview inspection** or later separately authorize a received test (not granted here); there is no actual preview/received welcome proof at present.
4. Resolve named Inspire3 partner permission, per-product EMAIL conditions, payout/link format and product-specific terms through the accountable owner.
5. **Final separate campaign send approval** required for each send/audience/timing; six draft approvals are **not** sending consent.

**As of this dossier:** all six `HOLD_UNSENT`; no proven commercial sale, external lead, or subscriber-to-buyer result. Net revenue/1,000 qualified humans is NOT COMPUTABLE. Do not claim A/B results with this list.
