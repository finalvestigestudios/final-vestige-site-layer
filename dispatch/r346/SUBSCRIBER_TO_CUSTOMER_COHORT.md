# Dispatch R346 — One-offer subscriber progression hypothesis (NOT A SEND SEQUENCE)
**Scope:** Existing six-issue weekly draft only. This is a mapping of three existing slots, **not three new emails**. No change to Jetpack settings, no new address list, no targeting automation, no claims of conversions.

## Primary hypothesis
A reader who comes to Final Vestige for the history of perception may be interested in a self-directed attention routine and only later in an optional guided-audio format. This does **not** justify presuming that a Fieldbook downloader has opted into a commercial newsletter. Test the relevance of one merchant at a time; the current proposed focus is *Zen12 Premium*, but this is **HOLD** until it is genuinely approved to email Final Vestige subscribers and a first-party presell guide is live. The **original six** remain the founder's 4 editorial / 2 commercial balance.

| Existing slot | Reader question / progression | One primary CTA and evidence | Commercial state |
|---|---|---|---|
| #01 history/perception | Can I trust my observation? | one *published* source-based investigation; do not repeat #02 destination without editorial approval | editorial only |
| #03 self-directed focus / format evaluation | Is a 12-minute listening format worth buying? | **FUTURE ONLY**: one verified independent first-party Zen12 guide, after direct email rights and named merchant earning link are authenticated | HOLD_MERCHANT; no URL activated |
| #06 seven-day evidence log | What did I actually do, not merely feel? | non-subscription editorial guide or a direct free download; do not pressure confirmed subscribers to re-enter signup | editorial only |

Issue #05 remains the second *reserved* commercial slot, but **must not be co-promoted in the Zen12 progression**. It requires a separate product, recipient-fit and permission decision. Existing published /focus/ already gives a direct PDF path; do not infer consent from use.

## Minimal measurement without duplicate tracking
* First-party source from Grok: utm_source=(actual platform), utm_medium=organic_social, utm_campaign=(actual cluster campaign), utm_content=(genuine immutable asset_id); accept only supplied/verified Grok IDs and platform-permitted routes. Never invent cross-device attribution.
* A **single** semantic event \`confirmed_signup\` occurs only when the Jetpack provider asserts confirmation for a consented subscriber record. The provider-side implementation must privately de-duplicate attempts using a stable provider confirmation key; no user email, subscriber ID or raw provider key should go to GitHub, PRs, analytics screenshots or Drive. Public/coordination report: counts with provenance/confidence only. Download and form-submission events never create \`confirmed_signup\`.
* The handoff is a cohort summary of new confirmations after prior confirmation history reconciles; the WordPress aggregates total3/confirmed3/unconfirmed2 cannot establish this count. Subscriber “confirmed” is NOT the same as mailbox receipt and not proof of mailing consent for a particular commercial offer.
* Email CTA: \`utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=issue03_zen12\` only on a **future first-party verified landing URL**, and only after Claude validates existing native analytics (avoid new scripts, personally identifying identifiers, tracking pixels or partner-unauthorized URL changes). These are a proposed contract, **not live tracked links**. Preserve an ordinary untracked fallback where tracking consent is not granted.
* On owned site: distinguish \`offer_guide_view\`, \`affiliate_outbound\`, \`merchant_checkout_start\` (only independently observable), \`merchant_confirmed_paid_order\`, \`affiliate_confirmed_settlement\`, \`refund_reversal\`, \`fees\`. Never promote a click or consent confirmation into a paid conversion.
* Seven and thirty-day cohorts: \`realized_net_revenue_per_1000_qualified = 1000 * (independently settled owned receipts + independently settled affiliate commissions - refunds - fees) / authenticated qualified-human sessions\`; report **NOT COMPUTABLE** if qualified denominator, settlement or attribution is missing. Never double-count merchant order and its affiliate commission as independent customers. Tiny samples are diagnostic, not A/B certainty.

## PII-free cohort acceptance template
| Value | Current state | Evidence required | Who |
|---|---|---|---|
| Provider-confirmed, deduped, consented subscriber | UNKNOWN | Restricted Jetpack authoritative per-record status and consent provenance | Claude / Focus |
| Fieldbook welcome received and PDF opened | UNKNOWN | Founder-authorized controlled inbox evidence; authorized receipt only | Focus / Founder |
| Relevant one-offer guide live | NO | Mind-owned first-party URL, legal QA, accurate comparison | Mind / Commerce |
| Affiliate email permission and issued earning URL | NOT VERIFIED | Named acceptance/current partner documentation | Mind / Commerce |
| Eligible inbox recipients | UNKNOWN | Private active audience/opt-out/consent reconciliation | Focus / Founder |
| Verified paid sales and commissions | UNAVAILABLE | Authenticated merchant/Payhip settlements, refunds and fees | Commerce |
| Verified net revenue per 1,000 qualified sessions | NOT COMPUTABLE | Both authentic purchase numerator and qualified-session denominator | Claude / Commerce |

## Experiment (proposal, not deployed)
After all authorizations and an actually reachable cohort exist, retain the same original issue, sender, CTA and disclosures while testing **one** editorial variable with an appropriately sized real audience. With the current tiny ambiguous list do not assert uplift, statistically significant A/B results or attributed revenue. The first actionable experiment is proving a genuine delivery, not manipulating subject-line CTR. A future commercial variant must never be sent merely because the tool's checks are green.