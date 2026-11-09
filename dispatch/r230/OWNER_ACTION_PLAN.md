# R230 conversion-critical action matrix (draft, not deployment)

| Offer → funnel | Blocker | Proposed change / experiment | Evidence / status | Owner |
|---|---|---|---|---|
| Zen12 → customer | No named affiliate acceptance, EMAIL rights, issued link, verified final cart or published buyer guide | Obtain account/provider proof privately, review /hnp specific terms and guide, keep email CTA inactive | **HOLD_MERCHANT**, seller page ≠ authorization | Mind #171 |
| Total Focus → customer | Same authorization, final checkout/refund, competing Issue 05 CTAs | Approve one reviewed guide after product/rights verification, not a merchant checkout blast | **HOLD_MERCHANT**, seller 33m/47MB observed only | Mind / Dispatch |
| Grok → Focus | No verified asset/campaign human-session attribution | Cross-check existing UTM/asset inventory, no duplicate scripts | **UNKNOWN** | Grok / Praxxis / Claude #820 |
| Focus → gift | Arbitrary nonblacklisted `?subscribe=` reveals gift | Stage safer semantics; gift reveal cannot imply confirmation | **REPRODUCED OFFLINE** native Node mock, not live signup verification | Claude / Focus #129 |
| Focus → confirmed email lead | 3 total/3 confirmed/2 unconfirmed, unknown eligible recipient breakdown | Read-only authenticated Jetpack Subscribers > Email subscription statuses, deduplicate and aggregate; no email export | **HOLD** pending provider status proof | Claude / Focus |
| Existing subscriber → PDF | In-app browser text says sign up again | Use R228 direct welcome link copy, do not duplicate implementation | **OPEN** R228 PR #1711 | Claude / Focus |
| Dispatch → inbox | Actual welcome delivery, Final Vestige postal address, unsubscribe MIME, subject rendering unverified | Get controlled native preview only after explicit founder approval; check existing authorized received evidence first | **HOLD** | Dispatch / Site QA |
| Buyer → net revenue | No settled paid order, fees/refunds or qualified session denominator | Native settlement reconciliation and 7/30-day cohort report, tiny-sample caveat | **NOT COMPUTABLE** | Commerce / Praxxis #820 |

Suggested landing-page copy for **separate staging review only**: “Trouble opening the PDF in an in-app browser? Open the download link from your welcome email in Safari or Chrome. If you already subscribed, do not complete the form again. A visible PDF button does not mean your email subscription is confirmed; follow the confirmation message to finish joining The Dispatch.”

No emails/posts, site writes, test signups or marketing attribution changes authorized.