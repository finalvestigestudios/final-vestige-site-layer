# Mind R485 — Offer → funnel → blocker → experiment → evidence → owner

**Status:** source-controlled design only, unpublished, no affiliate activation. **Date:** 18 November 2026. **Owner:** FV Mind & Affiliate editorial/presell lane. **Critical KPI:** refund-adjusted realized net revenue per 1,000 qualified human sessions, not pageviews, followers, CTA clicks, leads or attribution conjectures.

## 0. Commerce verification happens before buying-page publication

**Inspire3 / Refersion evidence:** connected Gmail was searched specifically for sender `refersion.com`, for subject patterns "affiliate", "partner", and "approved" in conjunction with Inspire3/Zen12/Refersion, and for Inspire3/Zen12 sender patterns, covering 1 August through 18 November 2026. The identifiable account-status message, dated 24 August 2026, says "Your affiliate account is pending." No subsequent *named account acceptance*, issued referral URL or approved channel list was authenticated by that search. Marketing newsletters from an Inspire3-related sender do **not** prove affiliate approval. Merchant portal/dashboard state was not accessible in this audit, so we do not assert rejection or current approval. **Result: P0 HARD HOLD.**

**Fallback owned offer:** The live Seven Day Focus Fieldbook at https://finalvestige.com/focus/ is free and tied to the existing Jetpack welcome. No currently payable rights-cleared Mind SKU, checkout, refund policy and fulfillment was authenticated. This does not prove none exists anywhere; it means this sprint cannot truthfully nominate one for a paid-conversion pilot. **Result: no speculative paid owned-product CTA.**

**Seller offer identity:** Zen12's standard https://zen12.com/about presents a twelve-minute, twelve-level audio program and four audio formats. The exact https://zen12.com/secret/ promotion describes a 12-level/48-MP3 package with additional bundle details. The main zen12.com and promotional funnel vary in pricing presentation, terms and promotional framing; neither has been validated as the offer that an approved Final Vestige referral would send readers to. No current price, countdown, discount or refund language is adopted as an FV-specific promise. Public checkout terms must be captured and founder-authorized before activation.

## 1. Audience → specific offer fit

**Primary audience:** a curious viewer who just watched a factual attention demonstration and wonders whether a structured twelve-minute audio session is more useful than a free timer. Motivations: a consistent brief listening habit, clear files and playback, a realistic price and cancellation/refund understanding. Not assumed: diagnosis, guaranteed brainwave change, fear of failure, desire for wealth or belief in extraordinary claims.

**Actual decision:** compare a no-cost structured starter practice to a seller-described audio program with four styles. If proven authorization and appropriate SKU terms become available, place one *plainly disclosed* commercial recommendation at the end of the independent buyer guide; never between scientific conclusion and its source.

**Near-term verified action:** visit the *existing* free fieldbook if it fits the reader's intent. This is a real published destination and can be monitored under existing analytics when privacy and QA are approved. It is not a paid purchase.

## 2. 3-video creator-topic-to-product crosswalk (research-only to Praxxis/Grok)

| Creator-topic hypothesis | Publisher state | On-topic destination | Optional next step | Product suitability / commercial limit |
|---|---|---|---|---|
| "How can a specialist look at a gorilla and miss it?" with 1999 + 2013 + 2023 caveat | New 2,123-word R485 investigation is **DRAFT**, no public route | Until published and signed-out QA: existing https://finalvestige.com/2026/11/02/change-blindness/ only if the actual video hook covers related attention, not if it promises a radiologist paper | existing https://finalvestige.com/focus/ | Zen12 is at most optional format-comparison guide; no claim that it prevents inattentional blindness |
| "How a large change disappears in plain sight" | Existing published Change Blindness investigation | https://finalvestige.com/2026/11/02/change-blindness/ | existing Focus Fieldbook | Consumer attention practice related by topic, efficacy not inferred |
| "What did Puységur actually document?" | Existing public historical source files | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | source audit, then optional Focus | Hypnosis Live may be researched separately, but historical magnetic somnambulism is not product evidence |

**Asset authorization gate:** All actual Grok `asset_id`, platform, spoken hook, publication date, permalink, media rights, signed-out route and appropriate UTM link are **UNKNOWN / UNMATCHED** in this sprint. `TBD` strings are not media IDs. Praxxis and Grok must authenticate existing posts and decide any creator assignments. Do not edit Grok's queue, publish or repost media, or rename a video to fit a sales page. The shared TASK-008 handoff is research-only.

## 3. Experiment specification: source guide vs source guide + optional 42s film

- **A:** `ZEN12_BUYING_GUIDE_A_TEXT_ONLY.html`, complete original independently sourced buyer guidance, six objection questions and native disabled paid control.
- **B:** `ZEN12_BUYING_GUIDE_B_OPTIONAL_FILM_CONCEPT.html`, same buyer guidance with an *additional optional* 42-second original educational film concept, poster, captions and transcript; **not** an encoded video.
- **Hypothesis:** the optional source-first film may improve **verified paid conversion per qualified human visitor** by clarifying the research/product boundary, or may harm conversion due to distraction, bandwidth or lower trust. Neither direction is asserted.
- **Variables:** preserve identical headline, core buying copy, disclosure, free alternative, offer SKU, actual checkout, routing and pricing. Only optional media varies. Never ship split variants that secretly receive different offers.
- **Accessibility:** real poster and transcript must be available no-JS; once production video exists use native `<video controls preload="none" poster>` with accessible timed caption `<track kind="captions">`, no autoplay, text alternative for substantive visuals, visible focus, responsive 360/390/768/1440/1920, reduced motion and keyboard testing. If any of these is missing, video variant is not ready.
- **Performance:** no third-party embed/tracker by default, avoid eager media loads, responsive poster, production compression, measure Core Web Vitals on actual supported devices and fallback without JS.
- **Primary result:** realized net revenue per 1,000 qualified human sessions. Secondary diagnostic: verified paid order rate, lead-to-customer after confirmed opt-in, revenue per buyer, returns and commission settlement lag. Track 7-day and 30-day cohorts and report small sample sizes with confidence intervals rather than declaring a winner from clicks.
- **Experiment gate:** NO visitor assignment, merchant clicks or sale attribution until authorized earning URL, real paid checkout, user-consent determination, founder release and Site QA pass. All current variants are research artifacts.

## 4. Privacy-safe event and accounting contract — no duplicate scripts

Use the existing first-party analytics mechanism only if Site QA/Claude confirms data semantics; do not inject another pixel, new SaaS, email form or fingerprint.

`utm_source=platform`, `utm_medium=organic_social`, `utm_campaign=mind_attention_2026_11`, `utm_content=verified_asset_id`. The `utm_content` must be the actual creator-owned stable ID, not a fabricated campaign asset. Define `variant=A|B` server-side only when experiment is approved; do not place personal data in URL parameters. Do not store raw IP, email, precise geo, user-agent fingerprints or third-party advertising identifiers in a new dataset.

Event meanings (never substitute a proxy for a settled order):
- `qualified_landing`: valid first-party visit after consent/applicable privacy checks and transparent bot/internal QA exclusions; count method documented.
- `article_to_resource_click`: outbound internal navigation to existing Focus or archive route. Not subscription.
- `confirmed_signup`: Jetpack independently confirms existing list opt-in. Unconfirmed signup forms do not count; dedupe against same existing list and do not access mail addresses in reporting.
- `affiliate_click`: *only after approved commercial activation*, actual outbound to an authorized merchant link. Not transaction.
- `merchant_confirmed_purchase`: authenticated merchant order with permitted aggregate matching, not a browser checkout view.
- `commission_settled`: authentic partner reconciliation of earned and payable commission; separate paid order from merely attributed commission.
- `refund_or_reversal`: merchant-confirmed financial adjustment.
- `realized_net_revenue`: paid and settled amount attributable to cohort minus discounts, refunds, chargebacks, known fees, and any applicable cost treatment explicitly disclosed in the scorecard.

**Key metric:** `(realized_net_revenue / qualified_human_sessions) * 1000` only when BOTH a verified denominator and verified applicable settlement exist. Otherwise status is **NOT COMPUTABLE**, not zero. Distinguish zero recorded *after complete observation* from missing observation.

Use 7/30-day time cohorts, distinct control and treatment buckets, source/offer/variant by qualified campaign. If affiliate platform cannot supply permitted aggregate conversion attribution, label *unattributed*, do not invent a join from near-simultaneous click times. Low sample counts (including fewer than 100 qualified visitors per variant) merit prominent "exploratory, insufficient power" warnings; power analysis and sequential-testing rules need approval before interpreting an A/B result.

## 5. Offer → funnel step → blocker → change / experiment → evidence → owner

| Priority | Offer / step | Blocker | Proposed change / experiment | Pass / fail evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → commission | Account accepted status, SKU, link, channel terms unverified | Request/read *named partner approval and authorized offer terms*; do not send sales traffic | PASS only with dated written approval + URL + terms; CURRENT HOLD | Founder / Commerce |
| P0 | FV-owned Mind → paid order | No authenticated payable SKU and delivery | Audit owned sale inventory, rights, refund and fulfillment before any new landing | PASS only with signed-off item, current checkout and fulfilled test order; CURRENT HOLD | Founder / Claude |
| P1 | Original article → relevance | R485 unpublished and site routes immutable | Editorial review + correction + staged route check | PASS after source reviewer and signed-out/mobile 200; NOT TESTED | Mind editorial / Site QA |
| P1 | Grok asset → qualified landing | IDs and exact spoken hooks absent | Praxxis authenticity crosswalk; no creator task change | PASS after actual ID, publicly accessible URL, rights, topic-fit and UTM check; UNKNOWN | Praxxis / Grok |
| P1 | Article → free fieldbook | Existing Jetpack delivery untested in this sprint | Read-only funnel QA; no new test emails without permission | PASS on confirmed existing-list delivery and accessible route; NOT TESTED | Claude / Dispatch |
| P1 | Guide A/B → merchant sale | B video conceptual, commerce disabled, a11y/browser untested | Encode original optional film, caption, compare only after approval | PASS on consistent buyer copy, accessible media, authorized checkout and actual paid results; HOLD | Mind / Site QA |
| P0 | Merchant → net revenue | Settlement and qualified human cohorts not authenticated | First-party ledger reconciliation; consent/data minimization review | PASS only on independently verified orders/settlements, refunds, fees and cohort denominator; NOT COMPUTABLE | Commerce / Claude |

## 6. Do-not-cross boundaries / handoff

No edits to live WordPress CMS, nav/settings or production website. No homepage PR #49 update, no takeover of Issue #150, no change to canonical Mind hub PR #172. Do not change Dispatch Issue #174 drafts or its existing Jetpack welcome. Do not activate affiliate links, marketing emails, social posts, paid services, new analytics instrumentation or production release.

Exact sources: https://inspire3.com/ ; https://zen12.com/about ; https://zen12.com/secret/ ; https://doi.org/10.1371/journal.pone.0286023 ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance ; https://finalvestige.com/focus/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://doi.org/10.1068/p281059 ; https://doi.org/10.1177/0956797613479386 ; https://doi.org/10.1073/pnas.2214930120 .

**Commercial result today:** paid commission not verified, FV-owned payable product not verified, real A/B not executed, qualified human session-to-settlement attribution not available. **Net revenue/1,000 qualified sessions: NOT COMPUTABLE.**
