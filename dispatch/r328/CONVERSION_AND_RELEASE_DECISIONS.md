# R328 — subscriber to paying customer, not email-volume optimization

**Source-of-truth:** master PR #175, Issue #174, companion #171, Focus #129, revenue #820. This R328 package does not rewrite/adopt prior R321–R327 alternatives or amend PR #49/homepage.

## Verified WordPress read-only snapshot (2026-11-13T11:39 UTC)
Jetpack Newsletter **enabled**, site_can_send **true**, auto-email new posts **OFF**, full content, from name “Final Vestige Studios”, reply-to no-reply; welcome **configured** to contain the 52-page Focus Fieldbook PDF URL. The latest inspected post sends each report `never_sent_opted_out`. **Do not infer no mail has ever been sent.** Dashboard total=3/confirmed=3/unconfirmed=2 cannot be added; follower classes and actual email-eligible consent are different data dimensions. Actual reception/eligibility are UNKNOWN.

Published /dispatch/ page #523 offers a Jetpack form and routes readers toward /focus/; published /focus/ #1579 uses Jetpack opt-in and the Fieldbook download. R320 previously reproduced an arbitrary URL query showing a gift UI; visibility is not a provider-confirmed subscriber. No new live signup or download performed here.

## One subscriber-to-offer journey (proposal only; NO sends)
1. Grok-authored video with authentic unique asset_id and campaign UTM → a relevant, actually published article; Praxxis audits topic matching. Do not infer attribution from query strings alone.
2. Voluntary /focus/ or /dispatch/ Jetpack form → provider's authenticated new site enrollment; consent, email eligibility and opt-out state; preexisting active followers are not new leads. Existing WordPress.com accounts may activate without an email confirmation challenge. On receipt, provider confirmation and Welcome Fieldbook links **require inbox proof**.
3. Use **existing welcome email only**, no duplicate message. Editorial Issue 01 or 02 provides historic/perception evidence. Do not send until founder approval.
4. Only if source-tagged subscriber has voluntarily engaged with relevant attention content, offer exactly one **verified/approved** relevant guide. Zen12 Issue 03 is a candidate, NOT activated. No behavioral tracking beyond approved first-party analytics/consent.
5. Reader independently chooses guide / verified merchant link if authorized. Merchant's separate newsletter signup is a distinct consent relationship. Log affiliate click only as interest, not revenue.
6. Independent partner paid-order/commission settlement → refund/fees join → realized net revenue. No partner proof means metric N/A (NOT COMPUTABLE), not $0.

## Funnel priority decisions
| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL PROOF | OWNER |
| --- | --- | --- | --- | --- | --- |
| Zen12 Premium | Guide-to-buyer | Account email permission, earning URL, live approved guide missing | Mind supplies authorized acceptance + canonical guide and checkout record | HOLD; official public portal alone insufficient | Mind / Commerce |
| Total Focus | Guide-to-buyer | Partner permissions and checkout pricing/refund claims unknown | Validate product-specific seller page, approved guide and authorized tracking | HOLD; 33min/47MB seller description only | Mind / Commerce |
| Seven Day Focus Fieldbook | Signup-to-welcome | Eligible list ambiguous, receipt not confirmed; client-side gift UI untrusted | Provider-sourced consent proof and founder-authorized received-message review | UNKNOWN; 3/3/2 overlapping counts | Claude / Focus |
| The Dispatch | Newsletter-to-inbox | Native preview, valid Final Vestige mailing address, functioning unsubscribe unknown | Founder-authorized WordPress native preview/received email & footer QA, no new list | HOLD; offline HTML is **not** Jetpack evidence | Dispatch / Founder |
| Grok social | Qualified visit-to-paid order | Missing verified asset/session/order joins | Existing Claude attribution, independent paid settlements | NOT COMPUTABLE; avoid fake clicks/sales | Grok / Praxxis / Claude / Commerce |

**Proposed event contract:** `confirmed_signup` occurs only after authenticated provider new enrollment and current consent/eligibility, deduped by opaque provider enrollment ID; do not emit duplicates for legacy subscribers or request attempts. `dispatch_cta_click` is a landing-link interaction only, `affiliate_outbound_click` is not a purchase, `paid_conversion` requires independent settled order evidence. Aggregate 7/30-day cohort by verified acquisition asset; key KPI net realized revenue per 1,000 qualified-human sessions, N/A until denominator and settled revenue exist. No PII in GitHub or URLs.

## Full hard-stop evidence before human send review
- Partner approval for specific EMAIL channel, allowed link format, issued affiliate earning URL, approved creative and seller price/returns at checkout (Issues 03/05 only).
- Live first-party warm-up guide published and owned by Mind; approved independent claim/disclosure review; **commercial link directly beside compensation disclosure**.
- Native preview/email tests reviewed by human with the real provider footer, unsubscribe action and a **valid Final Vestige sender postal address** (not merchant's or Automattic's); delivery + welcome proof.
- Reconciled eligible subscribers/opt-in/suppression privately, keeping addresses out of GitHub; consent and privacy signoff.
- Founder approves full final creative, exact recipient audience and schedule separately. No autonomous send or WP write.

All six original issues: **HOLD_UNSENT**; Issues 03/05: **HOLD_MERCHANT**. R328 previews are **REVIEW_ONLY_NOT_ADOPTED**. Zero production writes or sends.
