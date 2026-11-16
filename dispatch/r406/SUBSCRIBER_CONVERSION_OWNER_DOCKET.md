# Dispatch R406 — total-focus conversion and consent docket

**All changes draft-only. Master Issue #174, campaign PR #175 and guard PR #201 remain unchanged; separate from homepage PR #49.** Partner presell owner is Mind & Affiliate Studio (#171), site/analytics implementation owner is Claude, social acquisition owner is Grok with Praxxis review, founder owns all public release.

## Material finding: seller FAQ qualifies the guarantee
The official [Total Focus sales page](https://hypnosislive.com/mental-skills/total-focus) presents a fourteen-day satisfaction promise, a 33-minute MP3, and a $24.44 individual price with $29.95 reference and $19.95 per-item bundle display, observed November 16. The official [FAQ](https://hypnosislive.com/faq) adds a maximum **five refunded sessions per year**, plus another general price ($22.95 typical session). A FAQ cap qualifies the broader prominent reassurance; differing presentations are not proof of wrongdoing. The correct copy decision is to **omit price, refund promises and seller efficacy guarantees** from the draft email until the exact authorized FV referral checkout is verified.

The official [public affiliate portal](https://affiliates.inspire3.com/) advertises special affiliate links and generalized commission terms. That is not finalvestigestudios-specific acceptance, authorization for commercial EMAIL or an issued Total Focus earning link. Scientific [APA definition](https://www.apadivisions.org/division-30/about/index) and [NCCIH clinical review](https://www.nccih.nih.gov/health/hypnosis) are not product-specific efficacy tests. FTC advertising [substantiation rules](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance) constrain any implied effect.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → PASS/FAIL EVIDENCE → OWNER

| Offer | Step | Blocker | Proposed change | Acceptance status | Owner |
|---|---|---|---|---|---|
| Total Focus | Email 05 → warm-up guide | Named FV EMAIL permission and vetted guide unavailable | One visibly disabled guide CTA, near-link commercial disclosure | HOLD; partner-issued earning URL + consent + exact guide needed | Mind / Commerce |
| Total Focus | Warm-up → checkout | Conflicting sales/FAQ price and qualified refund details | Date-stamped exact referred checkout and policy, independent claim review | HOLD; public pages are not FV referral terms | Mind / Commerce |
| Free Fieldbook | Reader → confirmed signup | WordPress total3/confirmed3/unconfirmed2 overlap; deliverable audience unknown | Provider-authoritative dedup `confirmed_signup_v1` once per recipient; never infer from `?subscribe=` | HOLD; user-level consent proof required privately | Claude / Focus |
| Dispatch | Confirmed recipient → delivered welcome | Welcome setting is present, inbox arrival not evidenced | Authorized recipient-side witness only; no unapproved test email | HOLD; setting does not prove receipt | Focus / Founder |
| Dispatch | Preview → compliant commercial email | Publisher address, true Jetpack preview, operational opt-out unverified | Native non-sending WordPress Preview with documented subject/preheader/footer, then independent opt-out receipt | HOLD; offline HTML does not satisfy this | Dispatch / Founder |
| Grok → Focus → Dispatch | Qualified visit → paid settlement | Real asset ID, human sessions, merchant settlements unknown | Existing UTMs, consent dedup, independently reconciled orders and refund/fee records by 7/30-day cohort | HOLD; net / 1000 humans NOT COMPUTABLE | Grok / Praxxis / Claude |

## Event and UTM contract, proposed but NOT deployed
Use only actual published Grok `asset_id`, `utm_source`, `utm_campaign`; retain existing first-party tooling, not a duplicate script. Only provider-confirmed opt-in creates `confirmed_signup_v1`, deduplicated per platform identity and not storing raw email in analytics. An email CTA to a later verified guide may use `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026&utm_content=issue05_total_focus_guide`, with no tracking code added before publisher/engineering review. A guide click, add-to-cart and pending checkout are NOT sales. Only independently reported **settled** orders and refunds/fees contribute to net revenue. Without an audited unique qualified-human session denominator, the KPI is **not computable**, never presumed zero.

## Release controls
All canonical six stay `HOLD_UNSENT`; commercial 03/05 `HOLD_MERCHANT`, editorial 04 `HOLD_COPY`. Do not adopt this alternative without editorial approval. No post, test email, dispatch, subscriber contact, settings change, affiliate activation, merge, paid service or published social content is authorized.

Review sources: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), [prior #2771](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2771).
