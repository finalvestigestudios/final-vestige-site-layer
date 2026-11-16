# Mind R425: Conversion Acceptance, Experiment and Creator Fit
**16 November 2026 | UNPUBLISHED / HARD HOLD | Issue #171 + #820.**

## 0. Conversion first: what can actually be sold?
The public Inspire3 Affiliate Network advertises publisher sign-up and special links; it does **not** demonstrate that Final Vestige Studios has been approved, has access to an authorized earning link, or can advertise each product through social platforms. Gmail searches for relevant terms returned *consumer* marketing, not FV-named acceptance. The public Zen12 storefront advertises several packages and a refund policy, but an applicable referred checkout, tax, restrictions and merchant settlement are not verified. No product-specific evidence substantiates its advertised meditation-time equivalence.

As fallback, the currently live FV [Focus Fieldbook](https://finalvestige.com/focus/) is **free**, not an authenticated paid SKU. No independently authenticated FV-owned, rights-cleared, operational paid Mind product has been found in this run. Therefore **both paid pathways stay disabled**. A draft is an investment option, not an activated conversion mechanism. No product URL is inserted as an earning link.

## 1. Creator-topic → canonical article → free resource → tentative offer
All three rows are **candidate content matches**, not evidence that Grok published the video. Praxxis must obtain actual published YouTube/TikTok URL, immutable `asset_id`, exact spoken hook, rights/usage scope, posting date and mobile link path from Grok's original TASK-008; no fabricated IDs.

| Candidate video/topic and honest hook (not a posted script) | Destination already live and checked | Existing next step | Potential offer (held) | Evidence / risk |
| --- | --- | --- | --- | --- |
| Thatcher illusion: "Why can an altered face seem less bizarre upside down?" | Future **unpublished** Thatcher article; until published, safely land on [Change Blindness](https://finalvestige.com/2026/11/02/change-blindness/) with explicit topical distinction | [Focus Fieldbook](https://finalvestige.com/focus/) | Zen12 buyer guide, not yet public | Thompson 1980; Wong et al. 2010; **no illusion cure claim** |
| Door swap: "Can the person asking you directions change before your eyes?" | [Change Blindness](https://finalvestige.com/2026/11/02/change-blindness/) | same existing Focus route | Zen12 only if intent matches | Simons & Levin 1998; small sample and observational task |
| Franklin's hidden cause: "What did the commission find when participants couldn't know they were being treated?" | [Mesmerism](https://finalvestige.com/2026/11/02/mesmerism/) + [Puységur Files](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) | same existing Focus route | Hypnosis Live guide only after independently reviewed exact SKU | Historical commission; avoids claiming magnetism or hypnosis benefit |

**Creator boundary:** Grok retains video production/posting; Praxxis verifies IDs/hooks/allowed link surfaces via existing TASK-008. This workstream supplies source and guide eligibility only. Do not edit the video queue or Dispatch content.

## 2. High-intent buyer and truthful presell
**Audience hypothesis:** a reader who wants an achievable, optional 12-minute listening ritual but is skeptical of neuroscientific promises. **Buyer problem:** cannot consistently create a practice without structure. **Specific value under consideration:** a seller-described collection of short MP3 sessions organized in levels, not promised mental or medical outcomes. The guide gives this reader practical product-format facts, independent limits, a free alternative, package/return questions and a prospective affiliate disclosure. It does not ask readers to subscribe before learning the answer.

**Pilots:** `ZEN12_A_TEXT_ONLY.html` and `ZEN12_B_OPTIONAL_VIDEO_CONCEPT.html` use the **same substantive buyer guide**. B adds one 42-second original static poster/transcript/caption concept, no player, no autoplay, no external resource. The storyboard is not an encoded video and cannot be used as proof of a film-performance or conversion outcome. Final video release requires an original voiced/rights-cleared asset, captions tested in an actual player, poster, reduced-motion/no-JS fallback, LCP budget and site QA.

**Controlled A/B hypothesis (NOT TESTED):** a voluntary, lightweight optional film could better explain the evidence boundary for some high-intent mobile readers without depressing trust, accessibility or paid orders. After partner approval and founder release, the *single* primary decision endpoint is **merchant-verified, refund-adjusted paid conversion per qualified-human landing session**; guardrails include latency, bounce/exit, unintentional video playback (must be zero), and clear recognition of the disclosure. Lock page copy, price presentation, visitor inclusion, UTM channel, cohort duration and checkout before assignment. Assign at first-party level with a minimal consent-compatible random key and no sensitive profiles or new fingerprinting. Do not call an affiliate click a purchase. Tiny samples mean inconclusive, not success.

## 3. Privacy and measurement contract — no duplicate scripts
Proposed first-party schema to **reuse Claude's existing analytics path** after permission, not deploy a new tracker:

```json
{"event":"campaign_landing","campaign":"mind_pilot_2026_11","utm_source":"youtube|tiktok","utm_medium":"organic_social","utm_content":"verified_asset_id","page":"/2026/11/02/change-blindness/","variant":"A|B","consent":"honored"}
{"event":"article_to_resource_click","from_page":"known_slug","to_page":"/focus/","asset_id":"verified_asset_id"}
{"event":"affiliate_outbound","product":"zen12","merchant_authorized":true,"variant":"A|B","asset_id":"verified_asset_id"}
{"event":"confirmed_lead","source":"Jetpack_provider_confirmation","dedupe_token":"existing_non_pii_provider_id"}
{"event":"merchant_confirmed_purchase","source":"merchant_order_record","order_reference":"opaque","amount":null}
{"event":"settled_affiliate_commission","source":"merchant_statement","commission_net":null,"refunds":null,"fees":null}
```

The above is *illustrative schema*, not captured data. Do **not** create or transmit an event called `affiliate_outbound` while there is no authorized active link. Never put email, visitor IP, name, health status, product hypotheses or unconsented raw identifiers into URLs. Deduplicate Jetpack confirmations via provider records; do not manufacture test subscribers. Attribute only where the platform path and merchant reporting actually support it. Leave missing values **UNKNOWN** rather than zero.

**Reporting:** 7-day and 30-day matured cohorts, qualified unique human sessions from independently verified Grok `asset_id`, landing visits, contextual CTA click, provider-confirmed lead, merchant-confirmed gross paid orders, refunds, fees and net recognized revenue. Formula: `net_revenue_per_1000 = 1000 * (settled_gross_receipts - refunds - chargebacks - fees) / qualified_human_sessions`; for affiliate, use **settled commission actually attributable to FV, less reversals/fees**, not hypothetical customer gross. If denominator or verified income absent, show **NOT COMPUTABLE**. Small samples get explicit uncertainty and no causal claim.

## 4. OFFER → STEP → BLOCKER → EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
| Priority / offer | Funnel step | Blocker | Proposed change or test | PASS/FAIL evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 Zen12 | commercial eligibility | No FV acceptance/issued URL/allowed SKU/channels | Authenticate partner account and merchant-issued terms **read-only** | Signed/account-verifiable terms, exact link; absent = HOLD | Founder / Commerce |
| P0 owned FV digital | actual checkout | No identified rights-cleared payable Mind SKU | Inventory rights, transaction checkout, receipt, delivery, return rules | Authenticated live payable item; absent = HOLD | Founder / Claude |
| P1 landing→offer | buyer trust | Price/tiers/refunds differ by offer | Reconcile exact referred checkout, display only source-backed facts | Screenshots/merchant confirmation and source row | Commerce / Site QA |
| P1 Grok→article | qualified click | Video IDs/rights/link availability unknown | Verify 3 already-published authentic asset IDs/mobile CTAs in TASK-008 | Genuine URLs/UTMs; absent = NO MATCH | Praxxis / Grok |
| P1 article→Focus | confirmed lead | Jetpack provider confirmation/delivery not audited | Read-only audit existing single funnel | Provider proof, consent and dedupe | Claude / Dispatch |
| P2 guide A/B | paid order | B storyboard not encoded; browser QA incomplete | Encode with original footage; release controlled compliant test | Real browser+caption/performance tests; merchant paid cohort, not clicks | Mind / Site QA |
| P2 paid→net | settled revenue | No genuine transactions or attribution denominator | Reconcile merchant statements, refunds and qualified sessions | Independently verified paid order and settled net | Commerce / Claude |

## 5. Editorial/UX & security acceptance
- Keep investigative conclusions outside paid-guide copy; use `rel="sponsored noopener noreferrer"` on future authorized external affiliate link only after written approval.
- Near-link disclosure must remain immediately adjacent in DOM and visible at 360px and zoom 200%; a footer disclosure alone fails.
- No forced playback, autoplay, cookies, canvas fingerprinting, tracking pixels, iframes, third-party player, background media or JS dependency in drafts. Both variants offer full evidence by text and keyboard.
- Sanitize source-only HTML using the actual WordPress theme/plugin chain; no live CMS mutation in this sprint. Real QA must include 360/390/768/1440/1920, mobile nav, axe/WCAG 2.2 AA, 200% zoom, contrast, reduced motion, screenreader landmarks, keyboard, caption sync and Core Web Vitals.
- Preserve homepage flagship PR #49, Issue #150, canonical Mind hub PR #172, Dispatch Issue #174, existing Jetpack welcome and all social queues.
- Approval chain: Founder commercial/release → merchant permission/pricing → independent Site QA → Claude engineering → founder go/no-go. This document grants no deployment or publication authority.

**R425 result:** Source-controlled drafts prepared; no live page, approved affiliate URL, confirmed checkout, product purchase, Jetpack confirmation or qualified Grok matched sessions. Net revenue/1,000 qualified sessions = **NOT COMPUTABLE**.
