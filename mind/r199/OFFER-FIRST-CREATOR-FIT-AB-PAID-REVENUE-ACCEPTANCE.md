# R199 — One Authorized Offer, One Audience, One Verified Revenue Outcome

**Final Vestige Studios · Mind & Perception only · November 7, 2026 · UNPUBLISHED governance and conversion plan**  
**Source of truth:** [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [revenue charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).  
**Isolated branch:** mind-r199-wandering-mind-purchase-gates-20261107, stacked on R198, not on homepage PR #49 or Mind hub PR #172.

## Decision 1: an offer someone can actually buy

**Highest-fit audience:** A reader already contemplating paid structured meditation audio because they struggle to maintain a practice, not a casual viewer of a cognitive illusion. The person has an *evaluation question*, not a demonstrated clinical need: Is a professionally packaged twelve-minute library worth paying for instead of a free guided session or timer?

**Conditional merchant:** Zen12 Premium. Official seller page https://zen12.com/hnp consulted November 7, 2026 describes 12 levels and 48 MP3 recordings in four formats, twelve-minute sessions, manuals/support and a one-year advertised guarantee; the page showed a promotional Premium figure of **$87.99** that is **seller-displayed only**. No checkout was opened or completed, no taxes/fees or refund practice verified, and no product was listened to. Claimed equivalence of twelve minutes to an hour of meditation and all physiological/psychological benefits are excluded, not softened into implication.

**Affiliate program:** https://affiliates.inspire3.com/ publicly describes signup and special links; this does *not* establish Final Vestige publisher acceptance, channels, creative rights, specific link, order matching or actual commissions. Targeted mailbox searches surfaced promotion rather than authorization evidence. The prospective CTA stays a natively **disabled** button and has no href, click handler or outbound affiliate URL. The claim register maintains 28 open gates. No public commission percentage or seller EPC estimate is applied to an FV business forecast.

**Owned fallback:** The business charter notes existing Products 001–015/Payhip, but no authenticated SKU that is simultaneously (a) Mind-relevant, (b) rights-cleared, (c) currently purchasable, (d) correctly priced and delivered, and (e) verified for refund/payment reporting has been established. Do not pretend an owned offer exists or build a new product as a substitute for validation. Owner: Commerce/Founder to verify inventory. Only then create an alternate purchase pilot.

## Decision 2: connect three editorial topics without forcing a sales pitch

| Proposed creator asset (NO ID assigned) | Evidence-based hook, editorial destination | Reader's next useful action | Commercial fit / policy |
|---|---|---|---|
| Mind-wandering / a paragraph you cannot recall | An everyday reading-miss illustration → original [R199 mind-wandering manuscript](the-thought-that-left-the-room-MIND-WANDERING-INVESTIGATION-UNPUBLISHED.md) (NOT LIVE) | Optional existing [Focus Fieldbook](https://finalvestige.com/focus/); browse an independent audio comparison if reader chooses | **Highest fit hypothesis** for a reader actively considering a structured routine; Zen12 only after partner/release verification |
| Binaural beats / the tone that neither ear hears | 200/210 Hz conceptual sound → R198 [binaural evidence](../r198/the-beat-between-two-ears-BINAURAL-EVIDENCE-INVESTIGATION-UNPUBLISHED.md) (NOT LIVE) | Understand percept vs EEG vs outcomes; optional free observation | **Conditional** buying-guide fit; do not imply sound entrains the brain or sells results |
| Change blindness / did that object move? | Published [Change Blindness](https://finalvestige.com/2026/11/02/change-blindness/) | Read experiment, optionally Focus | **No immediate commercial recommendation**; prioritize trust, not shoehorned upsell |

Grok retains hooks, voice, media and publishing. Praxxis reviews/coordinates through the existing [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) and dated [handoff](https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit). The immutable published `asset_id`, platform, real social post URL, canonical live article, destination CTA location and approved `utm_campaign` remain **UNVERIFIED**. Do not insert placeholders that look like actual deployed IDs.

## Decision 3: editorial warm-up + commerce remains clearly separate

**Pilot offer-guide:** [Text variant A](zen12-offer-guide-A-TEXT-UNPUBLISHED.html), [text plus optional visual/storyboard B](zen12-offer-guide-B-OPTIONAL-FILM-UNPUBLISHED.html). Both use identical substantive purchasing information. The sole intended B addition is a **42-second original video concept**, currently a static SVG poster, a timed full-text transcript/caption proposal in an expandable details element, and a production checklist. No playable film is claimed.

**Problem → insight:** A reader finishes a page but cannot remember it. An attention-training study recorded selected task performance after ~5h/day for three months; that is not evidence that twelve minutes of a marketed recording equals one hour of advanced meditation.

**Free demonstration:** Twelve-minute observation with fixed, modest task and notes; this is a user preference diary, not a blinded clinical trial. This lowers the price of investigation and gives the user a meaningful reason to trust FV.

**Product value:** If one chooses to purchase, the legitimate value under review is **packaging**: 12 levels, 48 files, different audio styles, instructions and an advertised guarantee. Do not call efficacy settled, a medical treatment, or a sure productivity upgrade.

**Objections visible before CTA:** Scientific equivalence not established; no product-specific cure/attention evidence; seller-displayed $87.99 price not confirmed at checkout; no authenticated refund; free practice exists. Place the explanation of prospective commission immediately beside the disabled control. Do not assert a checkout has been initiated.

**Adjacent disclosure copy:** “If you purchase through a future clearly identified earning link, Final Vestige may earn a commission at no additional cost to you. Final Vestige has not verified partner acceptance or activated an earning link.” Upon any eventual launch, update to clear present-tense language and verify layout and link proximity at all breakpoints.

## Controlled A/B: a hypothesis, not a conversion result

- **Variant A:** Evidence-and-features text only; informative page, native disabled merchant control.
- **Variant B:** Identical body plus the original optional 42s video, once rights-cleared rendered assets and captions are approved. Initial storyboard is NOT rendered film.
- **Counterfactual:** Does reader-initiated visual storytelling increase *confirmed paid order rate* and **realized net revenue per 1,000 qualified-human sessions** without harming trust, accessibility, privacy or page performance?
- **Hold factors constant:** Article, CTA placement/wording, disclosure, source links, seller claims, mobile layout, consent and external merchant destination. Use server-side stable bucketing only if existing authorized infrastructure supports it; do not introduce a new fingerprint, cookie or analytics vendor.
- **Stop/go:** No test while approval/link, film, real-browser QA or verified merchant order reporting is missing. Once authorized, pre-register sample criteria, guard against social campaigns sending different-quality traffic to A/B, run 7-day and 30-day cohorts, and flag small samples. No p-values or winning variant from a handful of clicks.
- **Acceptance:** Funnel report separates views from consent-respecting qualified-human sessions and records completed paid orders, refunds, fees and received commission. If seller reporting cannot reconcile orders to campaigns, state attribution unknown.

## Minimal privacy-safe data contract for future approved integration

No new script or vendor in this branch. Claude/site analytics owns integration reuse.

| Event | Required permitted fields (no PII) | What it proves | What it does NOT prove |
|---|---|---|---|
| `campaign_landing` | coarse platform, `utm_medium=organic_social`, approved `utm_campaign`, immutable asset_id in `utm_content`, landing canonical, 7/30-day cohort, bot/consent classification | Candidate qualified session after dedup and bot filtering | Sale, unique human from a pageview alone |
| `article_to_focus_click` | campaign bucket, target `/focus/`, timestamp bucket | Navigational interest | Subscriber |
| `confirmed_signup` | authoritative Jetpack status only; aggregate cohort, no raw email | Confirmed opt-in, only if correctly observable and consented | Purchase |
| `guide_to_merchant_click` | campaign ID, guide variant, approval-gated product ID, no PII | Outbound CTA interest | Checkout or paid affiliate sale |
| `merchant_confirmed_purchase` | independent provider-reported order ID stored hashed or aggregated, amount/currency/status, attribution confidence | Confirmed paid transaction after merchant verification | Net income until fees/refunds/settlement |
| `merchant_refund_or_reversal` | same aggregated order cohort, amount and date | Correction to revenue | New sale |

Referrer/Utm must not carry emails, names, IPs, medical histories, persistent device fingerprint or private account ids. No tracking added by this sprint. Marketing link placement and attribution must respect consent and platform policies. Preserve the single Jetpack/Dispatch Focus welcome. As observed in the current Focus funnel, a visible fieldbook download is **not** evidence of a confirmed email opt-in; use authoritative Jetpack confirmation, not a page query string.

### Commercial decision formula

For each 7- and 30-day qualified-human cohort, where authoritative reporting exists:

```
realized_net = received_eligible_commissions + settled_owned_product_receipts
               - refunds - chargebacks - payment_processor_fees - allocable_variable_costs
net_revenue_per_1000_qualified_humans = (realized_net / verified_qualified_human_sessions) * 1000
paid_conversion_rate = merchant_verified_paid_orders / qualified_human_sessions
lead_to_customer = reconciled_paid_customers_from_confirmed_leads / confirmed_leads
```

If numerator/denominator/reconciliation missing, report **NOT COMPUTABLE**, not zero. Do not confuse merchant gross GMV with revenue to FV. Identify costs and cohort attribution confidence.

## Offer → step → blocker → controlled change → evidence → owner

| Priority | Offer / funnel step | Blocker | Change or experiment | Pass/fail acceptance evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → earning link | FV publisher approval absent | Confirm account-specific authorization, permitted site/social/email channels and earning link | Authenticated signed partner terms, link and channel approvals; otherwise HARD HOLD | Founder / Mind |
| P0 | FV Payhip owned alternate → purchase | No verified eligible Mind SKU | Read-only actual SKU/rights/checkout/fulfillment review | Documented active listing, rights manifest, checkout terms, delivery and refunds | Commerce |
| P0 | Focus → confirmed subscriber | Frontend PDF/download visibility can falsely imply opt-in | Claude/QA inspect server-side Jetpack list and consent-safe welcome delivery | Real authoritative confirmation, not arbitrary client state | Claude / Site QA |
| P0 | Any offer → paid conversion | Orders, commissions, refunds, fees unverified | Reconcile merchant report with consented campaign cohorts | Paid, settled orders and net-revenue ledger | Commerce / Analytics |
| P1 | Grok asset → article | No verified published immutable asset IDs | Praxxis/Grok reconcile TASK-008 without changing queue | Actual asset_id, URL, approved landing and context | Grok / Praxxis |
| P1 | Text A vs optional film B | Rights, film, browser and CTA gates open | Build original 42s only after approval; accessibility and low-cost media | Captions+transcript, no forced playback, low CWV cost, reviewed disclosure | Mind / Site QA / Homepage art |
| P2 | Hub → navigation | Unpublished /mind/ archive | Review four-stream hub against existing published routes; never write live nav | 360/390/768/1440/1920 browser proofs after QA and founder signoff | Mind / Homepage art / Claude |

## Scope and handoff

Mind #171 owns source work, conversion eligibility, presell guide and QA evidence. Dispatch #174 owns newsletter copy and its current Jetpack welcome. Homepage #150 owns visual integration. Site QA #126 verifies accessibility, trust, security, source claims. Claude owns production engineering and existing analytics infrastructure. Grok owns social assets and publishing. Founder owns spending and production release.

**Release decision remains HARD HOLD.** This branch changes only isolated Mind draft files and narrow prior Mind scientific corrections. No WordPress, navigation, email, subscriber, promotion, live merchant link, paid platform, checkout, tracking script, merge or deployment action is authorized. Do not confuse the new source-level artifacts with a live experiment.
