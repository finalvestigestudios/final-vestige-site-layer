# Mind R165 — One Offer, One Purchase Proof: Approval and Conversion Experiment Contract

**Status:** UNPUBLISHED / research-only / no partner purchase URL enabled. **Owner:** Mind & Affiliate Studio (pre-sell evidence) collaborating by review with Commerce, Claude Engineering, Site QA, Dispatch #174, homepage #150 and Praxxis/Grok TASK-008. **Do not publish, deploy, send, post, or modify Grok production assignments.** The only live first-party destination assumed from Issue #171 is the preexisting /focus/ route; its current anonymous behavior is not verified in R165.

## Founder priority and immediate commercial decision

**Offer candidate:** Zen12 Premium, exact standard public seller page https://zen12.com/?no-popup=1. **Audience:** people actively evaluating an audio meditation library after seeing credible attention/perception research, **not** all historical readers. **Buyer desire:** easy-to-revisit, short, varied audio sessions. **Real value proposition that may be stated after verification:** twelve levels, 48 MP3 tracks, four styles, downloadable structure **as described by the seller**; NOT a fivefold acceleration of meditation, clinical relief, guaranteed focus, wealth or brain repair.

**Disqualifier:** No authenticated publisher-specific Inspire3 approval, promotion rules, exact tracking link, current checkout/refund proof, or accepted commercial release. Merchant CTA in the HTML is a native disabled button, with no commerce href. This **hard hold** overrides a polished page. The public affiliate portal and promotional subscriber emails are not proof of publisher authorization. The proposed fallback, a rights-cleared FV paid Payhip Mind SKU, is likewise unverified; do not fabricate one. Prefer an authenticated currently sellable FV item once Commerce supplies product ID, rights, checkout and delivery records.

### Offer → funnel → blocker → experiment → test evidence → owner

| Priority / offer | Funnel step | Blocker | Proposed change / experiment | Pass / fail acceptance | Owner |
|---|---|---|---|---|---|
| P0 Zen12 Premium | Click → paid conversion | Named account approval, earning URL and terms absent | Check authenticated account status and exact SKU/channel permissions; document signed permission and merchant reporting | **HOLD** now; PASS only with acceptance, link, payout scope and terms sourced | Founder + Mind |
| P0 FV-owned product backup | First-party checkout → confirmed sale | Payhip product ID, rights and returns unavailable | Commerce inventory read-only audit; select one *actually live, rights-cleared* SKU | **UNKNOWN** now; PASS only after verified checkout and delivered order | Commerce |
| P1 Zen12 buyer page | Offer view → eligible CTA | No approved product-specific pre-sell live | Review original source-controlled guide and page; test 360/390/768/1440/1920 widths, reduced motion, no-JS, keyboard | Source-level PASS pending full browser QA; merchant button remains disabled | Mind + Site QA |
| P1 Focus route | Article → confirmed lead | Guest Jetpack submission and welcome delivery unverified | Test existing native /focus/ signup and expected welcome via authorized test account without new list | **UNVERIFIED**; record actual confirmation and email receipt or fail | Site QA + Dispatch |
| P1 Grok assets | Social → qualified-human visits | Actual asset IDs and placement permissions unavailable | Match each posted asset to canonical published article and allowed UTM placement via TASK-008 | **PENDING**; PASS only with immutable platform media IDs and allowed links | Praxxis + Grok |
| P0 Revenue integrity | Visits → merchant paid settlement | No real orders/fees/refunds crosswalk | Read merchant-authoritative settlement data; dedupe order IDs; reconcile 7/30-day cohorts | **NOT COMPUTABLE**; never substitute events for paid order | Commerce + Claude |

## Three proposed social video → article → Focus → optional offer routes

These are editorial *fit hypotheses*, not Grok production orders. Praxxis must match real published assets and permissioned UTM placements in the existing TASK-008 document, with publisher approval before public CTA changes.

1. **Change blindness**: Hook: “One detail changed. Did your attention catch it?” → LIVE historically reported https://finalvestige.com/2026/11/02/change-blindness/ → existing https://finalvestige.com/focus/ → optional independent meditation audio buyer guide **only for readers who expressly want a short listening routine**, and only after affiliate authorization. `asset_id = NULL`.
2. **Puységur / history of suggestion**: Hook: “What did observers in 1784 record—and what did they assume?” → historically published https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ → /focus/ → optional exact-product meditation guide only with a clear editorial/commercial boundary. `asset_id = NULL`.
3. **Choice blindness**: Hook: “Can you explain a decision that was swapped?” → R164 original investigation **DRAFT / NOT A LIVE URL**; no campaign landing or live cross-link yet. The study specifies tasting jam and smelling tea with **containers covertly flipped before final selection**, not a last-second reswap; never claim proof of commercial persuasion. `asset_id = NULL`.

No drafted video is assigned to Grok, no task queue is changed, and no marketing copy is inserted into its scripts.

## Attribution without counterfeit conversions

Use Claude Engineering's one existing first-party analytics stack if and only if the founder approves any changes. Do **not** add another GA4, Ahrefs script, pixel, cookie, or third-party library for R165. No PII, hashed email identifiers, IP address, full query-string dumps, or raw checkout secrets.

Approved conceptual event schema:

- `landing_view`: timestamp day-bucket, path, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `asset_id` if supplied by Grok; synthetic/bot and internal QA traffic excluded using documented methods. Denominator must be **qualified-human sessions**, not pageviews.
- `focus_cta_click`: on existing link, same campaign attribution when legal and consent-appropriate; a click is **not** a confirmed subscription.
- `confirmed_lead`: only when first-party Jetpack subscription state and authorized delivery/consent evidence support it; avoid identifying individual subscribers in exports.
- `offer_guide_view`: when independently validated and actually live, not a staged HTML preview.
- `affiliate_click`: only future authorized merchant outbound link, with allowed link and nearby disclosure; this event is **not** purchase or commission evidence. No active affiliate_click event exists in R165.
- `merchant_confirmed_order` and `merchant_confirmed_commission`: from Payhip official order records or partner-authenticated report, never client-side browser scripts.
- `refund`, `chargeback`, `fee`: reconcile on merchant-authoritative records, separate gross and settled realized revenue.
- `net_revenue_per_1000_qualified_human_sessions`: `1000 × (realized settled revenue – refunds – fees – recognized chargebacks) / qualified-human sessions`. Report **NOT COMPUTABLE** when numerator, denominator or attribution basis is unverified. Provide 7-day and 30-day cohorts, count and interval estimates; tiny samples are insufficient to declare a winning arm.

Deduplicate outbound and paid events separately. A visitor tapping a CTA several times should not be represented as several buyers. If affiliate partner tracking does not expose order-level linkage, label acquisition attribution **unverifiable**, even if total account commissions exist.

## Controlled text-only vs optional-original-video pilot

**Hypothesis, not promise:** a short video may help a motivated buyer grasp the gap between *seller package* and *scientific outcome*, without sacrificing page load or trust. Test only after named partner permission, commercial release and QA.

- A: exact same guide with source notes, proof/limits, price uncertainty, Focus option, and approved disclosed offer CTA.
- B: identical guide, plus original opt-in **42-second locally hosted** video with properly owned visuals/audio, poster, accurate timed WebVTT captions and full transcript. No autoplay; use `preload="none"`, no third-party embed, responsive player, reduced-motion/no-JS support.
- Randomization: stable non-PII assignment in approved first-party instrumentation with bot/internal exclusion. Assign by **qualified human session** if visitor-level persistence would require consent; respect privacy/consent decisions.
- Primary outcome: independently verified, attributable **settled net revenue per 1,000 qualified-human sessions**, not play rate or CTA click. Secondary: confirmed orders/visitors, net fees and refunds, Focus confirmed leads, affiliate outbound taps. Track load times, accessibility and disclosure recall as guardrails.
- Preanalysis: agree minimum information threshold with Growth/Commerce before running; do not declare a winner from a handful of purchases. No publishing a fabricated 10% or 20% uplift prediction.
- Stop/go conditions: freeze if affiliate permission lost; if consent/data protection fails; if conversion link broken; if material claims become unsubstantiated; if accessibility regresses; or if attribution cannot distinguish bot/test traffic.
- Performance: do not load video until user opts in, target compressed poster, no external scripts. Explicitly monitor LCP/INP/CLS on 360, 390, 768, 1440, 1920 widths in real browser after authorized staging build.

## Proposed internal link architecture (requires editorial/release review)

The existing Mind hub draft is PR #172 and must not be overwritten or independently deployed. Add a limited "Tools under review" source card *in a future approved release* pointing to a vetted buyer guide, not from scientific conclusions directly to paid CTA. Change Blindness and Puységur pages can each use one clearly optional **read the free Focus Fieldbook** in-body link once Claude/Site QA approves the already proposed changes. R164 article is not live; do not generate a public campaign destination from a draft slug. From the guide, link back to the specific investigation plus source notes and to /focus/. Avoid ad-like cross-links in editorial results paragraphs; visually separate purchasing evaluations.

## Source and copy approval checklist

Check the official [Inspire3 brand catalog](https://inspire3.com/), the [exact Zen12 standard seller page](https://zen12.com/?no-popup=1), and [distinct promo offer](https://zen12.com/secret/) separately. Do not reuse merchant ads, testimonials, or approved creative without actual rights. Record current checkout and returns through authorized verification before activation. Preserve near-button plain English: **"If you purchase through this link, Final Vestige may earn a commission at no additional cost to you."** The default preview already includes this disclosure next to a physically disabled control. Disclosures must remain visible in both A and B.

**Standing release instruction:** NEVER touch live CMS, homepage PR #49, Issue #150, PR #172, Jetpack welcome, Dispatch draft sequence, Grok queue, affiliate tracking or analytics until the proper owner and founder approve the specific release.