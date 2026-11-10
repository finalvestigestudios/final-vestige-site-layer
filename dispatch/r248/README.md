# Dispatch R248 | Apollo source timebase and subscriber-to-customer evidence gate | UNSENT

**Canonical:** six untouched drafts in [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), Issue #174; four editorial / two merchant-review. **Parent:** [R247 PR #1837](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1837). Readiness [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) and frozen homepage [PR #49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) unaffected. Nothing in this folder is approved for publishing or email.

## What is new, not a repeat of prior draft options

1. **Apollo 1 historical timebase:** an original alternate editorial edition 04, HTML reviewer view and matching plaintext explicitly distinguish first crew fire report at **23:31:04.7 GMT** from **approximate vessel rupture at 23:31:19**. The ~14-second span is report-to-rupture, NOT duration of fire, time of ignition, or time to death. NASA's board places last communication start at 23:31:16.8 and loss of telemetry at 23:31:22.4; later timestamps are less precise, exact source of ignition unconfirmed. This prevents an unsupported 'fourteen seconds' or competing 'seventeen seconds' headline from silently changing the historical claim. Primary original source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . Underlying report: https://ntrs.nasa.gov/citations/19930078717 . Original Issue 04 remains authoritative and unchanged pending founder review.
2. **Verified provider opt-in contract, not inferred newsletter audience:** `consent_attribution_gate.cjs` intentionally returns NULL for the real email-eligible count. Jetpack total=3/confirmed=3/unconfirmed_requests=2 are overlapping/non-additive counters; followers API email-only=0/wpcom=3 is a different partition. None proves actual email eligibility or received welcome. The provider's *Email subscription: Subscribed* status and independently authenticated transition is the only eligible proof, with replay protection. Test fixture transition IDs are wholly synthetic, and actual individual addresses are not accessed.
3. **Paid revenue is NOT asserted by an offline JSON fixture:** the gate checks chronology from qualified Grok asset, site visit, CTA, attributable outbound merchant click, independently settled purchase, fees/refunds and USD. Even an all-true local record is not an authenticated provider report; the tool deliberately returns NULL net revenue and refuses to release. Source-specific spend, price and commission are NOT invented.
4. **Documented offer path:** Grok already-published original asset → relevant published evidence page /focus/ → one existing Jetpack opt-in and configured 52-page Fieldbook → 4 useful editorial issue slots + 2 reserved commercial review slots → optional, founder-approved live Zen12 buyer guide → approved merchant earning URL → independent settled paid order. Mind & Affiliate #171 owns guide and partner rights, Grok owns creator production, Claude owns site/analytics implementation; Dispatch only supplies unsent editorial and event QA.

## Live source-of-truth snapshot (read-only, 2026-11-10 04:37 UTC)

- WordPress site ID **256784396**; newsletter enabled, post auto-send OFF; full-content emails, from name *Final Vestige Studios*, no-reply. Welcome configured with the existing 52-page PDF. **Configured ≠ delivered**. Five recent posts show `never_sent_opted_out`.
- Jetpack counters total **3**, confirmed **3**, unconfirmed requests **2**, suppressed **0**; followers stats partial=false, WP.com **3**, email-only **0**. Recipient deliverability/eligibility UNKNOWN, do not add these figures.
- /dispatch/ page **523** emphasizes historical investigations and a welcome gift; /focus/ page **1579** also discloses possible commission-earning recommendations. A harmonized disclosure sentence is proposed, not published.
- Published Editorial Standards page **17** requires documented primary sources, visible uncertainty, dated corrections for consequential changes and separation of commercial interests from conclusions.
- Seller pages https://zen12.com/hnp and https://zen12.com/secret/ advertise different prices, not verified as equivalent checkouts or eligible affiliate offers; https://hypnosislive.com/mental-skills/total-focus and https://hypnosislive.com/faq show seller terms/claims only. **No named Final Vestige approval, email promotion permission, or issued earning link established.**
- NASA exact review record supports Apollo chronology but is not evidence that a PDF in a private PR has ever been rendered by Jetpack.

## Critical WordPress rendering/documentation mismatch

Do not treat a static HTML file as the actual delivered email. WordPress's public https://wordpress.com/support/newsletter/email-appearance/ guide, fetched during this review, instructs enabling the **per-post send** toggle before native preview; an earlier campaign snapshot described a different Nov 9 preview procedure. Treat the operational toggle requirement as **UNRESOLVED**, not permission to enable it. No WP draft, per-post toggle change, native preview or test send was performed. Its email subject is the WordPress post title; our proposed preheader is NOT proved to survive Jetpack's renderer. Business mailing address and rendered unsubscribe remain pending. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Funnel and segmentation hypothesis (NOT implemented)

- **Discovery:** human-aligned source/asset ID → one relevant article. No fake creator ID and no duplicate tracking scripts.
- **Lead capture:** one existing Focus/Dispatch Jetpack form; count `confirmed_signup` only from a provider-confirmed transition, distinct provider transition key, not from an attempted email entry, Reader follow, or PDF download. Do not store subscriber emails in analytics.
- **Nurture:** first two editorial letters prioritize researched usefulness. Evidence of *reader-chosen* interest in evaluating meditation audio could justify a **voluntary** separate Zen12 guide CTA within reserved commercial Issue 03 *after merchant/consent approval*. Do not silently retarget every subscriber, import names, or build unapproved behavioral profiles.
- **Purchase:** guide → exact merchant-authorized link → independent paid conversion; measure 7/30-day cohorts with qualified human session denominator. Revenue / 1,000 qualifying sessions = 1000 × (settled gross commission less refunded/reversed amounts and fees) / qualified sessions, **only after both evidence sets are authenticated**. Unknown denominator/settlement => NULL, not $0 or an invented estimate.
- **Issue 05:** Hypnosis Live separately held; Issue 04/06 preserve historical evidence and direct existing Fieldbook without asking subscribers to resubscribe.

## OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Offer / step | Blocker | Required next proof or safe experiment | Evidence now | Owner |
|---|---|---|---|---|
| Zen12 → buyer | Named email partner rights, earning URL, exact eligible checkout/refund, approved LIVE guide missing | Authenticate partner records and authorized guide first | FAIL / HOLD_MERCHANT | Mind & Affiliate #171 |
| Grok → landing | Published asset_id and qualified-human attribution unresolved in TASK-008 | Reconcile existing asset IDs, intent and actual human sessions, no new script | NOT VERIFIED | Grok / Praxxis / Claude |
| Focus → confirmed lead | Confirmed counter ≠ eligible recipient and welcome receipt unknown | Privately check aggregate provider 'Email subscription: Subscribed', opt-in transition, welcome receipt; no PII export | UNKNOWN | Focus #129 / Claude |
| Dispatch → inbox | Preheader, native render, publisher postal address and working unsub unverified | Resolve preview toggle safely, then obtain explicit separate founder approval for any test email | NOT TESTED | Dispatch / Site QA |
| Apollo editorial → evidence reading | Subject timebase conflates phases | Optional R248 source-led revision for founder review; one existing article CTA | SOURCE TESTED, NOT ADOPTED | Dispatch |
| Buyer → net commission | No authenticated settled sale/fee/refund proof | Provider order reconciliation, 7/30 day cohorts, true net per 1,000 | NOT COMPUTABLE | Commerce / Praxxis #820 |

## Executable offline QA

`node --test dispatch/r248/tests/*.test.cjs`. Code is independent of network and avoids personal data. All output objects are deliberately release-blocked. See `QA_EVIDENCE.md` for exact code identities, runs, and limitations.

**Final disposition: ALL SIX HOLD_UNSENT; commercial #03/#05 HOLD_MERCHANT; no new WordPress, subscriber, merchant, analytics, social, email, settings, spend or live PR changes.**
