# R334 — Offer-first conversion, QA and founder release dossier

**12 November 2026, Pacific | Unpublished; not eligible for merge/deploy.** This folder belongs only to Final Vestige Mind & Perception. Canonical issue: #171; revenue owner coordination: #820 / #818. It does not amend homepage PR #49, canonical Mind hub PR #172, art Issue #150 or Dispatch Issue #174.

## Executive conversion decision

**DO NOT ACTIVATE AN INSPIRE3 LINK.** The publicly available affiliate recruitment page is not proof of Final Vestige's publisher eligibility. This run's targeted connected email search surfaced promotional material but no independently authenticated publisher-specific acceptance/issued tracking terms; the private partner dashboard was not accessed. No permitted earning URL, allowed channels, final pricing, commission settlement or buyer privacy contract was verified.

**DO NOT CLAIM A PAID OWNED PRODUCT IN THIS LANE.** Final Vestige has a confirmed free 52-page Seven Day Focus Fieldbook, not a confirmed paid Mind SKU. Private Payhip SKU/rights/checkout/fulfillment and refund ledger remain unexamined. Without an actually rights-cleared and purchasable Mind SKU, paid conversion cannot be tested. Escalate a private evidence request to Founder–Commerce; do not invent a fallback checkout or mislabel the free lead resource as a product sale.

**Current revenue result:** NOT COMPUTABLE, not zero. Both an independently confirmed paid numerator and trustworthy qualified-human denominator are absent. A click never establishes commission.

## This sprint's original content and conversion fit

The new feature [The Recording in the Trial Was Not the Recording on the Sales Page](./THE-RECORDING-IN-THE-TRIAL-WAS-NOT-THE-RECORDING-ON-THE-SALES-PAGE.md) reconstructs a 2025 333-person clinical audio trial, a 250-person hot-flashes audio trial, a 2025 app-quality review, and 2025 binaural-beat experiment. It explains the intervention/outcome mismatch rather than fabricating universal benefits for Zen12. The Puységur bridge uses the live source archive and retains ethical warnings.

### Three creator-topic-to-product bridges — proposals, not posted media

| Creator intent/topic | Verified editorial destination | Existing lead bridge | Paid offer relevance | Missing handoff |
|---|---|---|---|---|
| Change blindness: why we miss a major visual change | https://finalvestige.com/2026/11/02/change-blindness/ | https://finalvestige.com/focus/ | Low direct paid intent: mention buyer guide only in a separately labeled tools area, not as “a cure” | Genuine Grok asset_id/platform/post URL and CTA placement |
| Attentional blink: why the second target vanishes | R327 source-controlled draft only; **no published article URL** | Existing Fieldbook | Moderate interest in learning attention routines; product still optional | Actual approved publish route; Grok asset metadata |
| History of hypnotism, Mesmer and Puységur | https://finalvestige.com/2026/11/02/mesmerism/ plus https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Existing Fieldbook only if naturally relevant | Historical audience likely research-first, not a consumer-buyer audience; don't force Zen12 CTA | Actual Grok evidence/asset metadata |

**Praxxis/Grok** must reconcile actual existing asset IDs and destination rules in TASK-008. Mind neither makes social videos nor modifies scripts or publishing queues. Claude owns routing. Place source citations in permitted captions/source comments, no deceptive spoken CTA, don't assert TikTok clickable captions.

## Buyer experiment: text versus optional original short

- A: `zen12-A-text-only.html`. Same long-form buying information as B, with official package tiers, 12-minute free demonstration, research limitations, objections, prospective disclosure and genuinely disabled merchant control.
- B: `zen12-B-optional-film.html`. Adds an optional original **42-second** research explainer with poster, six timed caption cues, full visible transcript, `preload=none`, native controls, no autoplay and no JavaScript. The original source-controlled `render_zen12_film.py` generates the MP4 offline. **The MP4 is not committed, not deployed, and must be rendered/staged alongside the HTML before browser QA.** An unrendered B page will have missing media and fails release acceptance; it is not currently a deployable page.
- HTML contains no active merchant link, no new newsletter/signup form, no tracking script/iframe, no invented customer outcome or created scarcity. One true free Fieldbook CTA routes to existing https://finalvestige.com/focus/.
- No screenshot or actual WCAG browser QA claimed in this source bundle. Screens 360, 390, 768, 1440 and 1920; keyboard, source links, focus visibility, reduced motion, captions, video controls, no-JS, broken-image/film fallback and actual WordPress sanitizer must all be checked on staged final assets.
- Controlled experiment only after account authorization and checkout verification. A/B comparison must keep audience, topic, product, price, link/disclosure and underlying buyer copy identical, changing only availability of the film. If Claude cannot randomly allocate non-identifying visits without duplicating scripts or degrading privacy, use clearly labeled **quasi-experiment**, not a causal A/B claim. Preserve no-JS delivery and avoid persistent user identifiers.

**Experiment hypothesis:** adding a credible optional 42-second research film might improve buyer understanding without meaningfully increasing load cost and could improve verified net revenue per 1,000 qualified-human sessions. Competing hypothesis: the film may distract, slow loading or depress buyer confidence. Not guaranteed to convert.

**Acceptance, not wishful metrics:** Before activation, measure served page size and LCP, complete film dimensions/bytes, mobile playback, pause/seek/caption availability, text parity, drop-off by actual offer CTA and verified merchant paid outcomes. No video autoplay, video-based consent coercion or heavy client scripts. No new SaaS.

## Measurement: first-party design, event taxonomy and accounting

Use only current approved first-party analytics where sufficient. Claude owns implementation and avoidance of double tags. No PII in URLs or events, no email/IP/fingerprint stored in proposed event payloads.

Proposed source string (only when actual asset known):
`utm_source={actual_platform}&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content={actual_asset_id}`.
For platforms with bio-only links, explicitly map `asset_id → allowed link route` and label individual-video attribution uncertain if the path collapses several assets. Never fabricate a media ID or source.

| Proposed event | What it proves | What it emphatically does NOT prove |
|---|---|---|
| qualified_human_session | QA-defined non-bot site session with authorized source context | paid customer |
| campaign_landing | allowed article/offer landing observed | useful engagement |
| article_to_focus_click | click to existing Fieldbook page | confirmed subscriber |
| confirmed_signup | provider-confirmed consent/opt-in when observable | purchase |
| authorized_affiliate_outbound | outbound click on issued earning link, after authorization | paid affiliate commission |
| merchant_confirmed_purchase | merchant-sourced paid order, reconciled and within permitted aggregate attribution | settled net revenue before fees/refunds |
| partner_confirmed_commission | platform-sourced paid affiliate commission with status | cash already cleared if pending |
| net_revenue | settled receipts less refunds, chargebacks, merchant fees and partner costs, with dates | implied revenue from click totals |

**KPI:** `1000 * realized_net_revenue / qualified_human_sessions` with raw components, source confidence, eligible 7/30-day cohort windows, refund lag and small-sample warning. If denominator is absent, report **NOT COMPUTABLE**; if denominator is valid but purchases unverified, report **UNKNOWN**, not a measured zero.

Track 7-day and 30-day cohorts by campaign and eligible offer, reconcile merchant-confirmed paid orders and paid partner commissions independently, then refunds/fees. Do not expose customer-identifying data in issue comments or logs. A checkout-start event requires merchant-supplied evidence; no speculative click surrogate. Never add a duplicate Jetpack Dispatch list or rewrite its existing Focus welcome email.

## OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL EVIDENCE → OWNER

| Priority / offer | Funnel step | Actual blocker | Proposed change | Evidence required | Owner |
|---|---|---|---|---|---|
| P0 / Zen12 Premium | approved affiliate earning link → paid commission | FV acceptance, exact issued link, channel terms absent | privately authenticate partner contract, specific SKU, payouts, URL and allowed organic/email | partner account screenshot or signed terms *without publishing secrets*; validated current checkout; QA of consent and adjacent disclosure | Founder–Commerce |
| P0 / FV-owned Mind SKU | sellable product → paid order | private Payhip inventory, rights, delivery and refunds not inspected | audit actual active SKU and successful fulfillment; choose only if Mind audience fit | authenticated SKU ID, license, live checkout, current amount, delivery test, refunds and settled order data | Founder–Commerce |
| P1 / existing Fieldbook | article → confirmed opt-in | campaign-to-provider consent/source reconciliation uncertain | verify current single Jetpack flow and delivery without unapproved test subscriber | consent/confirmed provider status and welcome receipt with appropriate permission | Claude–Dispatch |
| P1 / Grok traffic | actual asset → qualified landing | media IDs and platform permitted URLs missing | TASK-008 inventory reconciled with actual link and article | real asset_id/post URL/source/campaign, mobile route tested | Praxxis–Grok, Claude |
| P2 / Zen12 A/B | matched guides → merchant outcome | no eligible merchant, video staging or independent browser QA | render film, compare variants, only launch after P0 and review | exact SHA, staging screenshots, no-JS, captions, offer copy parity, recorded paid outcome | Site QA–Claude |
| P2 / commerce | paid order → realized revenue | settlements, fees, refunds, qualified sessions missing | reconcile aggregated source records weekly | 7/30-day scorecard with qualified denominator, independent merchant numerator and costs | Commerce–Claude |

## Source integrity and safeguards

Claim classifications and 18 closed authorization gates: [CLAIMS-PARTNER-PROOF-MATRIX.json](./CLAIMS-PARTNER-PROOF-MATRIX.json). All research/merchant official links are preserved as reference URLs, but none is an earning link. FTC citations are included in the matrix and source article.

The proposed `/mind/` layout is an isolated, **unpublished** four-stream [HTML review specimen](./MIND-HUB-EDITORIAL-REVIEW-ONLY.html) and does not supersede existing Mind hub PR #172. Published 61 posts were Issue #171's Oct 30 baseline; a Nov 12 connected read previously reported 66 published posts/92 published pages. Do not repeat baseline as current without a fresh inventory. Production /mind/ not currently verified live.

**Release:** Site QA independent tests, art-owner coordination and founder exact-SHA approval remain required. No live CMS/navigation/scripts, email/social publishing, merchant activation, new subscriptions, paid SaaS, merge, deploy or spending in this branch.
