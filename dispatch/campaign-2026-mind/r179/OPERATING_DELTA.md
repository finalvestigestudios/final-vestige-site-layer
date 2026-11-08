# R179 — release-critical evidence, NOT another release approval

Parent: draft PR #1361 at `db4f37f03ab4d84a9b0a1d549fecdca1ea3bec7b`. Canonical six-issue draft: PR #175, unchanged. Independent per-edition hold controls: draft PR #201. Frozen homepage PR #49 untouched.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER

| Offer / funnel | Blocker | Safe proposed step | Current evidence | Owner |
| --- | --- | --- | --- | --- |
| Free Fieldbook / Focus→confirmed lead | Focus client display is not authoritative confirmed consent | Inspect signed-out form and provider confirmation without inventing events | FAIL TO VERIFY: no test signup authorized; 3 counted / 3 confirmed / 2 unconfirmed NONADDITIVE | Claude / Site QA; Dispatch observes |
| Existing subscriber→52-page welcome | WordPress welcome configured, actual receipt unknown | Read native delivery evidence for a previously consented test recipient only; no sending | CONFIGURED, NOT VERIFIED DELIVERED | Dispatch |
| Dispatch→email recipient | Native Jetpack template, footer, postal, unsubscribe not proven | On unpublished and **unsent** WordPress editor screen, use Preview email only (NEVER Send test email); capture full rendered evidence and source headers/footers; if preview requires WP draft creation, DO NOT create without founder permission | NOT VERIFIED | Dispatch / Founder |
| Total Focus→buyer guide | Only seller copy and no live guide / email marketing permission | Mind Studio obtains named affiliate acceptance, allowed email channel, earning link, seller-approved creative and founder-approved live guide | HOLD_MERCHANT | Mind Studio / Founder |
| Buyer→realized revenue | No merchant settlement and no first-party qualified-session attribution | Reconcile partner-paid conversion, commissions, refunds and fees by same source-asset identity; no sales from CTA clicks | NOT COMPUTABLE | Commerce / Praxxis |

## Merchant claim boundaries (official exact offer, retrieved 2026-11-06)
- Seller's official Total Focus page: https://hypnosislive.com/mental-skills/total-focus . It describes **33 min** and **47 MB**, and advertises a 14-day refund. Those are seller representations, not checkout fulfillment evidence.
- Words suggesting total focus on demand, productivity outcomes or brain reprogramming **are not demonstrated** by the 1935 Stroop interference experiment; they must not become asserted Final Vestige results. No price included, to avoid ambiguous live discounts and bundle presentation.
- Stroop (1935): https://doi.org/10.1037/h0054651; original readable transcription https://psychclassics.yorku.ca/Stroop/ . This supports color-word interference under specific tests, not an intervention trial for hypnosis products.
- Appropriate legal source: FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; endorsement placement https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking . Valid FV postal address and opt-out must appear in ACTUAL rendered commercial emails; Automattic's address in confirmation mail isn't FV's address.
- Jetpack current documentation updated 2026-11-04: https://jetpack.com/support/newsletter/ . Editor has **Preview email**, distinct from **Send test email**. Mailing only applies when new posts are published and email is toggled on. Current automatic-post email default OFF. No WordPress writes permitted this sprint.

## Current source-of-truth read-only observations (2026-11-07T06:33Z)
- WordPress newsletter subscriptions=true, email_new_posts_by_default=false, email_content_format=full, sender Final Vestige Studios, reply_to=no-reply; latest five published posts never_sent_opted_out. 3 counted/3 confirmed/2 unconfirmed, not additive. Counts ≠ deliverable audience.
- Welcome message contains 52-page Fieldbook URL; actual received welcome not verified. No new sends. /dispatch/ contains Jetpack subscription block but API view presents same-page Subscribe URL; **not** proof of browser breakage. /focus/ client-side success may not demonstrate provider confirmation.
- Editorial Standards demand records as close to event as possible, uncertainties kept visible, substantive corrections, and financial disclosures near relationships.

## Consent-to-revenue contract
Record `confirmed_signup` **only** on an authenticated provider-verified transition following consent, deduplicated across runs; never on a revealed Fieldbook panel, raw follower count, click or unconfirmed request. Preserve `utm_source=<actual_grok_platform>`, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<real_asset_id>` at first-party landing only with consent-aware analytics; use `utm_medium=email`, `utm_campaign=dispatch_mind_pilot_2026_11`, `utm_content=issue_05` only for authorized link publication. Conversion only on independent paid/settled merchant record or own completed paid order, net of refunds/fees, matched by campaign+asset. Do not invent click IDs or leak subscriber email addresses.

**No actual paid conversions asserted. No A/B tests with three counted subscribers. ALL SIX HOLD_UNSENT; commercial #03/#05 HOLD_MERCHANT.**
