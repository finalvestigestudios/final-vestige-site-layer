# Dispatch R282 — consent-to-customer provenance QA

**DRAFT / NO SEND / NOT DEPLOYED / NOT RELEASE APPROVED.** Scope: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), and [Conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). This adds a synthetic offline QA contract; it does not modify [original campaign PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [release review PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), or homepage PR #49. It stacks on [R281 #2052](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2052).

## Conversion first: what the prototype does and does not prove

`conversion_provenance.py` and `test_conversion_provenance.py` are **offline, privacy-minimizing, non-sending** files. Neither uses WordPress, subscriber data, merchant API, Google Analytics, Grok, or email delivery. All sample events and numbers in tests are **synthetic**, **not actual Final Vestige revenues, leads, sessions, or orders**. The asserted `verified` source tokens in fixtures are NOT cryptographic authorization or provider attestations: production code must authenticate source responses server-side before accepting them. The offline function **never** grants release approval.

One canonical `confirmed_signup` should represent an authenticated, consented provider subscription transition, deduplicated on a non-reversible provider reference, with actual current email eligibility. Not a landing view, form submit, follower, click, or every confirmation-email click; previously verified WordPress.com accounts may not require a new click. The prototype returns **unknown** eligible audience from diagnostic counters and refuses to compute net revenue per 1,000 without verified qualified-human sessions and settlement. No subscriber addresses, phone/IP fields, mailing list import, or new analytics tags are allowed.

## Live read-only evidence — November 11, 2026 06:37 PT

- Jetpack Newsletter `subscriptions=true`, `email_new_posts_by_default=false`, `site_can_send=true`, email format `full`, newsletter categories disabled; welcome message includes the existing 52-page Focus Fieldbook link. **No settings changed**.
- Subscriber diagnostics `total=3`, `confirmed=3`, `unconfirmed=2`; earlier follower breakdown `wpcom_followers=3`, `email_followers=0`. **Counters are not additive** and do not establish actual email-eligible people.
- Five recent WordPress post newsletter records are `never_sent_opted_out`; this does **not** prove zero sends across all history. Connected Gmail search located an October 25 confirmation request, **not** confirmed final welcome delivery or PDF download.
- Live `/dispatch/`, `/focus/`, and published Editorial Standards inspected read-only; no native Jetpack received-message preview. The sender's business physical mailing address, delivered unsubscribe URL and functioning opt-out remain **unverified**.
- Official merchant pages https://zen12.com/getstarted , https://zen12.com/welcome , https://hypnosislive.com/mental-skills/total-focus and https://hypnosislive.com/faq provide seller descriptions, not independent effectiveness evidence, Final Vestige's affiliate acceptance, email permission, earning link, or guaranteed checkout/refund terms.
- Commercial email legal review must include FTC CAN-SPAM primary-purpose test across **all six** issues, not just the two merchant-reserved issues: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Founder-preserved six-issue journey

Preserve **four editorial issues / two reserved commercial issues (03 Zen12, 05 Hypnosis Live)**. Zen12 is the **one provisional** buyer-guide funnel, not an approved offer. Hypnosis Live remains a potential alternate. Mind Studio owns verified guide and partner approval; Dispatch owns email and consent; Claude owns production measurement code; Grok owns published social assets. R280 Apollo alternative remains **NOT ADOPTED**.

Hypothesis (not a proven behavior): actual published Grok asset → sourced article → optional Focus Fieldbook → independently confirmed eligible subscriber → helpful non-selling historical Dispatch edition → **live independently reviewed guide** with adjacent disclosure after merchant approval → verified merchant settlement. Reader must also be able to reach the guide **without** joining the newsletter.

Source convention proposed pending reconciliation with Grok/Praxxis/Claude: `utm_source=youtube|tiktok`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `asset_id=<REAL_GROK_ASSET_ID>`. Note competing observed `mind_proposed_2026_11`: **neither is verified deployed; do not change live instrumentation**. Proposed issue 03 after permission: `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue03_zen12_guide`. These are offline proposed conventions, not live links.

**Measurement acceptance:** qualified unique human sessions after documented bot filtering → CTA engagement → independently authenticated and deduped eligible subscription → checkout paid order (if applicable) or merchant-reported settled affiliate conversion → fees/refunds → realized net revenue; report 7/30-day cohort dates and attribution completeness. **Never infer orders from clicks or monetize unverified merchant claims.** KPI: independently verified realized net revenue / verified qualified-human sessions × 1,000. Missing authentic session denominator, settled numerator, or linkable provenance = **NOT COMPUTABLE** rather than zero. No A/B success claim on tiny sample.

| Offer → funnel step | Blocker | Required no-send experiment/change | Proof | Owner |
|---|---|---|---|---|
| Zen12 → buyer guide → merchant | No FV partner acceptance, email-permitted earning URL, live vetted guide | Authenticate account terms, specific checkout variant and published guide | HOLD_MERCHANT | Mind/Affiliate |
| Focus → confirmed lead | 3/3/2 diagnostics vs follower status; consent/eligibility unknown | Provider read-only eligibility and consent reconciliation | UNKNOWN | Claude/Focus |
| Dispatch → inbox | Publisher postal, unsubscribe and real MIME untested | Native no-send editor preview; later separately authorized received-email inspection | HOLD | Dispatch |
| Grok → Focus | Actual published asset IDs and campaign mapping unverified | Reconcile existing analytics; do not add duplicate scripts | INCOMPLETE | Grok/Praxxis/Claude |
| Merchant → net revenue | No settled affiliate statement, order/refund/fees match | Verify transaction and commission from independent statement | NOT COMPUTABLE | Commerce |

## Reproducible synthetic tests and release gate

Run `python -I -m unittest discover -s dispatch/r282 -v` with no network. Tests cover eligibility, preverified accounts, dedup, misleading clicks, synthetic settled commission, malformed amounts, URL and PII rejection, and immutable hard-hold. A passing test **is not evidence of live eligibility, email delivery, legal compliance, affiliate authorization or sales**. Founder approval of exact creative, audience, schedule and channel remains mandatory. **NO EMAIL, NO WORDPRESS PUBLISH, NO SCHEDULING, NO SPEND, NO NEW LIST.**
