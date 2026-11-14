# R383 — conversion acceptance, creative routing and QA handoff

**Date:** 2026-11-14 PT
**State:** DRAFT / UNPUBLISHED / HARD HOLD. No claim of paid results.
**Owner:** Mind & Perception presell/evidence lane only.
**Do not modify:** homepage flagship PR #49, Issue #150, canonical Mind PR #172, live CMS, Jetpack Focus welcome, Dispatch issue drafts, Grok task queue, affiliate accounts or production analytics.

## Offer selection and decision
**High-intent audience:** readers intrigued by cognitive attention research who are evaluating a short guided meditation audio library and want product format/limitations before purchasing. **Tentative product:** seller-described Zen12 Premium, 12 levels / 48 MP3s, advertised one-year money-back guarantee (seller claim only). Exact offer checkout, rights, product-specific outcomes and refunds unverified. Previous public captures showed different $87/$87.99 amounts; zero numeric prices in buyer variants. The public affiliate portal exists but **publisher acceptance, permitted channels, unique earning URL, referred SKU terms and actual commission remain not authenticated**. Gmail targeted search did not locate approval and cannot establish absence. **Fallback FV-owned paid Mind SKU:** not authenticated; do not pretend the free Focus Fieldbook is paid inventory.

**Core message:** Twelve-minute sessions may be a convenient format. A meditation experiment involving three months of intensive training does not validate a particular 12-minute audio program. Source-backed value: help a buyer separate a seller's package from an independently tested result.

## Buyer page acceptance
A (text only) and B (identical core text plus optional 42-second film storyboard) contain:
- original scientific micro-story + clear seller-reported format, free honest exercise, objections, scientific limits;
- separate editorial analysis from a future commercial offer;
- visible adjacent prospective commission disclosure and **native disabled** merchant purchase button;
- one existing free Focus route; no duplicate subscription form, JS, remote pixels, redirects, merchant links or autoplay;
- accessible SVG alt, transcript and six VTT cues for B (film **concept only**, not encoded/hosted/playable).
A/B hypothesis, not outcome: an optional small original film may improve eligible paid conversion **without deteriorating mobile Core Web Vitals**. Randomize by durable anonymous first-party assignment only if consent/site policy and existing analytics permit. Same body copy, CTA, price/terms and hero for both; video only treatment. No claim of lift without confirmed paid orders and comparable denominators. Performance stop if LCP/INP/CLS regress materially; accessibility must pass at 360/390/768/1440/1920 CSS breakpoints, keyboard, reduced motion, no JS and screen-reader.

## Three creator routes (pending authenticated media IDs)
1. Grok change-blindness video (ID/date/URL unknown) → https://finalvestige.com/2026/11/02/change-blindness/ → https://finalvestige.com/focus/ → optional vetted Zen12 presell if high-intent; no forced signup.
2. Grok Franklin/Mesmer video (ID/date/URL unknown) → https://finalvestige.com/2026/11/02/mesmerism/ → Puységur sources https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ → optional Focus; commerce only if genuinely relevant.
3. Grok historical hypnosis/Puységur video (ID/date/URL unknown) → https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ → suggestion history and practical evidence guide → optional future Hypnosis Live guide after separate evidence/rights approval.

Praxxis owns independent published-platform verification and TASK-008 coordination. Grok owns creation/posting and immutable `asset_id` handoff, not this lane. **No asset IDs invented.**

## First-party privacy-safe measurement specification (no script installed)
Contract: `utm_source` platform, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<verified actual asset_id>`. Store only approved, allowlisted campaign IDs and anonymous cohort/variant; reject arbitrary input as event properties, sanitize referers, avoid emails, IPs, cookies/fingerprints or individual user journeys in logs. Native server analytics may already exist: Claude must inspect before adding code.

Events, independently labeled:
- `qualified_landing`: bot-filtered human session and verified asset_id + landing route; eligibility methodology documented;
- `article_to_focus_click`: navigational CTA interaction, **not lead**;
- `provider_confirmed_lead`: Jetpack confirmed opt-in from provider records, subject to privacy and ability to attribute; avoid subscriber PII;
- `affiliate_outbound`: only after partner authorization and on authorized click; **not sale**;
- `merchant_confirmed_paid_purchase`: independent merchant confirmed settled order or partner reported paid sale, deduplicated;
- `refunded_paid_purchase` and `net_settlement`: post-sale reconciliation, fees/taxes if relevant.
No checkout start is inferred from a disabled button or partner referral click. No attribution inferred from generic site views. Traffic, lead, click and revenue are different gates. Seven-day and 30-day cohort reports, anonymized and small-sample warned, plus currency/cohort cutoff, refunds and data provenance.

`net_revenue_per_1000_qualified_human_sessions = (realized_net_revenue / qualified_human_sessions) * 1000` **only if both are validated and denominator > 0**. Otherwise: NOT COMPUTABLE, never a synthetic $0. Record paid conversion rate, confirmed orders, lead-to-paid customer, gross/net, refund and fee adjustments separately. A/B decision only with verified merchant outcomes, not pageviews.

## Release blocker → change/experiment → pass/fail → owner
| Offer / funnel step | Blocker | Controlled action | Evidence right now | Owner |
|---|---|---|---|---|
| Zen12 → paid commission | Named authorization + link + checkout absent | Verify current account and exact permission/terms | HOLD, no link | Founder/Commerce |
| FV-owned alternative → paid order | Paid, deliverable rights-cleared SKU absent | Inspect active Payhip SKU, license, delivery, refund | HOLD | Commerce |
| Grok → article | Three actual media asset IDs unknown | Read actual published asset, hook, date, mobile link | UNKNOWN | Praxxis/Grok |
| Article → Focus lead | Jetpack provider confirmation not independently exercised | Review consent, confirmation and attribution with existing list | UNTESTED | Claude/Dispatch |
| A/B guide → paid purchase | B storyboard, merchant authorization + browser QA absent | Later encode own 42s video, test no JS/AX/perf, hold activation | STATIC ONLY | Site QA/Claude |
| Paid order → net | No merchant settlements + bot-filtered denominator | Ledger/report reconciliation; 7/30 day cohort | NOT COMPUTABLE | Commerce/Claude |

## Safety and independent QA
- No claim that meditation audio heals, cures anxiety, gives IQ/wealth gains or compresses an hour of advanced meditation into 12 minutes.
- Seller packages and one-year warranty are attributed, not independently verified fulfillment/refunds.
- FTC endorsement guidance https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking; FTC health products https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance.
- No active seller/affiliate links in buyer variants. No deceptive scarcity, prices, countdown or manufactured user testimonial.
- Native `disabled` is required; ARIA-only is not a substitute for prevention.
- Article is scientific-historical reporting. Offer is a separately marked, optional buyer page.
- Tests: run `node mind/r383/verify.mjs` from checkout; commit-source in-memory V8 checks are distinct from native Node/browser/CMS/merchant tests. Explicitly record what did not execute.
- Coordinate review with site QA #126, homepage art #150 and Dispatch #174 **by comment only**, preserving ownership. Log exact branch/commit, tests and sources to #171 and #820.
