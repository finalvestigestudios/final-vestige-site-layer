# Dispatch R252 — form action integrity and subscriber-to-customer evidence

**Status: DRAFT / RESEARCH / UNSENT / NO LIVE CHANGES**  
**Owner:** Final Vestige Dispatch Studio, Issue #174. Partner boundaries: #171 (Mind & Affiliate), #129 (Focus), #820 (commercial measurement).  
**Stack:** PR #1862 R251 @ `4369446ff110708d9a6bf9f3c251fcf1965605b1`, continuing R250 #1855. The original 6-issue PR #175 @ `d57ccdba3aee8f065e143e101c2945f4f3d01647` and R201 readiness PR #201 remain unchanged. Frozen homepage PR #49 remains untouched.

## Material new finding from exact predecessor code

R251's visual form inspector accepts *both* (a) a same-page GET form and (b) a seemingly visible form whose submission button has `pointer-events:none`. These are **synthetic counterexamples**, not evidence of a defective Final Vestige signup. Reproduced with native Chromium running the exact R251 inspector from verified commit. In both examples it returned `FORM_BINDING_VISUALLY_VALID_UNSUBMITTED`.

A form can have a visible, labeled email field and a bound submit button yet remain nonactionable or lack evidence of a subscription route. R252's conservative, non-interacting inspector checks the submit button's actual associated form, pointer-event availability, center-point hit-test for a blocking overlay, explicit same-origin action and POST method. **This is a heuristic only**: a legitimate JavaScript-intercepted form may use GET or no declared action. Such forms must be marked **ACTION_PATH_UNVERIFIED**, **not broken**, and require approved live-browser review before claims of working acquisition. A visible POST form is **not** a successful signup, consent, welcome delivery or merchant conversion.

## Evidence executed — 10 November 2026 (UTC)

- Original campaign: downloaded exact source from GitHub PR #175; verified Git blob SHAs of all **six manuscripts + manifest + original Python test**; ran `python -I -m unittest discover -s tests -v` natively against matching files: **6/6 PASS**. This confirms baseline static safeguards only, not campaign eligibility.
- R251 false-positive: executed exact source inspector from `dispatch/r251/form_proof.py` against synthetic GET and non-clickable fixtures; both erroneously returned visually valid.
- R252 inspector: `python -I -m unittest discover -s . -p test_route_proof.py -v` in native Python 3.13 and Chromium (Playwright, executable `/usr/bin/chromium`), **18/18 PASS**. Fake origin is provided through an HTML `base` element inside offline `about:blank` documents. **No Internet or production visitor session**. Positive POST fixture is not a real Jetpack endpoint/confirmed user journey.
- Authenticated WordPress read-only @ 2026-11-10 08:33 UTC: Newsletter enabled; post auto-send OFF; email format FULL; configured 52-page Fieldbook welcome; Jetpack total=3, confirmed=3, unconfirmed=2, suppressed=0; five recently published posts individually **never emailed** (`send_subscription=false`). Counts are **not additive**. Actual `Email subscription: Subscribed` total unknown. Confirmed-at-dashboard counter does not alone establish current deliverable recipients.
- Public /focus/ extraction shows an email field, submit action and accessible direct Fieldbook link; REST page content includes a self-page subscribe anchor fallback. Different representations **do not establish failure or success**. /dispatch/ similarly has a REST fallback. Live browser/keyboard/signup/double opt-in has not been tested.
- Seller source pages `https://zen12.com/hnp` and `https://zen12.com/secret/` show materially different advertised promotional arrangements. No currently applicable exact authorized offer, paid checkout, affiliate tracking identity, permission to promote by email, price, final refund conditions or specific product-efficacy substantiation is verified. Hypnosis Live Total Focus must be assessed separately. Mind Studio owns these records. **No commercial URL is activated.**

## Conversion-first acceptance and owner matrix

| Offer -> step | Blocker | Read-only next experiment / owner | Result |
| --- | --- | --- | --- |
| Free 52-page Fieldbook -> visible signup | REST fallback vs public text + no actual browser proof | Anonymous `/focus/` and `/dispatch/` Chromium 390/1440 desktop/mobile, keyboard and popup inspection; Claude / Focus / Site QA | New **offline** form-action 18/18 PASS; **LIVE UNKNOWN** |
| Signup -> qualified confirmed lead | 3 confirmed counter may include Reader-only, paused or bounced | Jetpack Dashboard > Newsletter > Subscribers > **filter Email subscription: Subscribed**, record aggregate only; Focus | **UNKNOWN**; do not export identities |
| Confirmed lead -> welcome PDF | Configured message is not received-email proof | Audit existing lawful confirmation/welcome receipts without sending, or separately approved founder-controlled test; Focus / Dispatch | **NOT VERIFIED** |
| Dispatch issue 03 -> Zen12 warmup -> checkout | Affiliate email rights, authorized deep-link, exact terms, approved *live* guide missing | Authenticate partner account and approved guide, current seller offer identity; Mind | **HOLD_MERCHANT** |
| Dispatch issue 05 -> Total Focus guide -> checkout | Separate product rights and exact listing unknown | Separate named merchant/partner review; Mind | **HOLD_MERCHANT** |
| Any issue -> inbox | Jetpack generated preheader and legal footer not observed | Authorized **unsent** native WP visual preview (do not enable send to subscribers or publish); approved received-email test only after explicit consent; Dispatch / QA | **NOT VERIFIED** |
| Purchase -> realized net revenue | No independently settled paid order, refund or fees reconciliation | Existing source-of-truth commerce dashboard with opaque order IDs, 7/30-day cohorts, no PII; Commerce / Praxxis | **NOT COMPUTABLE** |

## Release, attribution and compliance

Preserve **four editorial + two optional commercial drafts**, one free Fieldbook and the existing Jetpack list; do not change original manuscripts. No alternative copy is automatically approved. Commercial recommendations must lead first to an independently approved *live* FV evaluation, not directly to an unapproved vendor checkout. Near any qualifying recommendation: “If you buy through a link in our guide, Final Vestige may earn a commission.” Do not copy vendor brainwave, therapeutic, time-equivalence, urgency, countdown or guaranteed-result claims as established facts.

One optional `confirmed_signup` event is valid only after provider-side email subscription confirmation; key it to opaque provider transition ID and campaign consent version, deduplicate replays, and do not count attempts, Reader followers, form visibility or Fieldbook downloads as confirmed leads. `asset_id` and `utm_campaign` preserve Grok creative provenance without exposing audience identity. Measurable conversion requires independent settled paid-order evidence adjusted for refunds and fees. **Net revenue per 1,000 qualified human sessions is presently NOT COMPUTABLE**; never infer sales from clicks or manufacture A/B performance on three reported subscribers.

FTC official guidance requires accurate commercial headers, honest subject, physical **publisher** address and usable opt-out, with appropriate disclosures near affiliate content. Automattic's own postal address in a WordPress confirmation email is not proof of the publisher's commercial-mail address. WordPress may control sender domain and generated footer; HTML/offline tests do not prove what arrives.

**Real-world release remains** `ALL_SIX_HOLD_UNSENT`, `ISSUES_03_AND_05_HOLD_MERCHANT`. Zero sent, zero test messages, zero WP writes, zero affiliate activation, zero subscriber reads/exports, zero platform expense. Founder alone approves final content, audiences and sending.

### Primary references

- https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174
- https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- https://wordpress.com/support/subscribers/ (reviewed Nov 4, 2026; subscription statuses and filters)
- https://wordpress.com/support/newsletter/email-appearance/ (last reviewed Oct 6, 2026)
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- https://finalvestige.com/editorial-standards/
- https://zen12.com/hnp
- https://zen12.com/secret/
