# R445 — read-only conversion-first release and ownership decision
2026-11-18 · Draft PR stacked onto Dispatch R444. Original issue #175 and safeguard #201 are untouched. Homepage PR #49 remains frozen.

## Actual evidence, not extrapolation
Authenticated WordPress Jetpack status at 2026-11-18 10:30 UTC: enabled; site_can_send=true; newsletter totals=3, confirmed=3, unconfirmed=2, suppressed=0. Subscriber list previously filtered to Email subscription=Subscribed shows 3 eligible provider records; do NOT call these 3 independent, acquired readers (publisher-associated records observed). Zero proven newly confirmed external leads. Five most recent notification records status never_sent_opted_out. Settings: auto new-post emails=false, email_content_format=full, reply_to=no-reply, welcome configured with PDF. No received welcome and no native Jetpack Preview witnessed. Historical October 30 counts were 2/2/2; no summation of confirmed and unconfirmed. None of these snapshots grants sending permission.

WordPress's non-sending Preview is available in an unpublished post's Newsletter sidebar and separate from sending a test email. Its actual rendered footer and mobile behavior must be witnessed by an authorized site editor. No WordPress draft or settings write authorized. Valid publisher postal and functional unsubscribe remain required for commercial messages: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## One offer, no switcheroo
Target high-intent reader: a viewer already curious about perception/suggestion who opts into the free Focus Fieldbook, returns for evidence-based advice, and voluntarily reads a clearly disclosed exact-product buyer guide. The prospective first paid offer remains **Zen12** in Issue 03; Issue 05 is separately reserved for **Hypnosis Live**, never Total Focus. Only 2/6 commercial placements. Both guides are currently source-only; merchant email-channel approval, identity, issued earning URL, exact SKU, price, format, refunds, media claims, and permission for promotional creative are NOT VERIFIED. The 2026-08-24 Refersion notice found in Gmail was application-pending, not an approval. Neither existing public offer landing pages nor a consumer newsletter grant account permissions. No link activation.

## Non-sending progression hypothesis (NOT a schedule)
- Segment A: confirmed Dispatch email-eligible, independently consented; evidence-oriented interest. Offer Issue 01 → live change-blindness article → optional /focus/ at visitor's own choice.
- Segment B: a *future* actually new provider-confirmed subscription with documented source asset_id and consent scope. Fieldbook welcome delivery must be witnessed by permitted, recipient-initiated verification; no new signup tests without approval.
- Segment C: voluntary visit to the actual published Zen12 independent guide **after** Mind and founder approve offer-specific claims, checkout terms, affiliate email marketing rights and public guide URL. Issue 03 may then carry one disclosed guide CTA. No automatic product follow-up triggered from merely viewing the PDF.
- All segments: opt-out respected by provider; no segmentation using health/sensitive attributes; no subscriber PII in repository; no emailing anyone until explicit founder final go-ahead. Issue 06 closes on the free Fieldbook, not a last-chance sales pitch.

## Attribution acceptance
Use existing Claude/Issue #820 implementation only: social utm_source by actual platform, utm_medium=organic_social, utm_campaign=<topic>_pilot_2026_11, utm_content=<immutable asset_id>. Newsletter utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_pilot_2026_11, utm_content=issue06_r445 for *future* approved links; do not alter real URLs or put invented tracking on the live site. The first-party CTA is /focus/ without tracking until that contract is accepted. Client-side click and URL query params are diagnostics, not confirmed leads. Count confirmed_signup only from a new authoritative eligible provider transition with deduplication and documented consent. Do not export email addresses.

Paid order requires settled transaction or merchant payout ledger linked to attributable cohort, with fees and refunds; never assume affiliate click or checkout equals sale. Compute realized net revenue per 1k qualified-human sessions only when both numerator and auditable denominator exist, separately for 7/30-day cohorts. If no eligible external readers or missing external order records, display NOT COMPUTABLE, not $0 and not 100% conversion.

## OFFER → STEP → BLOCKER → PROPOSED CHANGE → EVIDENCE → OWNER
| Priority | Offer / step | Blocker | Change/test (no live write) | Current evidence | Owner |
|---|---|---|---|---|---|
| P0 | Free Fieldbook → newly confirmed lead | 3 provider records do not establish independent acquisition or received welcome | Get read-only, privacy-safe confirmed transition and welcome receipt authorization | Provider settings yes; receipt NO | Focus / Claude |
| P0 | Dispatch → compliant recipient inbox | True native Preview, FV postal & opt-out unverified | Site editor witnesses desktop/mobile native Preview and full footer without sending | Offline previews only; FAIL/HOLD | Dispatch / Founder |
| P0 | Zen12 → approved guide → settlement | EMAIL affiliate rights / exact checkout / live guide absent | Mind obtains actual account permission and current offer evidence, founder reviews Guide A/B | Only source-only candidate guides; FAIL/HOLD | Mind / Commerce |
| P1 | Issue 06 → /focus/ | Original too brief and weak investigative anchor | Review R445 Fisher story and free practical log | Draft + independent sources + offline QA; NOT adopted | Dispatch / Founder |
| P1 | Grok → sessions → orders | No qualified human-session or settlement join | Validate existing asset_id to landing/event data via Claude without duplicate tags | No independently verified paid cohorts | Grok / Praxxis / Claude |

## Hard release decision
Six canonical issues remain untouched; four editorial, two commercially reserved. All HOLD_UNSENT. No newsletter/test send, subscriber contact/import, WordPress post/settings/subscribe change, merchant link, paid platform, merge, social post or expenditure permitted. Release blockers do not close based on code tests or preview mockups.
