# Dispatch R268 — source-of-truth attribution correction (HOLD ONLY)

**November 10, 2026, 16:39–17:xx PST.** Owner: Dispatch #174; Mind & Affiliate #171; Focus #129; conversion #820; creator-led acquisition: Grok/Praxxis TASK-008. This is a **non-sending, non-publishing draft**, stacked exclusively on R267 #1964 @ `92bdbcd2adb7202da1e4d6bec8555c27ffe68b22`. Original six-issue #175, hold gates #201, frozen homepage #49, WordPress production, subscribers, merchant accounts, and Grok's publication queue stay unchanged.

## Three reproduced defects in the R265 prototype, not hypothetical seller outcomes

Fetched the exact prior `dispatch/r265/cohort_audit.js` blob **dd1c3b9f227ccd356e701d9e8037bf30f43df703** at PR #1951 commit `fb5f590b51d0539d79156aaad592575f1e192c85` and executed it in read-only V8 with synthetic examples.

1. **Broken real campaign naming:** R265 accepts campaigns starting with literal `cluster_pilot_`, yet approved Grok TASK-008 specifies `utm_campaign=<topic_cluster>_pilot_2026_11`, such as `mind_pilot_2026_11`. R265 returned `invalid_session_0` on the intended real format. That could have silently blocked qualified acquisition evidence while testing only a placeholder.
2. **Negative net revenue impossible:** R265 rejects `refund_cents + fee_cents > gross_commission_cents`. A fully refunded purchase with a nonrefundable processing fee would correctly produce **negative net revenue**, not be discarded. Synthetic reproduction (gross 100¢, refund 100¢, fee 5¢) returned `invalid_settlement_0`.
3. **Conflicting opt-in events silently undercount:** R265 deduplicates a reused confirmation reference by taking the first status. Synthetic `pending` followed by `confirmed` with the same event reference returned `pass=true` and zero leads. Whether Jetpack actually reuses a reference is **unknown**; this is a demonstrated unsafe input behavior, not a claim that the provider does so.

R268 adds an isolated **v2** analytical contract without replacing R265, changing production, or counting anyone. The tests are executable via `node dispatch/r268/cohort_audit_v2.test.js`.

## V2 correction and analytics contract

- Canonical `utm_source`: YouTube, TikTok, Instagram, Facebook, Pinterest, X, Bluesky as applicable. `utm_medium=organic_social`. `utm_campaign={mind|mysteries|history|preparedness}_pilot_2026_11`. `utm_content` is the actual immutable **Grok asset_id**, not a visitor identifier. Never deploy public tags or modify Grok assets from Dispatch.
- A TikTok bio/profile visit without a provable asset is marked `profile_unresolved`, surfaced separately, and excluded from asset-specific denominators. This avoids inventing per-video attribution.
- Deduplicate **exact identical provider event references** only; if the same reference changes day/status, fail closed and reconcile privately with Jetpack instead of choosing a status. No email address, IP, device ID, cookie, raw consent record, or merchant mailing-list join in the repo.
- Settlement route must match the **same acquisition day**, source, medium, campaign and asset with nonzero qualified sessions. That is only an aggregate consistency condition; **it does not prove a particular session generated a paid order**. Payment verification requires independently authenticated merchant records and trustworthy attribution.
- Keep negative net commissions possible: `net = gross - refunds - fees`, and allow a refunded settlement with net below zero. Orders pending settlement are excluded. Missing reconciled source data stays `null`, **not zero**.
- Seven- and thirty-day acquisition windows use the as-of date; no false A/B significance with a tiny audience. No person-level lead-to-customer rate without explicit permitted linkage.
- `synthetic` and `external_aggregate` inputs are labeled `SYNTHETIC_EXAMPLE` and `UNVERIFIED_EXTERNAL_ATTESTATION` respectively, **even when all data flags are true**. The library never establishes merchant approval, paid revenue, or permission to email; `send_authorized=false` always.

## Actual read-only production evidence (no subscriber identities)

At **2026-11-11 00:39 UTC**, authenticated WordPress newsletter: enabled; automatic new-post sends **OFF**; format **full**; from name **Final Vestige Studios**; welcome **configured** to link the 52-page Seven Day Focus Fieldbook; reply-to `no-reply`. Diagnostic total **3**, confirmed counter **3**, unconfirmed requests **2**, suppressed **0** — counters are **not additive** and provider-filtered email-eligible recipients **UNKNOWN**. Last five inspected posts `never_sent_opted_out`. No received Jetpack Fieldbook message, functional unsubscribe or real FV business postal address was authenticated. The published /dispatch/ copy still omits advance discussion of occasional affiliate recommendations; /focus/ discusses commissions but has repeat-signup friction. Actual consent, deliverability and download receipt remain UNKNOWN. The WordPress PDF media registry matches the configured welcome and Focus page href, but **HTTP/PDF 52-page binary has not been independently verified**.

## Merchant and legal boundary

Official Zen12 seller [standard sales presentation](https://zen12.com/hnp) and [free-audio signup](https://zen12.com/freeaudio) must not be conflated; the latter explicitly joins a **separate vendor newsletter**. Official [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus) promotes a 33-minute recording; the [FAQ](https://hypnosislive.com/faq) discloses a 14-day request period and a five-refunded-sessions-per-year limit. None of the seller's product-specific outcome claims have been independently proven here. Do not quote a current final checkout price, promised effect, guarantee or affiliate payout. Inspire3 Final Vestige-specific acceptance, authorized affiliate link, **email-channel permission**, and permissible marketing materials remain **NOT VERIFIED**. FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): truthful sender/subject, valid business postal address, effective unsubscribe and applicable commercial identification must be checked in the *actually received* message.

## Offer → funnel step → blocker → proposed experiment → evidence → owner

| Offer / funnel step | Blocker | Change or test | Evidence / status | Owner |
|---|---|---|---|---|
| One vetted Zen12 guide → paid merchant checkout | No accepted partner email permission, live approved guide or earning URL | Obtain signed/portal account-specific channel authorization; verify exact approved guide, checkout, terms before any email | **HOLD_MERCHANT**; no paid sale established | Mind & Affiliate #171 |
| Grok asset → Focus/Dispatch landing | R265 rejected canonical UTMs; bio attribution can be ambiguous | R268 v2 contract, verify existing actual source-tagged traffic with Claude before any instrumentation | **BUILT + NATIVE TESTED**, NOT LIVE | Dispatch #174 / Grok / Claude / Praxxis |
| Focus → confirmed lead → Fieldbook | Actual eligible population/consent provenance/welcome receipt unknown; repeat signup prompt | Private Jetpack `Email subscription = Subscribed` aggregate, safely authorized received-email inspection, link test; no duplicate signup | **UNKNOWN**, no list access/export | Focus #129 / Claude |
| Dispatch → compliant inbox | FV physical address and actual opt-out not proved | Separate approved WordPress native preview/received MIME, business address, opt-out workflow | **HOLD_UNSENT** | Dispatch #174 / Site QA |
| Paid purchase → net revenue | No independently authenticated settlements/refunds or source join | Merchant-settlement verification and 7/30-day gross-minus-refund-minus-fee reconciliation | **NOT COMPUTABLE** | Commerce / Praxxis #820 |

**Founder final approval is required for all sends, test emails, publishing, configuration changes, or commercial activation.** R268 does none of these. The 4 editorial : 2 affiliate-draft pilot allocation, original copy, and six hard-release gates remain unchanged.
