# R171 — One-offer first-purchase contract, creator fit, and release-ready evidence gates
**Final Vestige Studios · Mind & Affiliate · 2026-11-06 · DRAFT ONLY**

## Decision at the top
**Candidate primary Mind offer:** Zen12 Premium, exact official merchant listing https://zen12.com/ (merchant describes 12 levels / 48 MP3s). **Eligible affiliate status: NOT VERIFIED**. Public https://affiliates.inspire3.com/ has a registration/login screen, not evidence of approval for Final Vestige. **ACTIVE CTA: NONE; purchase control disabled.** No claimed earnings, customer results, pricing guarantees, generated partner links or paid conversions.

**Fallback:** An *existing*, rights-cleared, independently purchasable FV-owned Payhip Mind digital SKU **if and only if** authenticated Payhip evidence confirms ownership, listing status, current public price, checkout, digital delivery, terms, refund policy, and a demonstrably successful order. Scope review of existing inventory ONLY. No new product invented. None authenticated in this sprint. Do not substitute an arbitrary product simply to show a button.

**Highest-intent audience:** People already comparing meditation-audio packages who value structure, file format and a manageable listening routine, not illusion viewers passively watching Grok videos. Two micro-personas: (A) buyer wants a guided routine without subscribing to another app; (B) buyer specifically comparing a paid audio library with free recordings. Avoid claiming this audience is measured until first-party analytics prove it.

**Critical business output:** attributable *cleared* FV-owned purchases or *settled* paid affiliate commissions, minus non-netted reversals/fees, divided by **qualified human website sessions** in a defined cohort. NOT pageviews, clicks or merchant gross sales.

## OFFER → STEP → BLOCKER → EXPERIMENT → ACCEPTANCE → OWNER
| Priority | Offer and funnel step | Blocker | Change or controlled test | Pass evidence / fail condition | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → earning link → commission | Named account/channel/link not authenticated | Verify signed-in acceptance, permitted placements/creatives, exact tracking URL and current order/reversal terms without disclosing secrets to public issues | PASS: redacted acceptance evidence + link validated by partner reporting; FAIL: only public signup / promo mail | Founder + Mind |
| P0 | FV-owned Mind SKU → verified paid checkout | Payhip product/rights/price/delivery/returns not authenticated | Read-only inventory audit and controlled purchase validation only under authorization | PASS: authorized live product SKU, visible terms, confirmation, fulfillment, net settlement record; FAIL: screenshot of a product concept only | Commerce |
| P0 | Paid order → settled net | No attributable transaction or denominator available | Source-system join with event IDs and accounting reconciliations | PASS: 7-/30-day reports with cleared orders, payout, refund/fees and attribution coverage; FAIL: treating clicks or checkout start as sale | Commerce / Growth |
| P1 | Buyer guide → credible CTA | Product claims cannot be borrowed from hypnosis/EEG research | Independent exact-offer guide, explicit seller attribution and near-link disclosure; disabled while unapproved | PASS: QA verified no merchant href, native disabled, accessibility checks; FAIL: any live earning/seller link | Mind + Site QA |
| P1 | Grok asset → qualified landing | Actual asset_id and public link unknown | Read existing TASK-008, request Praxxis QA handoff only; no production queue edit | PASS: real platform ID, publish date, permitted CTA placement and actual destination; FAIL: made-up media ID | Grok / Praxxis |
| P1 | Free Fieldbook → confirmed lead | Display status can falsely imply email confirmation | Use one existing Jetpack flow, double-opt-in/delivery proof from authoritative records where applicable | PASS: consent and server-side confirmed event, not CSS/query parameter; FAIL: UI shows subscriber while no verified signup | Site QA / Dispatch |
| P2 | Guide A vs guide B with optional video | No video, no browser/mobile acceptance yet | Controlled test, identical offer/disclosure/CTA, only optional 42s accessible video changes | PASS: reproducible cohort randomization, primary metric confirmed paid purchase rate, guardrails; FAIL: CTR-only declaration of winner | Mind / Site QA / Growth |

## Creator topic-to-product fit: three distinct routes (do not create videos)
| Grok/Praxxis suggested topic | Research truth to communicate | Destination | Free/Dispatch bridge | Commercial fit | Actual asset_id / media URL |
|---|---|---|---|---|---|
| "Why a word can defeat an instruction" (Stroop/suggestion) | Specific suggestion altered Stroop interference for selected participants; no universal mind control | R171 source-controlled Stroop manuscript — **UNPUBLISHED**, no website link | Published /focus/ optional | LOW/MEDIUM: history/science readers usually seek evidence; Zen12 comparison only after independent intent | UNKNOWN; TASK-008 owner |
| "A huge change can vanish while you watch" (change blindness) | Task focus can hide changes; no proof audio improves daily attention | Existing published https://finalvestige.com/2026/11/02/change-blindness/ (route per #171; browser check needed) | Existing /focus/ optional | LOW: do not hard-sell to curiosity viewers | UNKNOWN; TASK-008 owner |
| "Puységur's magnetic sleep—experience versus explanation" | Historical reports of altered states do not establish magnetic fluid or modern recording efficacy | Existing https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (route per #171; browser check needed) | Existing /focus/ optional | LOW/MEDIUM: more relevant to hypnosis history than Zen12; do not misrepresent an eighteenth-century therapy | UNKNOWN; TASK-008 owner |

Never tell Grok what to produce; ask Praxxis to reconcile platform IDs and content fit in its existing TASK-008 and dated handoff. Avoid nonexistent /mind/ traffic destinations until approved. Preserve existing Dispatch issue #174 and its Jetpack welcome, no email sends.

## Internal-link and navigation proposal, not a CMS change
1. Canonical /mind/ hub remains PR #172. The R171 four-stream preview is a **review artifact only**; no duplicate hub replacement. The header/explore link request belongs to homepage/art lead and Site QA after their release.
2. A published Change Blindness investigation may contextualize a *free* Focus Fieldbook link if Site QA approves. It should not claim Zen12 efficacy.
3. Puységur historic archive should link to modern methodological essays only with explicit time-period separations; preserve investigation conclusions and primary archive trail.
4. R171 Stroop research manuscript, if independently edited and published later, can appear under Perception & Attention and History of Suggestion. Commercial buyer guide belongs under clearly marked Tools Under Review, not mixed into conclusions.
5. Each landing must provide its research sources, one usable exercise, one optional free route, and an independent onward navigation path. No forced subscription.
6. The site-wide affiliate disclosure is supplemental, never a replacement for a clear near-button earning relationship.

## First-party attribution without tracking creep
- **Only after approved production engineering:** use Claude's current single analytics instrument under #820, not new pixels or a second GA4 tag. Read allowed `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` and a non-PII `asset_id` value from Grok's real asset inventory. Sanitize format (ASCII alphanumeric, underscore, hyphen, bounded length), strip arbitrary query parameters. Do not treat referrer+UTM as unique people.
- Qualified-human session: first-party session after consent/bot checks where applicable, with known source and explicit timeframe. Mark all unknown portions and bot-filter limitations. Do not stitch identities across devices or store IP/email in exported measurement artifacts.
- Distinct event family: `landing_view` (qualified source session), `offer_view` (guide visible), `focus_click` (free CTA), `confirmed_optin` (authoritative Jetpack record), `affiliate_click` (future outbound only when authorized), `checkout_start` (only when authoritative merchant can show it), `paid_order_confirmed`, `affiliate_commission_confirmed`, `settlement_paid`, `refund`, `chargeback`. A proxy event never upgrades itself into a paid event.
- Store no full email, raw IP, exact referrer with personal tokens, or unconsented cross-site ID. Apply existing privacy policy and consent requirements.
- **Net formula:** FV-owned: actual cleared customer receipts (after price/discounts) minus **only** refunds, chargebacks and expenses not already netted. Affiliate: actual **FV-paid** commission after merchant adjustments, minus only additional non-netted adjustments; do NOT count merchant checkout retail revenue as FV revenue.
- 7-/30-day `net_revenue_per_1000_qualified_sessions = realized_net_revenue / qualified_human_sessions * 1000`. Undefined when denominator or settlement is unknown. Carry source-coverage and sample-size labels. Do not report $0 in lieu of missing data.
- Lead-to-customer rate only where consent and compatible person-level linkage exist; otherwise UNOBSERVABLE, not guessed.

## Controlled A/B hypothesis: useful guide (A) versus useful guide + video (B)
Pre-register **H0**: no improvement in independently confirmed paid order rate among qualified, intent-matched humans. **H1:** optional original ~42-second video may improve actual paid purchases *without* degrading consent, accessibility or performance. This is hypothetical, not an asserted uplift.

- A = same content, art, FTC disclosure, price/returns caveat, single earning destination (after verified approval); no video module.
- B = exactly the same except one user-started video, local lightweight asset, WebVTT captions, full transcript, static poster, no autoplay/preload beyond metadata. No external video CDN unless independently reviewed.
- Randomize eligible qualified sessions 50/50 using one first-party consent-compatible mechanism approved by Claude, with sticky assignment for repeat exposure but not covert tracking. Do not independently inject new cookie or script. Unit = unique qualified session, not pageview.
- Primary outcome = **paid, attributable conversion rate** and **settled net revenue per 1000 qualified sessions** over 7/30-day cohort windows after payout delay, not click-through rate. CTA and free confirmed lead are secondary; report refund-adjusted net and CI/uncertainty. Mark when traffic too small to interpret.
- Guardrails = mobile LCP/INP/CLS, keyboard focus, WCAG 2.2 AA manual review, transcript caption parity, no-JS source guide, CSP/no remote scripts, same proximate FTC disclosure in both arms, no email funnel duplication, no merchants without permission. Stop on disclosure or security failure.
- Zero actual experiment traffic or sales supplied. This proposal is NOT A/B test evidence.

## Exact offer and objection matrix
**What the merchant sells:** 12 levels, 48 MP3s in four listening styles; a stated year guarantee and a public $87.99 Premium figure on 2026-11-06. These are sellers' statements. **Objection:** why pay instead of using free recordings? Answer: a bundled progression and format choices are the described differentiation; usefulness and clinical/cognitive benefits are not independently established. **Objection:** is it a proven one-hour-equivalent meditation? No reviewed exact-product independent efficacy evidence permits that statement. **Objection:** do I have to join an email list? The seller's own free-audio flow appears to have a newsletter opt-in; buyer must inspect terms; FV does not auto-subscribe them.
**What FV can responsibly recommend today:** its already published free Focus Fieldbook, without asserting it will heal/treat or guarantee results. Do not automatically qualify the public Zen12 catalog as an approved affiliate sales funnel.

## Proof and blockers, exact status
Source audit: verified official https://inspire3.com/ , https://zen12.com/ , https://affiliates.inspire3.com/ on 2026-11-06; read FTC official guidance; checked published primary abstracts and academic review; GitHub Issue #171 and #820 inspected. A bounded Gmail query returned promotional communications, **not verified FV publisher acceptance** (one 'access approved' subject was merely a Reprogram.ME waitlist). An authenticated partner dashboard and seller-specific terms were not available in this lane. Payhip authenticated inventory, checkout, refunds, settlements and unique Grok media URLs were also not supplied.
No live WordPress, social, newsletters, Jetpack, merchant account, tracking code, merges, deploys or spend touched.
