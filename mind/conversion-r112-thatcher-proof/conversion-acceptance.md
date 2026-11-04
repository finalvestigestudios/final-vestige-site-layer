# R112 — Conversion-first release decision and Zen12 acceptance specification
**2026-11-03 PT | Private draft only | #171 Mind, #820 revenue and TASK-008 Grok/Praxxis**

## Decision
**HOLD paid Mind activation.** Fresh authenticated WordPress Collection page ID 78 (https://finalvestige.com/collection/) shows the 52-page Seven Day Focus Fieldbook as **free with the existing Dispatch subscription**; it does not show a paid Mind SKU. Previous descriptions of Payhip Products 001–015 cannot prove current rights, price, delivery or merchant-confirmed orders. Access to a merchant-authenticated Payhip ledger is still missing; this is a verification gap, **not proof that no paid product exists**.

Official Inspire3 catalog https://inspire3.com/ lists Zen12, Hypnosis Live and Brainwave Shots, but public pages and promotional emails **do not** establish Final Vestige affiliate acceptance. Targeted Gmail review of Inspire3/Zen12-related messages after August 2026 found marketing material and product receipts, **no qualifying written FV-specific affiliate acceptance**, permitted channels or tracking URL. Buyer-identifiers protection is also not proved. Do not activate links.

## Merchant and buyer fact pattern, independently rechecked
Official https://zen12.com/ describes 12-minute audio, four styles, 12 levels and Premium 48 MP3s. Exact https://zen12.com/getstarted checkout displayed **USD 87.99** before jurisdiction-dependent final sales taxes on November 3, 2026. This is a **dated observation**, not a future price quote, advertised verified discount, or final order confirmation. Do not copy its timer, testimonials or urgency into FV copy.

Seller terms linked by that checkout: https://inspire3.com/terms/?s=zen12 . Zen12 has a **seller-stated** one-year money-back guarantee; card refunds after 90 days are manually handled via PayPal. Seller says downloadable MP3/PDF files **may** include purchaser-identifying tags and provided phone numbers **may** lead to SMS offers. Those are policy statements, **not** independently verified refund performance or proof any download bears a tag. Seller privacy https://inspire3.com/privacy/ expressly permits sharing names, emails and purchased-product details with referring affiliates. Written aggregate-only/no-buyer-identifiers protections are a **P0 gate**.

Seller's “one hour of advanced meditation in twelve minutes” claim is not supported by the independent 2023 binaural-beat systematic review https://pubmed.ncbi.nlm.nih.gov/37205669/ . The 2007 meditation/attentional-blink experiment https://pubmed.ncbi.nlm.nih.gov/17488185/ used three months of intensive training, not Zen12. FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking says plainly disclose earning links beside recommendations, not only via footer or vague “affiliate” labeling; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance requires suitable support for objective psychological/health claims.

## ONE high-intent presell, canonical R110/R111 — no duplicate public guide
**Audience:** adults *actively comparing* a short guided/audio meditation routine with free alternatives. This is distinct from general curiosity about illusions or Puységur.

**Headline:** *Twelve minutes may fit your day. What does the evidence say it buys?*

**Original truthful opening:** “Twelve minutes is time you can imagine finding, even on a crowded day. It is not proof that a recording can recreate an hour of intensive meditation. Before spending anything, see what the seller includes, what independent studies tested and what the seller can do with your data.”

**Useful experience before any sale:** three free 12-minute sessions on separate days: quiet reflection, a freely available guided session and ambient sound. Record ease, willingness to repeat and preference; don't label subjective results neurological improvement or a treatment outcome. The buyer can **decline to buy**.

**Offer value/limitations:** Zen12 seller describes downloadable, organized 12-minute sound options and manuals. We have **not** tried the product, verified neurological results or independently confirmed buyer support. The exact seller conditions must be rechecked at publication. The buying guide is a separate editorial page, never a commercial conclusion to a scientific investigation.

**Current in-page CTA, intentionally unavailable:** “Zen12 referral unavailable pending partner authorization.” Render a real disabled button, no `href`, tracking code or checkout redirect. If approval arrives, draft link copy near this disclosure: “If you buy through this link, Final Vestige may earn a commission at no extra cost to you.” Any eventual actual link must be separately approved, use `rel="sponsored noopener noreferrer"`, and avoid collecting buyer identity. Existing https://finalvestige.com/focus/ remains a clearly labeled **free** optional resource; no duplicate Jetpack form or changes to its welcome message.

## A/B proof and controlled hypothesis
**Verified source-only parity this sprint:** On R111 ancestor, R110 `variant-a.html` has 10,868 characters; `variant-b-video-concept.html` has 12,785. Removing exactly **one** 1,917-character optional `aside` containing poster/transcript from B produces **byte-for-byte identical A source**. Each contains exactly one disabled commerce button, zero earning-link anchors. This is strong **source parity**, not a tested lift. The original 40-second R102 film exists offline; no hosted player/autoplay was added.

Only after eligible paid offer, founder approval, permitted tracking, and QA may a test compare A (text) against B (same text + optional short original video with captions, poster, transcript, no JS requirement). Before release, Site QA must check no-JS, keyboard, contrast, mobile 360/390/768/1440/1920, reduced motion, caption synchronization and CWV. Declare a winner only from merchant-reconciled paid outcomes with adequate 7/30-day cohorts; never from clicks or tiny samples.

## Three source-grounded Grok/Praxxis TASK-008 topic-fit candidates
| Topic | Editorial destination | Commercial status |
|---|---|---|
| Change blindness (“The scene changed while you watched”) | https://finalvestige.com/2026/11/02/change-blindness/ — recheck at post time | optional existing free Focus; no inferred product intent |
| Historical suggestion / Puységur (“What did the witnesses record?”) | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | research→optional Focus; no scientific proof of hypnosis audio |
| Thatcher illusion (“The pixels did not change”) | New R112 `thatcher-investigation.md`, **unpublished** | no creator destination until artwork rights + editorial release |

All corresponding actual Grok asset IDs, post URLs and rights/caption/bio-route proof remain **unknown**. Do not invent them, overwrite TASKS, post videos or claim attributable visits.

## Measurement, owner and pass/fail
Use Claude's existing #820 instruments if and only if approval permits—no new analytics provider or duplicate script. Requested standard fields: `utm_source=actual_platform`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=actual_grok_asset_id` when supported by a platform's route. No guesswork for lost bio-link attribution. No visitor IPs, email, full referrer, fingerprints, affiliate customer names or order IDs in campaign logs.

**Events must remain distinct:** qualified-human landing → source article → resource CTA → merchant-verifiable confirmed lead, if relevant → offer view → `affiliate_outbound_click` (NOT sale) → merchant-confirmed paid order/commission → refunds/fees → **realized net revenue per 1,000 qualified human sessions**, 7d/30d, with denominator and sample warnings. Until qualified denominators and source-reconciled orders both exist, metric = **NOT COMPUTABLE**, never substitute clicks or zero.

| Offer → step | Blocker | Change/experiment | Current evidence | Owner |
|---|---|---|---|---|
| Zen12 → earnings | Named acceptance, link, channels, no-PII terms missing | Review documentary partner rights; exact approved URL and aggregate-only reporting | **HOLD** | Founder/commerce; Mind audits |
| Owned FV Mind → checkout | Paid SKU, fulfillment, price, rights, refunds not verified | Merchant-authenticated Payhip listing and test delivery/settlement | **UNVERIFIED** | Claude/commerce |
| Grok → qualified landing | Asset IDs, actual URLs, source/licensing absent | Reconcile TASK-008; Praxxis independent QA | **UNOBSERVABLE** | Grok/Praxxis |
| Article → Focus free lead | Confirmation and attributed signup unverified | Stage existing Jetpack path with consent; no test subscriber without permission | **LIVE FREE ROUTE; NOT PAID** | Claude/Site QA/Dispatch |
| Guide A vs video B → paid order | No approved live trial/commerce | Parity verified; full staged browser and caption tests next | **SOURCE PASS; REAL-WORLD UNTESTED** | Mind/Site QA/founder |
| Order → actual net | Missing merchant report/refund/fee ledger | Reconcile independent merchant source and session cohorts | **NOT COMPUTABLE** | Claude/Growth #820 |

**Release:** HARD HOLD. No WordPress/Jetpack/Dispatch email, Grok content, analytics installation, merchant contact, link activation, paid ad, checkout, CMS navigation, merge or deployment performed. Mind hub PR #172, homepage PR #49 and art lead #150 untouched. Provide only source-grounded approval evidence to #171 and #820.
