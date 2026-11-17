# Dispatch R417 — merchant offer-context divergence (DRAFT / NO SEND)

**Scope:** Owner [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); [revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Canonical six-issue draft [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), per-issue QA [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) and last Dispatch draft [#2833](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2833). This is additive source QA; no new campaign, substituted copy, first-party page, sent email or affiliate activation. 4 editorial + 2 commercial slots remain unchanged.

## Conversion-critical issue: an advertised price is not the referred offer

Quoting one public price while the reader lands on a different package, coupon or bundle creates direct checkout friction and damages trust. The merchant pages below are **seller-controlled observations as of November 17, 2026 UTC**, not live FV account disclosures, an account-issued earning URL, verified checkout or independent efficacy evidence.

### Issue 03 — Zen12

- [Official Zen12 main sales page](https://zen12.com/) advertises 12 levels, four listening styles per level, distinct Beginner/Premium/Advanced packages. It displayed Beginner and Advanced at $67.77 and Premium at $87.99 at review; these are separate packages and may change. Seller asserts 12 minutes corresponds to an hour of meditation. No independent Zen12-specific substantiation was authenticated.
- [Distinct official promotional landing page](https://zen12.com/secret/) displayed a $37 coupon offer with its own video/sales framing. Whether it reaches an FV visitor on the verified earning path is **unknown**. Never imply the reader qualifies for that price, a limited-time sale or the seller's efficacy promise.
- **Status:** first-party guide NULL, final selected package NULL, named FV affiliate acceptance NULL, product-specific permission to promote via email NULL, earning link NULL, referred checkout NULL, settlement NULL. Issue03 = HOLD_MERCHANT. Mind & Affiliate Studio owns the actual authorized guide and rights; Dispatch owns email claims and near-offer disclosure after partner proof.

### Issue 05 — Hypnosis Live Total Focus

- [Official Total Focus product page](https://hypnosislive.com/mental-skills/total-focus) describes one **33-minute, 47-MB** MP3, publicly displaying **$24.44** for the single item at this inspection, plus a different two-product bundle priced separately. Cached or different-visit contexts have displayed different public prices. These observations **do not establish why or when a price changed**, much less the approved referred checkout.
- [Official Hypnosis Live FAQ](https://hypnosislive.com/faq) says refund requests are within **14 days**, subject to a maximum of **five refunded sessions per year**. The broader promotional guarantee on a product page must not suppress the qualifying FAQ terms; checkout still needs a current firsthand review.
- Seller claims such as 100% concentration, brain reprogramming or guaranteed productivity are not independent clinical evidence. **Status:** distinct guide, earned URL, specific email permission and exact checkout remain unverified. Issue05 = HOLD_MERCHANT.

### Public affiliate page is not a private authorization

The [Inspire3 affiliate landing page](https://affiliates.inspire3.com/) describes special links and general payouts. That is neither confirmation of an FV account nor named Zen12/Total Focus email rights or an issued URL. Do not apply another product's affiliate creative or general program claims to these two slots. Do not quote any merchant commission or EPC as an FV realized earning.

## Subscriber-to-customer acceptance

Read-only Jetpack newsletter status/settings captured November 17, 2026 at **06:33 UTC**: newsletter enabled; post email default **OFF**; format FULL; sender Final Vestige Studios, no-reply; recent five published post notifications **never_sent_opted_out**; subscriber diagnostics 3 total / 3 confirmed / 2 unconfirmed. Separate follower metric: 3 WordPress.com Reader / 0 direct-email followers. These categories are not additive; *eligible unique inboxes unknown*. Welcome message contains the 52-page Fieldbook URL, but its actual receipt, functional opt-out, native Jetpack preview and FV's own postal address **remain unverified**. The merchant's London address does not satisfy FV's sender address requirement.

FTC rules for commercial messages demand truthful headers/subjects, unmistakable promotional character where relevant, an actual valid **FV physical mailing address** and a clear **operational opt-out**: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Hybrid educational + promotional messages require primary-purpose analysis, not an assumption that they are purely editorial. No native preview, email delivery or physical address was witnessed in this run.

## OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer / step | Highest-impact blocker | Verification or experiment | Evidence / result | Owner |
|---|---|---|---|---|
| Zen12 / vetted guide → paid order | Package price vs separate coupon route, missing EMAIL rights and earning URL | Record a named FV authorization, exact approved SKU, guide, referred checkout and independent commission settlement | Public sellers inspected; private proofs NULL / **HOLD** | Mind / Commerce |
| Total Focus / buyer guide → paid order | Single MP3 vs bundle, refund qualifier, missing EMAIL rights | Review the exact referred checkout, 14-day/5-per-year terms, first-party guide and issuer link | Public terms inspected; actual checkout NULL / **HOLD** | Mind / Commerce |
| Fieldbook → qualified Dispatch lead | Overlapping WordPress totals, no recipient/receipt witness | Provider ID dedup, confirmation and suppression, safely authorized welcome receipt check | 3 / 3 / 2 vs Reader3/email0; distinct inboxes UNKNOWN | Focus / Claude |
| Dispatch → lawful inbox | No native Preview, FV address or unsubscribe witness | Founder-approved non-sending native Preview and separate authorized opt-out evidence | **FAIL / HOLD**, no test sends | Dispatch / Founder |
| Grok asset → human session → realized net revenue | No authenticated campaign-session denominator or settled orders | Use existing Claude UTM/asset_id attribution, dedupe, independently paid settlement after refunds/fees; 7/30-day cohorts | **NOT COMPUTABLE**; clicks are not sales | Grok / Praxxis / Claude |

## Measurement contract and founder decision

Propose one deduplicated `confirmed_signup` event only from authenticated provider confirmation **and** actual email eligibility, once per subscriber identity—not a success query, Reader follower or PDF click. Do not publish addresses/IDs. Only after approved guide URLs are live, use `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_pilot_2026_11` and `utm_content=issue03_zen12` or `issue05_total_focus` where native settings/links support them, preserving earlier Grok asset source in the existing Claude pipeline. A click, trial or referral order intent is not a paid order.

**KPI:** `1,000 × realized net revenue ÷ audited qualified-human sessions`, where net is actually settled gross less refunds, reversals and applicable fees. Return **not computable** when either audited denominator or paid outcomes are missing. No fabricated A/B results on a tiny list.

The founder's *draft* campaign authorization is not final send approval. Obtain individual acceptance of copy, guide, named commercial rights, actual reviewed email preview, audience, postal/unsubscribe and future schedule before any send or publication. Frozen homepage PR #49 untouched.
