# R396 — Product identity drift in the original six-issue Dispatch pilot

**Status:** SOURCE-ONLY / UNSENT / editorial decision required. Primary sources: [canonical pilot PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [current full preview PR #2703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2703), [Mind issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Dispatch issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Read 2026-11-16 07:03Z. Not authorization.

## Specific new finding and necessary correction

**The founder-approved draft allocation is not "Zen12 + Total Focus".** It is **Zen12 (Issue 03)** and **Hypnosis Live (Issue 05)**. The canonical `manifest.json` names the unchanged, disabled Issue 05 destination `[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]`; the canonical original Issue 05 says "A program under review: Hypnosis Live." Later optional R391 content centered on **Total Focus**. Total Focus is indeed a specific MP3 *within* Hypnosis Live's Mental Skills catalog, but a SKU-specific focus guide is a narrower offer than the campaign's existing broad catalog. This is a **product-scope-change proposal, NOT a discovered false product relationship**, and it cannot silently replace an original issue. No published approved buyer guide exists for either proposed destination.

| Scope | Canonical Issue | Exact source | What is supported | Still not verified |
|---|---|---|---|---|
| Zen12 meditation | 03 | [Zen12 official About](https://zen12.com/about) | Seller says 12 levels, four formats, 12-minute sessions | Named FV account approval, EMAIL-channel rights, exact licensed link, referred price and refund, independent equivalence/brainwave proof |
| Hypnosis Live collection | 05 | [Hypnosis Live official catalog](https://hypnosislive.com/catalog), [FAQ](https://hypnosislive.com/faq) | Seller operates a collection of self-hypnosis MP3s; FAQs say session tracks are bought as downloads | Named FV exact-channel/catalog marketing rights, issued earning URL and eligible buyer-guide destination |
| Total Focus particular recording | OPTIONAL narrower version of 05, **NOT canonical** | [Official Total Focus detail](https://hypnosislive.com/mental-skills/total-focus) | Within Hypnosis Live catalog; seller lists 33 minutes, 47 MB and Julie-Ann Amos | Founder approval to narrow Issue 05; product-specific permission; checkout eligibility; actual purchase or independently established efficacy |

### Commercial-copy boundaries

* The official Total Focus page currently shows a retail/cart price and multi-item promotional offers. Earlier indexed snapshots presented different prices. Neither display is a verified FV affiliate checkout, so **include NO price** in unsent campaign copy until the owner reconciles exact linked purchase terms. Never transplant a two-product bundle price into a one-audio recommendation.
* Hypnosis Live's FAQ says most recordings last about 40 minutes and that they are MP3 downloads; the specific Total Focus page says **33 minutes**, so use the product detail for that SKU, not an average catalog-duration claim.
* Hypnosis Live's FAQ mentions an approximately 14-day refund and a limit on how many recordings may be returned in a year. Those are seller-originated current-page terms, not approved FV checkout entitlements. Inspect actual merchant policy and founder-authorized referred flow when ready. No refunds promised in editorial copy.
* The merchant says its audio may "reprogram" the mind or deliver extraordinary focus. These are **seller claims**, not scientifically proven Total Focus outcomes. Avoid reproducing testimonials or performance guarantees.
* Public [Limitless Labs](https://inspire3.com/ll/) email swipe materials concern a different Inspire3 product and even that page explicitly calls for promotion approval. This does **not** grant Zen12 or Hypnosis Live EMAIL permission, an issued earning URL, or a Final Vestige partner account.

### Decision rule

Until founder chooses either **retain broad Hypnosis Live Issue 05** or **explicitly approve narrowing to Total Focus**, do not move optional R391 content into the canonical six. If narrower: Mind & Affiliate Studio must deliver a SKU-specific independently sourced comparison guide, a named permission record covering **email**, an issued commission-earning link, explicit creative rights and live merchant checkouts before CTA activation. Then Dispatch and founder independently review final email disclosure and footer. The original allocation remains **4 editorial + 2 commercial-review-pending**, all HARD HOLD.

This is the intended purpose of `offer_scope_gate.mjs`: programmatically surface product-family drift and fail closed on a child-SKU narrowing without a separate founder evidence ref. A test fixture with all proofs true can at most become `review_ready`, never `send_enabled`.
