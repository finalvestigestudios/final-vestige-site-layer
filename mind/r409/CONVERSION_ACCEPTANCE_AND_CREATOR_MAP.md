# Mind R409: Commerce proof, creator–article crosswalk, and conversion acceptance
**2026-11-15 | Source-only, unpublished | Release: HARD HOLD | Owners: Mind / Commerce / Praxxis–Grok / Claude / Dispatch / QA / Founder.**

## Decision before design: which offer can actually be paid for?

- **Zen12:** a real public merchant SKU exists, but *Final Vestige* named affiliate acceptance, permitted web/social/email channels, issued per-SKU earning URL, actual referred checkout, return applicability, and payout evidence **remain unauthenticated**. The public affiliate-program page and marketing emails are not an approval letter. Therefore the merchant purchase CTA is native-disabled, no commission is claimed, and no live experiment can yet be scored on paid revenue.
- **FV-owned digital Mind offer:** WordPress read-only inventory showed ordinary posts/pages/forms, no WooCommerce product post type, and search of live content for “payhip” returned no results. This does **not** prove an owned paid SKU does not exist in a separate store. It does mean no actual, verified payable/rights-cleared Mind SKU was authenticated. Do not invent or redirect to one. The existing **52-page Seven Day Focus Fieldbook is free**, not a paid order. Founder/Commerce should inspect existing product IDs, current merchant checkout, IP rights, fulfillment/delivery, VAT/sales tax, refund policy, settlement and payout before adopting any owned product.
- **Hypnosis Live Total Focus:** actual SKU describes a 33-minute 47 MB recording, but public displayed price moved (latest 2026-11-15 observation $24.44 against $29.95), so eliminate fixed-price presell claims without direct authorized referred checkout. Email rights remain specifically unverified.
- **Brainwave Shots Focus Shot:** official FAQ describes *isochronic* audio; do not substitute evidence from *binaural* studies. The product page is the source for seller-described 15/30-minute format. No authorized earning URL.

## Prioritized OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL EVIDENCE → OWNER

| P | Offer → funnel | Blocker | Proposed change / controlled test | Pass criterion | Owner and current decision |
|---|---|---|---|---|---|
| P0 | Zen12 → legitimate affiliate sale | No authenticated named affiliate acceptance or earning URL | Request internal verified account documents and exact SKU/channel approval. Compare standard vs coupon seller checkout, terms and settlement reports *before any promotion*. | Dated written program/account acceptance naming FV, authorized site/social/email lanes, issued exact URL and permitted creative/claims, associated merchant test checkout and refund policy | Founder/Commerce — **HOLD** |
| P0 | FV-owned Mind resource → paid order | No verified paid rights-cleared SKU | Audit existing Payhip/product records, secure merchant checkout, delivery and refund rights; choose a *pre-existing payable* SKU only | Authenticated product ID, item rights, final order price/terms, deliverable fulfillment, evidence of independently confirmed order | Commerce/Claude — **HOLD** |
| P1 | Grok asset → landing article | Real immutable social media IDs and intended URLs unverified | Praxxis request inventory/rights/primary CTA from Grok via existing TASK-008; do not replace content pipeline | Three actually published media URLs, original asset IDs, sourced hooks, rights and mobile landing-page QA | Praxxis/Grok — **HOLD** |
| P1 | Article → Focus lead | Provider confirmation/welcome delivery not tested | Keep exactly existing Jetpack Focus funnel; consent-based test confirmed signup/delivery without adding a form | Provider-confirmed consented subscription and delivery, deduplicated lead ID (no PII in analytics) | Claude/Dispatch/QA — **HOLD** |
| P1 | Zen12 A/B → merchant order | No merchant authorization, and playback/server QA incomplete | Source-controlled identical text buyer guide A vs same guide B with optional original 42s **silent** video. Randomize only after authorized live merchant offer and founder approval. | Browser 360/390/768/1440/1920, WCAG keyboard/reduced-motion/no-JS, same seller copy, equal CTA position/disclosure, performant playable media and real confirmed orders | Mind/QA/Claude — **HOLD** |
| P0 | Settled order → net revenue | No transaction, refunds/fees, qualified-human denominator | Reconcile source-of-truth affiliate partner reports or payment processor order with eligibility, refunds and fees | Verified payment ID or settlement report, timestamp, non-duplicative attribution, fee/refund ledger | Commerce/Claude — **NOT COMPUTABLE** |

### Three *proposed* creator-topic → landing article → free resource → optional eligible offer pathways

These are suggested routing hypotheses; **not three verified Grok videos**. Asset IDs, captions, rights, published links and clicks must be supplied by Grok/Praxxis TASK-008 before creating real campaign URLs.

| Creator topic / evidence-based hook | Article destination | Optional Focus/Dispatch transition | Offer fit and necessary warning |
|---|---|---|---|
| **Change blindness:** “The stranger at the door: why didn't observers notice?” | Existing live https://finalvestige.com/2026/11/02/change-blindness/ | Free https://finalvestige.com/focus/ + existing Dispatch only upon confirmed consent | Only a cautious optional *independent* Zen12 buyer guide. Experiment does NOT verify Zen12 results. |
| **Mesmer / Puységur history:** “What did the archive actually record about magnetism?” | Existing historical primary-source collection https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Existing Focus Fieldbook if desired; no newsletter re-enrollment | Optional independent Total Focus format guide only if approved; historical hypnosis is not proof of product efficacy. |
| **Attentional blink / the second target:** “What happens when a second event arrives too soon?” | Canonical *already-live* Mind/perception attention article to be verified by Site QA; do not invent a new public slug | Existing Focus route, no forced signup | Optional Zen12 comparison only if it helps reader understand audio-format purchasing; Slagter intensive training results are not Zen12 trials. |

The third mapping deliberately stays **UNRESOLVED** until the actual canonical live article and creator asset ID are verified. If no appropriate live third destination exists, do not schedule the creator link or invent a route. The 42s optional film is an original **FV site-side buyer education element**, not a replacement for Grok-made social videos.

### A/B hypothesis and assignment protocol

**Hypothesis (not an outcome claim):** Giving a high-intent buyer an original silent 42-second evidence explainer, with transcript, might improve *qualified understanding* and eventually verified paid-order rate versus otherwise identical text; it might instead distract, increase load time or decrease checkout rate. The only primary commercial outcome is **net realized revenue per 1,000 qualified-human landing sessions** (not video plays, clicks, downloads or provisional leads).

- A: same substantial HTML buyer guide, no video; B: identical substantial guide plus optional film. Same primary disclosure, CTA text and disabled status in this draft. All buyer text after media is byte-identical in source-controlled files.
- Randomize one consenting/eligible session or stable privacy-safe first-party cohort to A/B using Claude's existing analytics mechanism; no new cookie/banner, arbitrary client fingerprinting or extra GA4 script. Preserve assignment only as allowed by site consent policy. Protect against bots/auto-opens and repeat reload inflation; publish test counts separately with sample-size caveats.
- Keep B `preload="none"`, `controls`, `playsinline`, an original same-origin MP4, original poster, full independent visible transcript and six caption cues. No forced playback, third-party video host, audio, strobe, animation effect or JS needed.
- Test a **non-inferiority** threshold on verified paid purchases only after substantive eligible traffic exists; do not call a winner on small sample/zero transactions. Secondary: relevant CTA click, confirmed Focus lead, qualified engaged sessions, browser WCAG/Core Web Vitals, no-JS experience.
- Do not deploy A/B or render actual partner link without written founder release authorization, approved partner permissions and verified URL/terms.

### Measurement contract (Claude owns implementation; do not install a second script)

`asset_id` (actual Grok immutable ID, never invented) and `utm_source` (platform), `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<asset_id>` must map to a *verified canonical page* with normal platform URL policies. For TikTok non-clickable captions, record whether the route is a profile link or bio rather than pretending caption links work.

Events and independently identifiable meanings:
1. `qualified_human_session`: filtered bot/owner activity, qualifying event, 7/30-day cohort, visitor counted using the **existing** consent-compliant first-party system.
2. `landing_view`: verified loaded canonical article, source and campaign fields. Views do not represent people automatically.
3. `relevant_cta_click`: event from the specific named placement, not a payment.
4. `focus_confirmed_lead`: confirmed by the actual Jetpack provider, with only aggregate or opaque privacy-safe IDs in analytics. Do not export email/name.
5. `affiliate_click`: only after verified partner approval and outgoing URL activation, not a commission.
6. `paid_order_verified` / `affiliate_commission_verified`: independently confirmed order or partner financial report; separate duplicate reconciliation and returns.
7. `refund_verified`, `fee_verified`, `net_revenue_realized`: settled financial movements, with pending/void excluded.

Formula, for each 7-day and 30-day **qualified** cohort, evaluated only with actual ledger inputs:

`net_revenue_per_1k = 1000 * (sum(settled gross FV-order revenue + settled affiliate commissions - eligible refunds - fees - chargebacks)) / qualified_human_sessions`.

If the denominator is unavailable or sales cannot be independently reconciled, report **NOT COMPUTABLE**, not zero. On very small samples present counts and uncertainty, not “winning conversion” narratives. Where attribution cannot be reconciled between merchant and site, report unattributed revenue separately and do not assign it to a Grok asset.

### Privacy/security/disclosure test matrix (unexecuted acceptance until QA)

- [ ] Native disabled purchase control blocks keyboard and pointer; no `href`, client script, dynamic URL, cloaked redirect or tracking vendor on draft.
- [ ] Affiliate disclosure visibly adjacent to precise commercial CTA in every view; readers are not promised no additional cost unless documented for authorized checkout.
- [ ] Distinguish seller descriptions/price snapshot from independently demonstrated findings; disallow claims of tested product, guaranteed health, finances, memory, immediate focus.
- [ ] A and B reproduce exact same core `<article>` and seller limitations/disclosure. B transcript and captions represent exact on-screen material, 0–42 seconds with no gaps.
- [ ] Silent video is actually playable from same-origin deployed path, MP4 content-type; reload and no-JS work; poster fallback and transcript readable with network disabled.
- [ ] Test mobile 360, 390, 768, 1440, 1920; keyboard, zoom 200%, contrast, reduced-motion, WCAG 2.2 AA, meaningful headings, no horizontal scroll, video captions, autoplay absent.
- [ ] Correct source links and archive/Focus routes; verify exact independent third canonical article and **real Grok media IDs**.
- [ ] No new signup form, recipient sync, marketing mailing, Jetpack welcome replacement, analytics script, cookie or paid service.
- [ ] Paid conversion actually recorded in merchant/processor report, not guessed from affiliate clicks.
- [ ] Founder/Commerce approval recorded; QA and homepage/Dispatch owners sign off before any live write.

### Active ownership, canonical handoffs

- Mind Issue #171: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- Cross-site conversion Issue #820 and charter #818: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818
- Site QA #126, homepage art #150, Dispatch #174; preserve flagship homepage PR #49 and canonical Mind PR #172.
- Grok via Praxxis TASK-008: https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit ; dated handoff https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit. Do **not** edit creator scripts, content queue, shared task board, newsletter issues or site CMS.

### Commercial stop condition

**HARD HOLD**: No trusted named Inspire3 approval, no authorized tracking URL, no verified paid FV-owned Mind product, and no independently reported settled sale. Neither a prior PR count nor 42-second film output is a commercial conversion.
