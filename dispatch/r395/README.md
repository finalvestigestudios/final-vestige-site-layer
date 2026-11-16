# FV Dispatch R395 — verified conversion, not email volume (SOURCE-ONLY / HARD HOLD)

Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Merchant owner: [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Lead capture owner: [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129). Monetization coordination: [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Historical six-issue baseline is [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), controls are [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), native six-edition email specimens are [PR #2703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2703), and immediate prior cohort proof is [PR #2709](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2709). This R395 branch stacks directly on R394. Frozen flagship PR #49 is not edited.

## Material risk discovered
R394's settlement verifier correctly rejected unaudited zero revenue but still divided **ALL** independently settled publisher commissions by an audited qualified-session number without requiring those commissions to be from **the same Grok asset and 7/30-day cohort**. An unrelated advertiser's legitimate commission could falsely inflate the purported Grok-attributed conversion rate or net dollars per thousand qualified human sessions. R394 also silently ignored duplicate settlement IDs with conflicting refund/fee values. These are *accuracy/integrity gaps in an offline verifier*, not claims that Final Vestige has incorrectly reported real revenue.

## New code and executed evidence
- `cohort_guard.mjs`: zero-dependency pure, **NO SEND** function; requires 7/30-day UTC session window, authentic first-party audited human sessions, named unique Grok asset ID and campaign ID; requires verified exact SKU and EMAIL-channel partner rights, LIVE approved guide, independently reconciled merchant ledger, explicit completeness attestation; joins settlement by asset+campaign+session date; rejects conflicts, checkout events and PII; reconciles refunds/reversals/fees and deduplicates unique paid orders.
- `cohort_guard.test.mjs`: **31 native Node tests** using explicitly synthetic fixtures; 31/31 PASS on local Node v22.16.0. Final Git blob identity and results recorded in QA.
- `COHORT_AND_CONSENT_CONTRACT.md`: actual customer/lead journey, event schema, 7/30-day denominator acceptance, test plan and blocked real-data joins.
- `JETPACK_LEGAL_AND_NATIVE_PREVIEW.md`: exact no-send WordPress owner-side inspection for consent, welcome, native rendering, footer and unsubscribe.
- `SELLER_COPY_AND_CTA_DECISIONS.md`: original six-issue copy prioritized by revenue intent and compliant seller boundaries; no draft is silently changed.
- `PROVIDER_SNAPSHOT_REDACTED.json`: latest independent provider settings/status and all-false approval evidence.
- `REVIEW_BOARD.html`: static accessible reviewer surface, no active affiliate link or recipient form.
- `POST_COMMIT_QA.md`: test and source authenticity details.

The current site is **BUILT** as a Focus landing page and newsletter signup. It is **NOT VERIFIED** as a received welcome-to-purchase journey. This code is **BUILT + NATIVE TESTED**, not deployed. No native Jetpack-preview/MIME or provider-filtered recipient result exists.

## Release holds (unchanged)
Original Issues 01/02/04/06 are editorial; 03 Zen12 and 05 Hypnosis Live/Total Focus are the only 2 prospective commercial placements. All six are **HOLD_UNSENT**. 03/05 additional HOLD_MERCHANT; 04 HOLD_COPY. Do not send a welcome/test email, publish, merge, activate a merchant link, change Jetpack settings, import any subscriber, spend or touch Grok/Claude queues without founder's explicit final approval.

Sources: [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC endorsement disclosures](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking), [WordPress Preview email](https://wordpress.com/support/newsletter/email-appearance/), [WordPress subscriber status](https://wordpress.com/support/troubleshooting-not-receiving-notification-emails/).