# Mind R185 — One-offer proof-to-purchase contract and creator-topic fit
**2026-11-06 PT · UNPUBLISHED · Founder-release HARD HOLD**
**Scope:** Mind & Perception presell/editorial/evidence, no Grok production, Dispatch editing, main-site engineering, WP CMS writes, merchant checkout, or spend.

## Decision in one sentence
Do not launch another monetized Zen12 page merely because an attractive design exists. The public Inspire3 portal is not an account-level approval. Choose the commercial offer only when publisher identity, permitted channels, approved earning URL, exact landing product, current customer price/returns, and transaction reporting are independently authenticated. Until then, the current offer is **Zen12 Premium, research-only**; the buyer page and CTA are natively disabled. If an authenticated, rights-cleared Payhip Mind product is proven to be presently purchasable, prioritize that owned product for the first authorized revenue pilot.

## Offer → funnel step → blocker → change/experiment → pass/fail → owner

| Priority | Offer / step | Hard blocker | Experiment or correction | Pass evidence / current state | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 Premium / merchant purchase | FV-specific affiliate approval, channel permissions, link and tracking terms not established | Review signed approval/account screen and link generation against the actual Zen12 Premium product; no public link before approval | FAIL-to-activate: generic https://affiliates.inspire3.com/ only; named FV authorization unknown | Founder / Mind |
| P0 | FV-owned Payhip product / paid order | No independently authenticated currently sellable, licensed Mind SKU | Read-only inventory + proof of rights, current listing, live checkout, price, returns, payment destination and fulfillment | UNKNOWN, not assumed sellable | Commerce |
| P0 | Either offer / verified net revenue | No settlements, approved purchase source attribution, fees, or refunds | Request read-only settlement ledger + order IDs (store securely; never in public issue) and aggregate derived counts | NOT COMPUTABLE; no sales claim | Commerce / Growth |
| P1 | Grok asset → qualified landing | Actual published media IDs, allowed CTA placement and human traffic not reconciled | Grok/Praxxis reconcile asset ID, platform, publication time, allowed link, audience and rights through existing TASK-008 | PENDING; no new posting or queue edits | Praxxis / Grok |
| P1 | /mind/ → Focus | Fieldbook route exists, but guest confirmation/delivery and subscriber count need independent test | Validate existing one Jetpack list, consent, download and welcome using approved QA process, no duplicate form | NOT VERIFIED in this sprint | Site QA / Dispatch |
| P1 | Presell A vs B / purchase | A/B cannot provide paid outcome until approved earning URL and merchant reconciliation | Controlled text-only A versus same guide + opt-in original 42-second video B | Designed, not run; optional poster/transcript concept only, no MP4 | Mind / Claude / Site QA |
| P2 | Page fidelity and trust | Merchant page displayed inconsistent price observations, untested refunds; claims exceed evidence | Use accurate features only, no fixed price or savings claim, remove efficacy shortcuts and countdowns | SOURCE CHECK PASS for controlled copy; production/browser unknown | Mind / Site QA |

## Audience and three proposed creator fits (NOT instructions to Grok)
Actual asset_id, post URL, publication time, link placement, captions, rights, qualified human sessions and attribution are **unknown** for each until Grok supplies them via Praxxis. Do not invent published media IDs or relabel existing Grok work. Do not replace Mini Museum acquisition priorities.

| Creator topic / honest hook | Existing or proposed destination | Intent | Best free action | Commercial fit if independently authorized | Integrity caveat |
|---|---|---|---|---|---|
| Change blindness: “what changed without your noticing?” | LIVE https://finalvestige.com/2026/11/02/change-blindness/ | Curiosity, low immediate buying intent | Optional existing https://finalvestige.com/focus/ | None by default | The demonstration does not prove meditation products improve perception. |
| Mesmerism to suggestion: “who supplied the answer?” | LIVE https://finalvestige.com/2026/11/02/mesmerism/ then LIVE Puységur https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/; proposed R185 memory investigation is UNPUBLISHED | Evidence/history, low-to-medium buyer intent | Read originals, optional Focus | A separate critical hypnosis-product guide only with relevant buyer intent | Hypnosis history is not clinical proof or memory recovery. |
| “Would a twelve-minute guided audio library fit your schedule?” | R185 Zen12 Premium A/B guide — UNPUBLISHED, no public destination | High-intent purchaser evaluation | Three free 12-minute trials + existing Focus; no signup required to read guide | Zen12 Premium precise offering only after named publisher approval | No 12-minute-equals-one-hour, brain-reprogramming, anxiety relief, or guaranteed results. |

**Proposed UTM scheme when Grok explicitly selects a destination:** `utm_source=<actual_platform>&utm_medium=organic_social&utm_campaign=mind_offerfit_2026_11&utm_content=<actual_asset_id>`. Record platform's actual destination constraints and bio-link intermediary separately. `utm_content` is an immutable asset identifier, not a viewer ID; do not put email addresses, personal identifiers, click IDs or private notes in URLs. Campaign naming does not establish source attribution until first-party landing and actual media IDs corroborate it.

## No-JS offer-design acceptance
A and B use the same independently vetted offer wording and natively disabled merchant button. Both render the full guide without JavaScript, with links to original science and the same existing `/focus/` destination. B adds only the original optional 42-second film **concept** as a collapsed `<details>` with SVG poster and timed transcript. Video is not made and has not been tested. If an MP4 is later produced, require caption VTT, full transcript, no autoplay, no network request for video until explicit interaction, reduced-motion/no-sound respect, poster, codec fallback, and keyboard/mouse/touch checks.

**A/B assignment hypothesis, not a result:** among *qualified human* high-intent sessions arriving via verified creator assets, the optional contextual video may improve understood offer fit and eventually paid purchase rate compared with an identical useful guide without video. Randomize at the approved routing layer only if that does not require a paid vendor or duplicative analytics script. Assign visitors to A or B once within a 7-day horizon using only a short-lived, consent-appropriate first-party experiment assignment. If privacy constraints or traffic volume make reliable randomization impossible, label side-by-side usability review as **qualitative**, not A/B conversion evidence.

**Primary metric:** `realized_net_revenue_per_1000_qualified_human_sessions = 1000 * (settled_attributed_sales_receipts + settled_attributed_affiliate_commissions - refunds - merchant_fees - attributable_direct_transaction_costs) / verified_qualified_human_sessions`. If the numerator or denominator is missing, report NOT COMPUTABLE, never 0. Report 7-day and 30-day cohorts with timestamp boundaries, product and campaign ID, and merchant settlement reconciliation. Gross purchase price is not the partner commission. If affiliate reporting gives only aggregated unattributed sales, report the merchant aggregate separately and mark creator-level paid attribution UNKNOWN. Treat tiny cohorts as descriptive; no uplift or statistical significance when information is insufficient.

**Event dictionary (use existing first-party/Jetpack-compatible measurement, Claude owns implementation):**
- `campaign_landing`: first party /mind/ or article view with observed UTM and referrer; exclude known bots, QA and repeat floods; report uncertainty.
- `article_to_focus_click`: hyperlink click, not lead.
- `confirmed_signup`: only when Jetpack backend confirms opt-in and welcome/delivery; do not infer from click or unconfirmed count.
- `presell_guide_view`: human-accessible offer guide view; do not require PII or mandatory newsletter.
- `affiliate_outbound`: authorized earning-link click only; NEVER call it purchase. Before activation do not emit synthetic clicks.
- `merchant_confirmed_paid_purchase`: independently reported, settled nonrefunded merchant order within agreed attribution window.
- `merchant_confirmed_paid_affiliate_conversion`: approved partner ledger reports sale/commission; use only verified amounts.
- `refund_fee_adjustment`: financial reconciliation; may arrive after 7-day cohort and revise results.

No new SaaS, pixel, fingerprint, email-list, third-party cookies or duplicated scripts. Do not store visitor identity or transfer email, IP or the Focus subscriber list to Inspire3. Reconcile publisher tracking IDs privately with merchant export; only aggregate statistics go into public GitHub issues.

## Disclosures, objections and acceptance gates
FTC disclosure must be plain text immediately before an eventual affiliate CTA (not 'affiliate link' alone). Example: **“If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.”** The A/B prototypes display it prospectively and explicitly state no earning link is active. Keep this adjacent on 360/390/768/1440/1920px screens and after keyboard focus. The site-wide affiliate policy is additive, not a substitute.

Efficacy claims require competent product-specific substantiation; general research about meditation, hypnosis, EEG or source monitoring is not evidence that the merchant's audio benefits the individual buyer. For Zen12, the seller's 12 levels/48 MP3 library is described accurately. Year-long refunds are **advertised**, not independently verified. The public price was inconsistently returned as $87 and $87.99 and is never committed in CTA copy; verify current checkout. Do not repeat merchant countdowns, discounts, guaranteed outcomes, earnings statistics or fake testimonials.

**Blocking acceptance before any commercial launch:** authenticated publisher acceptance and channel permissions; approved exact earning URL; current checkout and returns verification; independent QA of all product claims; final real-browser a11y and privacy/performance evidence; explicit founder release authorization; Grok asset linking and adequate consent; merchant settlement pathway to distinguish clicks from paid sales. The default state is DISABLED.

## Source and coordination references
- Canonical business charter https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818 and conversion contract https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820
- Mind ownership and editorial contract https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- FTC guides https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Seller https://inspire3.com/ and exact offer https://zen12.com/hnp ; generic public enrollment https://affiliates.inspire3.com/
- Research https://doi.org/10.1016/S0022-5371(74)80011-3 ; https://pubmed.ncbi.nlm.nih.gov/621467/ ; https://pubmed.ncbi.nlm.nih.gov/37205669/
- Praxxis/Grok creator source-of-truth TASK-008 https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit and dated handoff https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit. Mind may add a research-only note, not change Grok's publishing queue.
- Dispatch issue #174 owns newsletter copy and sending; site QA #126 owns independent release audit; homepage Issue #150/PR #49 and Mind hub PR #172 are untouched.

**Release state:** Source work only. No active sales, no visitor measurement deployed, no affiliate link, no newsletter send, no site edit and no claim of real revenue.