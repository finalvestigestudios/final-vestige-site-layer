# R123 — One-offer commercial acceptance and creator-fit contract
**Status:** Draft research/engineering proposal, 2026-11-04 PT. **Zero approved affiliate links, zero proven payments.** Owner: Mind & Perception (#171). Commerce source of truth #820; charter #818. This file does not authorize deployment, merchandising, social posting or email sends.

## Commercial decision before further landing-page work

**High-intent audience:** Adults who already search for short, structured meditation audio and are asking whether the *specific* Zen12 library makes practical sense. Avoid luring a visitor searching for a cognitive illusion into an unrelated product offer. For a casual invisibility-gorilla or change-blindness reader, the next action should be the **free Focus Fieldbook**, not a paid offer.

**One potential paid offer:** Zen12 Premium is the lead commercial candidate, not an approved offer. 2026-11-04 public research at https://inspire3.com/ and https://zen12.com/hnp documents seller-described 12-minute sessions, 12 levels, 4 styles, 48 Premium MP3s. A different official seller page https://zen12.com/secret/ shows a $37 conditional coupon; /hnp displayed a $87.99 Premium promotion. Neither represents a verified FV customer checkout price. The buyer guide deliberately avoids claiming a fixed price, savings, or recurring/one-time terms that are not currently verified. The same seller's https://inspire3.com/privacy/ says affiliates *may receive buyer name/email/product details*; our policy is no buyer PII ingestion, requiring documented merchant permission and reporting configuration.

**Owned-product fallback:** Existing https://finalvestige.com/focus/ is *free*, not a paid order. The previous authenticated WordPress audit verified this route and Puységur; this run's public web tool could not reopen those URLs. There is no authenticated Payhip-paid-SKU/rights/fulfillment/settlement document in this sprint. Until commerce supplies actual seller-side evidence, **do not invent a paid FV Mind product** or redirect customers to an unverified checkout. Founder/Claude commerce must provide authenticated seller inventory and authorized product/rights/return policy.

**Go/no-go decision:** HOLD ALL merchant earning links and paid conversion claims. The existing draft A/B guide may be staging-tested but not promoted to live or linked from a published email.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER (priority ordered)

| Priority | Offer / funnel step | Blocker | Single most valuable change or experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → permitted commission | No named acceptance; merchant approval link and privacy-safe reporting absent | Request written partner account eligibility, permitted social/email channels, approved URL/creative, commission/refund/attribution contract, right to prevent receipt of buyer PII | Signed/dated merchant evidence + approved link + permission matrix; **FAIL/CLOSED** | Founder merchant outreach; Mind verification |
| P0 | FV owned digital SKU → verified checkout | No authenticated current paid Mind SKU/rights evidence | Audit Payhip seller dashboard on one existing SKU: title, licensed rights, visible price/currency, tax, checkout total, download fulfillment, refund terms, completed transaction identifier and payout/fees | Authenticated dated screenshots/export, rights record, settled test/real order; **UNKNOWN** | Claude/commerce |
| P1 | Creator asset → one matched factual article | Immutable Grok post ID, channel permalink, live CTA placement and genuine clicks missing | Crosswalk three *existing* Grok assets; no queue changes | Asset ID + live URL + campaign UTM destination + screenshot; **UNKNOWN** | Grok/Praxxis TASK-008 |
| P1 | Article → qualified free lead | Jetpack current fieldbook subscription and delivery attribution not proven per asset | Independently test existing Focus→Dispatch welcome/delivery and opt-in without adding form, consent or list | Confirmed delivery and aggregate campaign/source, avoid exposing emails; **PARTIAL/NOT VERIFIED** | Site QA/Dispatch |
| P1 | Article → independent Zen12 buying guide | Draft /mind/ and guide not live; research article also unpublished | Staged reading path with accessible cross-links; never route posted social traffic to drafts | Mobile 360/390/768/1440/1920, no JS, keyboard, WCAG AA, disclosure; **BUILT, BROWSER UNTESTED** | Mind + Site QA |
| P1 | Guide → merchant outbound | Product authorization and checkout proof missing | Keep native button disabled; after permissions, replace with only reviewed destination and clear immediate commission disclosure | Disabled in all source prototypes; **PASS STRUCTURALLY**, commerce **FAIL/CLOSED** | Mind/founder |
| P0 | Paid purchase → realized net | No merchant confirmed orders, fees, refunds, or qualified-human denominator | Reconcile settlement-level payouts and cohort traffic from authoritative sources | Merchant-confirmed orders/customer/refunds/fees + attribution confidence; **UNKNOWN/NOT COMPUTABLE** | Growth + Claude #820 |

## Creator-to-article-to-product fit: research-only crosswalk

| Candidate Grok topic / research hook | Live first-party destination on prior authenticated WP audit | Useful action | Commercial intent fit | Proof still missing |
|---|---|---|---|---|
| Change Blindness — “What changed while you looked?” | https://finalvestige.com/2026/11/02/change-blindness/ | Existing /focus/ (optional, no gate to research) | **Low buyer intent.** No auto Zen12 pitch. | Actual asset ID, platform URL, landing CTA placement, qualified sessions |
| Mesmerism/Puységur — “When does suggestion become evidence?” | https://finalvestige.com/2026/11/02/mesmerism/ → https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Source archive, then optionally /focus/ | **Low–moderate** on historical interest; only a self-selected tools reader may open evaluation | Actual media rights, permalink, live navigation, consent logs |
| Attentional Blink — “Why does the second number vanish?” | **New R123 manuscript is NOT live** | After approval: fact-first investigation → optional /focus/ | Moderate curiosity; paid Zen12 **only** for explicit “buy short meditation audio” interest in separate guide | No live target URL, actual Grok asset ID, source permissions or released guide |

Praxxis/Grok retain production responsibility. Do not script video, post to channels, overwrite TASK-008, or assign imaginary asset IDs. Use existing TASK-008 convention: utm_source platform where actually supported, utm_medium=organic_social, utm_campaign=mind_pilot_2026_11, utm_content=<verified unique Grok asset_id>. Do not assume TikTok caption URLs are clickable; document bio/profile attribution loss honestly. Do not put email, name, phone, raw IP, fingerprint, or receipt tokens into URL parameters.

## First-party measurement contract (plan only, NO new script)

**State transition:** consent-respecting, deduplicated *qualified human session* → article landing → topical CTA (Focus click / buyer-guide click) → optional Jetpack-confirmed lead → approved merchant affiliate_click → partner **confirmed, paid, attributable commission** → refunds / partner and processing fees → *realized net revenue*. A checkout-start is not a sale. An outbound click is not a commission. Pageviews and creator views are diagnostics only.

Record only aggregate fields where allowed: day (PT or UTC consistently), verified asset_id, source, medium, campaign, landing path, guide_variant (A/B), event enum, session qualification category, numeric counts, transaction status from merchant aggregate reporting. A session ID or consent signal, if used by production analytics, stays within approved first-party instrumentation—not a new script here. Lead counts can be reported only from Jetpack-confirmed records, not inferred via /focus/ views. Commercial outcomes require merchant payment reconciliation; record data-source lineage, confidence and delay.

**7/30-day cohorts:** Primary KPI = 1000 × realized net revenue / qualified human sessions, where realized net revenue = settled merchant proceeds/commission less discounts, fees, refunds, chargebacks and explicitly attributable expenses, with currency and attribution basis disclosed. Report paid conversion rate, confirmed paid orders and customers, gross and net, lead-to-customer, and refunds. If the merchant cannot supply an attributable aggregate paid outcome or denominator is zero/unknown, display **NOT COMPUTABLE**, not $0. Require minimum sample context and confidence intervals; at tiny samples label findings exploratory.

**Privacy:** No personal identifiers are sent to merchant via UTMs. Do not receive or store buyer-identifying partner reports. Written authorization must either restrict affiliate reporting to aggregate nonidentifying data or identify an alternative compatible arrangement agreed by the founder. No new pixels, redirects, GA scripts, email forms or SDKs. Respect user consent and existing production analytics decisions. Native download/lead attribution remains probabilistic if platforms strip UTMs.

## Controlled A/B hypothesis and release gate

**A:** Full original source-first independent decision guide with fixed text and disabled purchasing control. **B:** Byte-identical guide plus an optional original forty-second storyboard. Poster uses CSS, captions span 00:00–00:40 continuously, transcript is in an expandable native details element with visible title. There is **no recorded video, MP4, VTT file, autoplay, embed or third-party fetch** in this sprint. No-JS readability remains intact. Neither variant can be traffic-tested for merchant conversion until a *live*, approved purchase path exists.

**Hypothesis:** For explicit guide-intent visitors, optional film may clarify the evidence distinction without increasing perceived unsupported medical/brainwave claims. It might also distract and reduce conversions. Control allocation should be randomized by stable consent-safe session assignment *only with approval*, not manually routed by social platform. Keep offer, CTA text, price verification, disclosure, source copy and placement equal. Assess *verified net revenue per 1000 qualified humans*, not play events, button taps or raw visitors. Predeclare minimum detectable effect and stop rule with realistic traffic first; insufficient paid sample → **INCONCLUSIVE**. Monitor WCAG, mobile scroll depth, non-JS rendering, CWV/LCP, film bandwidth, caption/transcript validity, source references and consent/security. A storyboard cannot support a performance claim about a future video.

## Staged acceptance and ownership

1. Named merchant acceptance and exact approved seller destination (Mind/founder); do not copy merchant testimonials, creatives or claims absent permissions.
2. Authenticate actual paid FV SKU instead if merchant does not permit the needed privacy configuration (commerce owner).
3. Independently perform mobile keyboard, reduced motion, contrast, axe/WCAG, CSP, no-JS, form and privacy checks (Site QA #126).
4. Preserve PR #49, #172 and Issue #150; ask homepage lead for isolated optional portal integration only after approved hub QA. Avoid altering current homepage or menus.
5. Coordinate Dispatch Issue #174 solely on possible future *approved* guide URL and allowed affiliate email terms. Do not edit drafts, replace Focus welcome, send newsletters or establish another list.
6. Reconcile first-party/merchant evidence in #820; founder explicitly approves live publishing, paid acquisition and posting separately.
7. On rejection, rollback by **not shipping** these isolated files. No live artifact requires rollback now.

**Research links:** https://pubmed.ncbi.nlm.nih.gov/1500880/ ; https://doi.org/10.1371/journal.pbio.0050138 ; https://doi.org/10.1371/journal.pone.0286023 ; https://zen12.com/hnp ; https://zen12.com/secret/ ; https://inspire3.com/privacy/ ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
