# Dispatch R356 — independently checked source/release QA

**Date:** 2026-11-14 PT. Source-only DRAFT / NOT ADOPTED / UNSENT. Parent is latest prior Dispatch draft #2477 at `96a7ee7e341f575d38267d48d7ff80ecfbef90a8`. The original #175, per-edition gates #201, homepage #49, merchant #171 and Focus #129 are not edited.

## Source-of-truth reads

- Read [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) and its newest comments, [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), original #175, original QA #201, latest Dispatch #2477. Fresh [Mind #2484](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2484) remains an unmerged and unapproved source-only guide, not a permissible live Zen12 destination.
- Authenticated WordPress Jetpack `status`/`get_settings` **2026-11-14T14:31:51–52Z**: enabled, automatic post emails OFF, email format FULL, no-reply, sender display Final Vestige Studios, configured 52-page Focus Fieldbook welcome but no verified inbox receipt. Subscriber aggregate `total=3, confirmed=3, unconfirmed=2`; separate WordPress Stats show WP.com followers 3/direct-email followers 0. Count sets may overlap. Eligible email recipients **UNKNOWN**, not 3.
- Read live WordPress page content for [Dispatch / ID 523](https://finalvestige.com/dispatch/), [Focus / ID 1579](https://finalvestige.com/focus/) and [Editorial Standards / ID 17](https://finalvestige.com/editorial-standards/). WordPress page representation can flatten dynamic Subscribe blocks to a self-link; do not infer visitor failure. No form submitted.
- Read connected Grok/Praxxis [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) confirming `utm_medium=organic_social`, and seller primary pages plus official WordPress/FTC. Bounded Gmail read-only searches found October 25 subscription CONFIRMATION only, no actual matching welcome receipt and no account-named affiliate-email approval. **Negative search is not proof no contract exists elsewhere.**

## Original PR #175 — actual native Python

From the previous archived, byte-exact master source (mounted from FV_Dispatch_R354_Native_Consent_Revenue_QA.zip), independently recalculated eight Git blob SHA1s and checked against **live GitHub source at exact current PR #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`**. Six original Markdown issues, manifest and test match. Native `python -m unittest discover -s ...` **6/6 PASS** in this run. No rewrite of master.

## R356 new evidence

- New research-grounded optional Issue 03 addresses original Zen12 marketing with 1784/1785 commissioners' controlled observations, Wellcome primary record, Zen12 exact merchant sales page, separate 2021 mindfulness evidence. Subject/preheader honest; commercial disclosure is directly after SINGLE proposed INACTIVE CTA; final postal/unsubscribe placeholders remain. This has **not been substituted into the original six**.
- New read-only Python release/consent/revenue validator plus committed 36-case adversarial test module, all-false proof fixture and deterministic HOLD report. Local native Python implementation passed **36/36** release tests; local offline HTML review passed **18/18** structural/source assertions; total **54/54** local native test passes, using synthetic cases. Committed source contains equivalent code and 36 named tests, but **byte-identical committed-source native Python execution has not been independently demonstrated**. Do not mislabel the GitHub Python suite as CI green.
- Local Chromium via Playwright and executable `/usr/bin/chromium`: first offline reviewer had **mobile horizontal overflow (438 px scroll at 320/375/390)**. Corrected table fixed layout and overflow-wrap; then offline local review **6/6 widths PASS (320, 375, 390, 768, 1024, 1440 px)** with one H1 and no script/form/iframe. GitHub HTML also received the same fixed-layout treatment. This is **offline local HTML testing, NOT a genuine Jetpack editor, inbox or real screen reader verification**.
- Independently fetched all nine new R356 GitHub files after mobile fix at their blob SHA1s. **20/20 source-level structure, disclosure, privacy, schema, hold, CTA and tracking assertions PASS**. Preheader visibility in an actual Jetpack email, sender, postal footer and working opt-out NOT TESTED.
- Revenue: all test orders are synthetic. Zero synthetic orders in report must **not** be read as proven zero real orders or revenue; net USD per 1,000 genuinely qualified sessions is **NOT COMPUTABLE**.
- All original 6 = `HOLD_UNSENT`; commercial 03/05 additionally = `HOLD_MERCHANT`; R356 candidate = `NOT_ADOPTED`. No production mail/test email, subscribers, new list, WP draft/post/settings, affiliate activation, social post, analytics code deployment, PR merge, spend or actual order.

## Real release blockers / owner proof

1. Mind/Commerce: named publisher acceptance, explicit EMAIL rights, exact issued earning URL, approved LIVE guide and buyer-facing checkout/return/creative terms.
2. Focus/Claude: provider-confirmed opt-in and consent identity dedup, privately reconciled eligible recipient count, actual received Fieldbook welcome.
3. Founder/Dispatch: valid FV sender mailing address and native **Preview email**, later separately authorized real received email with functional unsubscribe, final creative approval.
4. Grok/Praxxis/Claude: independently verified published asset ID, canonical social attribution and real qualified-human session receipts.
5. Commerce/Claude: independently settled order/commission ledger, fees, refunds and 7/30-day cohort revenues; no fake sales, campaigns or A/B claims.

**Next exact acceptance step:** acquire merchant EMAIL rights and provider-authoritative subscriber consent first, not an extra draft. Founder retains release control.

## R356 independent receipt-hardening correction

Follow-up exact GitHub commits after the first QA record strengthen the offline gate: a bare Boolean `provider_proof` is insufficient without Jetpack provider-source and opaque receipt reference; a bare Boolean `independent_receipt` is insufficient without an explicit merchant/payhip settlement-report source and opaque receipt reference; net revenue per 1,000 sessions is suppressed without an explicit first-party qualified-session source reference. Three additional synthetic adversarial tests were committed. **36 named GitHub Python tests**, and analogous local native implementation produced **36/36 PASS**, with **18/18 local HTML candidate tests** = 54/54 local. The committed test-source is not externally run by hosted CI, and references alone are not authentication: owner must independently attest actual provider records before any business result can be accepted. No real subscriber or order records were used.
