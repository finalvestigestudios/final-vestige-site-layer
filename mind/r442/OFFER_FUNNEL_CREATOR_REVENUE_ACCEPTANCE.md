# R442 — Offer-to-revenue decision and attribution contract
**Status: source-controlled, unpublished, no commercial activation | 2026-11-17 PT**

## 0. The commercial decision before design

**Candidate high-intent audience:** organic/social readers interested in short meditation practices who have completed, or are evaluating, a twelve-minute focus routine and are considering a downloadable guided/sound course. Do not confuse “likes perception tricks” with “intends to buy meditation audio.”

**Preferred conditional offer:** Zen12 full-course format, only if named Final Vestige publisher approval, specific SKU/channel permissions, an issued earning URL, matching referred checkout/returns and founder release approval are evidenced. The exact vendor description currently claims 12-minute sessions, twelve levels and four variants per level; a separate promotional surface describes 48 MP3 tracks. *No evidence reviewed proves a 12-minute hour-equivalence or product-specific health effects.* Official source surfaces: https://zen12.com/about and https://zen12.com/secret/ . Public promotional price/discount intentionally NOT adopted as a Final Vestige price.

**Fallback gate:** public /focus/ is a free 52-page lead magnet, NOT a payable product. No authenticated purchasable, rights-cleared FV-owned **Mind** SKU with current checkout/fulfillment/refunds was established. Do not fabricate one. Founder/Claude should verify a real existing paid SKU, its intellectual-property rights, current fulfillment and merchant transaction reconciliation before substituting an owned offer.

**Offer, not asset count, is the bottleneck.** Several previous isolated Mind source draft PRs exist and remain hard held. R442 adds scientific differentiation and tighter product/measurement boundaries; it must not be used to imply a launch was authorized or a prior guide went live.

## 1. Creator-topic → exact destination → optional audience capture → offer fit

| Candidate Grok hook (not a published media claim) | Scientifically defensible core | First-party article destination | Free next step | Commercial alignment | Status |
|---|---|---|---|---|---|
| “How did nobody see the person switch?” | Change blindness is experimentally studied; witnessing is not full scene memory | https://finalvestige.com/2026/11/02/change-blindness/ (existing LIVE canonical) | https://finalvestige.com/focus/ if relevant | LOW/MEDIUM; do not force Zen12 on curiosity-only visitors | Grok asset_id and exact published mobile URL NOT VERIFIED |
| “Why the invisible gorilla was invisible” | Attentional load may hide an unexpected event; no diagnostic or product benefit implied | R438 invisible-gorilla source draft ONLY, unpublished; select actual live article only if approved | Same existing /focus/ route | LOW/MEDIUM | Media ID and live article destination UNVERIFIED |
| “Do binaural beats really make you focus?” | Four-layer distinction: beat percept → EEG response → attention task → sustained work | R442 investigation UNPUBLISHED; no live link, hold social redirect | /focus/ independently useful | HIGH-INTENT subject fit, Zen12/Focus Shot comparison only after permission | Media ID, publication, landing and approved offer all UNVERIFIED |

**Praxxis/Grok coordination:** supply these as research-only candidate hooks to the existing TASK-008; request confirmation of exact published asset_id, campaign tag, allowed CTA/mobile link, posting date, rights and platform. Grok chooses/produces/posts; this workstream does not enqueue content or assert live views. If no published matching article exists, do not tag a draft as a landing destination.

## 2. One presell, two genuine treatments, one payable endpoint after authorization

**Control A:** `ZEN12_A_TEXT_ONLY.html`: full independent buyer guide, no video. **Variant B:** `ZEN12_B_OPTIONAL_FILM_CONCEPT.html`: identical buyer text plus original optional 42-second audiovisual concept with original static SVG poster, transcript and VTT caption source. **Currently B is storyboard only, not an encoded film**; no actual experiment can run yet. Both have free direct first-party link, exact seller facts only as descriptions, five buyer objections, no merchant href, a truly native disabled button, and adjacent hypothetical earning disclosure. The identical buyer text is critical for isolating the film addition rather than changing the offer/copy simultaneously.

**A/B hypothesis (not a promise):** with an eligible paid referral product and properly verified traffic, optional original short film may improve independently confirmed net revenue per 1,000 qualified human sessions without materially increasing load time, reducing accessibility, or undermining trust. **Null:** no difference or film makes business results worse; text-only may be superior. Do not pretend that video reach predicts purchaser outcomes.

**Allocation after authorization only:** 50/50 at first eligible campaign landing, sticky per consented first-party assignment or deterministic server-side nonidentifying bucket; no cross-site identity or unsolicited tracking. For nonconsenting users, present default A and do not set experimental IDs. No client-side experiment framework or new SaaS. Claude owns any actual implementation/review; no new script in these HTML sources.

**Keep both arms identical:** word-for-word commerce copy, same independently authorized exact checkout, same disclosed affiliation, same CTA position/language, same page hierarchy and same price/terms; B adds *only* a short click-to-play media unit near introduction. Static no-JS reading state and full text remain available. Avoid autoplay, video CDN preloading, inline trackers, auto-enrolling visitors, third-party pixels.

**Minimum QA before experiment:** exact partner and approved landing; creator asset_id→route→offer parity; 360/390/768/1440/1920 px screenshots; keyboard/focus/touch/VoiceOver or equivalent; WCAG 2.2 AA audit; color contrast; mobile speed and Core Web Vitals, poster alt semantics, transcript, synchronized captions, reduced motion, media error fallback and download size; consent and data retention review; published source/citation, FTC placement, checkout/returns tests and independent QA signoff.

## 3. Measurement: no paid sale from a click

Minimum source tags from actual creator links, if platform permits:
`utm_source={actual_platform}&utm_medium=organic_social&utm_campaign=mind_audio_pilot_2026_11&utm_content={actual_grok_asset_id}`.
Do not invent an asset ID; if a link-in-bio hop is used, document an exact mapping. Avoid personal identifiers in UTMs.

**Unit of exposure:** a distinct eligible human session with explicit criteria (bot and internal-test exclusions, valid UTM route, real page load, consistent 7/30-day UTC+local conversion windows, consent as required). Do not simply interpret Jetpack pageviews as qualified human visits.

**Event boundary and owners:**
1. `campaign_landing`: server-observed legitimate landing, no PII, logged only under approved controls; owner Claude.
2. `article_to_resource_click`: event where observable, distinct from confirmed email lead; owner Claude.
3. `confirmed_signup`: provider-confirmed Jetpack subscriber only (deduplicated), never a form view or button click; owner Claude/Dispatch.
4. `offer_guide_view`: visit to a LIVE approved guide; a draft-file view does not qualify; owner Claude.
5. `affiliate_click`: click on authorized merchant earning link; NOT a sale; owner Claude if first-party tool already supports this.
6. `merchant_confirmed_order`: independently reported eligible paid affiliate or FV product order, net of duplicate/test orders; owner Commerce.
7. `refund_or_chargeback`, `merchant_fees`, `settled_commission`: actual merchant/partner accounting; owner Commerce.

Do not deploy duplicate analytics scripts or cookies. Aggregate 7/30-day cohorts by `asset_id`, article, eligible offer and A/B arm. Prefer privacy-preserving nonidentifying event counts and merchant aggregate order reconciliation; do not send email/IP/cookies to new systems or deanonymize individuals to join social and purchase data. If exact user-level attribution is absent, report merchant sales as verified but source attribution unknown. Approval/consent limits trump perfect attribution.

**Definitions:** `confirmed_paid_orders` are verified payments only; `gross_revenue` excludes click value; `realized_net_revenue = settled receipts or commissions - refunds - fees - chargebacks - allocable direct costs` (report costs separately and currency conversion if relevant). `net_revenue_per_1000 = 1000 * realized_net_revenue / qualified_human_sessions`, only when both numerator and denominator exist and use the same eligibility window. `paid_conversion_rate = confirmed_paid_orders / qualified_human_sessions`; `lead_to_customer = matched_verified_purchasers / deduped_confirmed_leads` only if appropriately observable, otherwise UNKNOWN. Report 7- and 30-day raw N, missing attribution, and tiny-sample uncertainty; no p-value-driven winner call on tiny cohorts.

**Current R442 status:** payable link = NOT VERIFIED; affiliate approval = NOT VERIFIED; paid purchase = NOT VERIFIED; confirmed commission = NOT VERIFIED; qualified-human denominator = NOT VERIFIED; A/B arm assignment = NOT IMPLEMENTED; **net revenue/1,000 = NOT COMPUTABLE**, not zero and not a click estimate.

## 4. Prioritized OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Priority | Offer and step | Blocker | Next change or experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → valid checkout | No named FV partner acceptance/earning link, allowed social/site/email channel or exact referred terms | Authenticate written approval and merchant dashboard/link only with designated account authority | PASS only named written rights, issued exact SKU link, approved creatives and checkout/returns; otherwise HOLD | Founder/Commerce |
| P0 | Alternative owned digital SKU → paid order | No verified rights-cleared payable Mind SKU/checkout | Read-only check of already-live owned inventory; assess actual SKUs, rights, fulfillment/refunds | PASS only existing payable SKU and live verified purchase path, no test purchase without approval | Founder/Claude |
| P1 | Exact creator media → article | No matched published Grok asset_id/live Mind destination | Praxxis/Grok TASK-008 research handoff and source audit | PASS real media ID, publishing URL, permitted tracked landing and rights | Praxxis/Grok |
| P1 | Article → Focus Fieldbook lead | Existing Jetpack provider confirmation not retested here | Read-only confirmation/delivery and one-list consent audit | PASS provider-confirmed unique lead and actual existing welcome route, no dummy signup | Claude/Dispatch |
| P1 | Buyer guide → verified paid order | Current offer link intentionally disabled | Test copy, accessibility, exact seller offer vs checkout, and disclosure before any activation | PASS QA + founder release + merchant-reported order; affiliate_click alone FAIL | Mind/QA/Founder |
| P2 | Film B vs text A | No encoded playable captioned film or valid eligible traffic | Produce original film, mobile performance baseline, after approvals run controlled experiment | PASS full WCAG/film + 7/30-day verified net-revenue cohorts; else INCONCLUSIVE | Mind/QA/Claude |
| P2 | Settlement → revenue | No merchant order/refund/fee evidence | Reconcile actual statements against sessions and event buckets | PASS matched timeframe signed-off finance proof; else UNKNOWN | Commerce/Claude |

## 5. Internal-link and editorial guardrails

Proposed navigation only, no CMS writes: **Explore/Library → Mind Archive → independently sourced investigation → free Focus Fieldbook (optional) → tools guide (optional)**. Keep published change-blindness URL canonical. Keep Puységur archive as a separate historical source trail. Put contextual FTC earning disclosure directly next to a specific affiliate recommendation after authorization; do not put commercial copy inside the research conclusion. Do not duplicate Dispatch or Fieldbook forms, alter homepage flagship PR #49, art Issue #150, canonical Mind hub PR #172, Dispatch Issue #174 or site QA ownership. WordPress hub source has `noindex` in the *offline file only*, not a request to alter live robots settings.

## 6. Evidence and next release decision

This sprint's artifacts: one original research manuscript (R442), offline hub, Zen12 A and B with static SVG/poster/transcript/VTT, 34-claim / 13-source matrix and 28 all-HOLD gates, tests/QA receipt. Scientific sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/ , https://doi.org/10.1038/s41598-025-88517-z , https://pmc.ncbi.nlm.nih.gov/articles/PMC7082494/ . Vendor pages https://inspire3.com/ , https://zen12.com/about , https://zen12.com/secret/ , https://brainwaveshots.com/focus-shot and https://hypnosislive.com/mental-skills/total-focus . FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

**Release decision: HARD HOLD.** Founder approval, partner-specific permissions, actual payment and QA evidence must precede activation. No merchant link, newsletter send, social post, paid purchase, WordPress edit, merge or deployment is authorized by this source draft.
