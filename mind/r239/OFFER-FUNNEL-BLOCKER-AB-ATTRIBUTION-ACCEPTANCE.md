# Mind R239 — Conversion preflight, creator–product fit and independent QA acceptance

**9 November 2026 · SOURCE CONTROL ONLY · NOT A RELEASE · Issue #171 / business #820**  
**New branch:** `mind-r239-gorilla-integrity-commerce-20261109`; draft PR and final SHA are recorded in issue comments after completion.

## Decision first: what can actually be sold today?

**Intended main affiliate vertical: Inspire3 Zen12 Premium.** The exact merchant page, https://zen12.com/hnp, offers a structured twelve-level meditation-audio library with 48 files in four listed styles and advertises a one-year refund guarantee. Those are **seller-described features and promises**, not verified consumer outcomes or proof that merchant refunds have been honored. The seller also suggests that 12 minutes can produce the benefits of an hour's meditation; this is **not independently substantiated for the actual product**. The parent catalog at https://inspire3.com/ is not a partner approval record.

Target adult: someone who has tried a simple timer, wants optional guided structure and varied audio, and is evaluating whether a paid library adds convenience. The **purchase motive is a library format and user choice**, never an invisible-gorilla cure, brain rewiring, guaranteed focus, symptom relief or increased income.

**Actual selling authorization: HARD HOLD.** Targeted new Gmail searches for recent Inspire3 acceptance/affiliate tracking returned no qualifying messages; this is not proof of rejection. Partner dashboard authentication, Final Vestige-specific publisher acceptance, permitted website/social/**EMAIL** channels, issued earning URL, exact tracking attribution, settlement terms, approved creatives, tested cart and return execution remain unknown. A legitimately sellable, rights-cleared FV Payhip Mind SKU is not authenticated either; therefore no fallback purchase CTA is approved. Owner: founder + Commerce. **Do not build a false checkout or activate an outbound link.**

No advertiser-supplied “swipe” copy is authenticated as permitted. Do not use unknown creative assets or reproduce its urgency, safety, health, income or performance claims. FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Existing high-intent buyer guide: do not multiply competing pages

The actionable A/B candidate is already source-controlled:
- **A text:** `mind/r237/zen12-presell-A.html` describes actual listed package, reasons to choose or skip, a useful free twelve-minute alternative, refund caveats, prospective near-button FTC disclosure and disabled button.
- **B video concept:** `mind/r237/zen12-presell-B.html` retains the **exact same buyer text** plus optional original 42-second static storyboard and transcript. `mind/r237/zen12-42s-concept.vtt` provides seven cues spanning exactly 0–42 seconds. No actual MP4/WebM exists. No media autoload, JS, third-party video, active merchant anchor or published A/B; cinematic concept must be rendered and independently caption-reviewed before any test.
- **Mind hub:** existing canonical source proposal PR #172 stays owner-controlled. The R237 HTML preview is source-only, **not** a saved WordPress draft and does not supersede #172.

**Recommended buyer-message sequence:** “The first twelve minutes do not need to be perfect” → show a free, nonmedical observation exercise → differentiate repeating a routine from demonstrating a scientifically validated effect → exactly what the merchant lists (12 levels, four styles, 48 MP3s) → who may not need it (free timer works, already has recordings, expects a treatment) → seller-advertised one-year guarantee, with actual cart/fulfillment and exclusion terms **unverified** → **disabled** purchasing intent module. Do not show price, invented discount or terms until final authenticated checkout proof and seller authorization. Document the merchant's independent newsletter/free-audio opt-in separately; joining that list is not a Final Vestige Jetpack lead.

**Prospective commercial module (text contract):**

> Considering Zen12 Premium's audio-library format? The seller lists a twelve-level program with 48 MP3 files. Scientific evidence cited here does not establish the seller's promised mental-health or cognitive outcomes. Check final checkout and refund terms yourself. **If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you.** [Explore the Zen12 Premium offer — **UNAVAILABLE until publisher approval and verified link**].

This is an *implementation example only*, **not a currently enabled merchant link**. When approved, the actual CTA needs the clear disclosure **immediately before the clickable anchor**, `rel="sponsored noopener noreferrer"`, legitimate authorized URL, readable external-domain cue, distinct hover/focus state and no hidden redirects. Where link terms forbid added tracking parameters, use the original approved link. A dedicated review must evaluate message matching at the final destination. **Clicks do not prove purchases.**

## Three creator-topic → editorial → legitimate next step mappings

| Candidate EXISTING Grok topic; spoken-hook proof required | Editorial destination | Value and next action | Possible commercial relevance | Verification state |
|---|---|---|---|---|
| “Spot what changed” flicker or door-swap | https://finalvestige.com/2026/11/02/change-blindness/ | Full primary-method explanation and optional free https://finalvestige.com/focus/ | Only optional structured-audio guide for a reader independently interested in routines; NEVER assert Zen12 fixes blindness | Existing publication VERIFIED; **no Grok asset ID** |
| “What did Franklin's 1784 investigation actually show?” | https://finalvestige.com/2026/11/02/mesmerism/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Historical commission and original Puységur source exploration | Optional separately vetted Hypnosis Live Total Focus buying decision ONLY with active permission; NO clinical or history-to-efficacy leap | Editorial routes known; **no Grok asset ID** |
| “Twelve minutes to begin a task” | https://finalvestige.com/focus/ | One existing 52-page Fieldbook; existing Jetpack/Dispatch only | If a visitor asks for varied audio, optional Zen12 offer guide (not live). Not a cure nor hour-equivalence | Free route known; **no Grok asset ID** |

A **gorilla/inattentional-blindness** article is proposed in `mind/r239/GORILLA-IN-THE-SCAN-UNPUBLISHED.md`. It is editorial-only and **NOT** the current live Change Blindness article; no social link may point to an invented public gorilla permalink. Screen existing unpublished drafts for collision before choosing a canonical release. The other known editorial collisions require reconciliation: R211/R238 Coué, R196/R236 attentional blink, R237/live Mesmerism.

**Coordination handoff to Praxxis/Grok TASK-008:** Ask ONLY to reconcile already-published platform URL, media ID, date, spoken hook/transcript, rights, permitted UTM/bio pathway and actual in-app mobile URL. Grok retains creation and distribution; do not post or modify queue. Founder controls posting. Dispatch #174 controls email manuscripts, subscriptions and send approval. Do not replace the single Focus welcome email, duplicate Jetpack signup, or add paid SaaS.

## Privacy-preserving conversion evidence contract (design only; Claude owns implementation)

Existing analytics first: inspect deployed first-party/Jetpack/Ahrefs configuration; **never add a second tracking script** just to satisfy this packet. Where supported and consented, identify an inbound campaign by allowlisted query parameters `utm_source` (platform), `utm_medium=organic_social`, `utm_campaign` (predeclared cluster), `utm_content` (verified Grok `asset_id`). Reject unknown query values and cap lengths. Preserve source page route, cohort and anonymous aggregate event counts. Do not persist IP addresses, email addresses, user-agent fingerprints, unique per-person click IDs or cross-site identifiers in the Mind ledger.

Distinct measured steps with evidence classes:
1. **qualified_human_session:** explicitly filter verified internal/test traffic and known bots; don't equate Jetpack view with unique human.
2. **landing_view:** valid destination and matching creator hook; can be checked before activation.
3. **guide_cta_click:** actual first-party transition to free Fieldbook or reviewed buyer guide.
4. **confirmed_lead:** recorded by existing Jetpack provider after applicable consent/confirmation, never just visible form success; count duplicates and anomalies separately.
5. **affiliate_click:** only actual authorized external link events, if existing analytics can measure; not partner money.
6. **checkout_start:** only authoritative merchant signal, not inferred from a click.
7. **paid_order:** confirmed owned-product order or reported paid affiliate conversion, not a cart or form.
8. **cleared_commission** and **refund/fees:** ledger-confirmed payment facts, with attribution and reconciliation gaps explicit.

**Primary KPI (7-day and 30-day windows)** = 1,000 × (cleared receipts or commissions minus refunds and fees not already withheld, plus any attributable incremental costs deducted once) ÷ qualified-human sessions. If denominator or independently settled revenue is missing → **NOT COMPUTABLE**. Record missing as NULL rather than numerical zero. Supporting measures: checkout-to-paid, paid customers, acquisition cohort, confirmed-lead to paid, refund rate, net per cohort and confidence. With tiny denominators report observed counts and interval uncertainty; do not declare a winning creative based on two people.

## Unlaunched A/B design and test acceptance

**Hypothesis only:** a source-respecting optional 42-second original clip may improve completed paid purchases compared with equal text alone for qualified visitors considering a library of meditation audio. It could also delay reading or reduce conversions. Do not predeclare B the winner.

When founder release and affiliate account verification exist: identical variant text/offer/disclosure; only B adds optional **locally hosted, click-to-play, captioned, transcript-accessible** clip. Randomize 50:50 in an approved non-profiling way; stable aggregate variant cohorts; document exclusions and UTM source integrity. Precommit to **merchant-verified paid rate** as primary outcome, not clicks or form leads; review 7-day and 30-day cohorts. Monitor refunds and net revenue, not only first transactions.

QA gates requiring actual evidence, not static assumptions: 360/390/768/1440/1920 viewport captures, 200% zoom, accessible heading sequence, 44px target sizes where relevant, no horizontal scrolling, WCAG 2.2 AA contrast and focus, keyboard-only, `prefers-reduced-motion`, no-JS, video captions and transcript review, screen-reader/aria state, CSP/no executable embedded markup, real mobile embedded-browser /focus/ path, no autoplay or heavy initial fetch, WordPress sanitizer fragment survival, campaign allocation correctness, no double conversion counted, link disclosure visually adjacent, consent and merchant-cart checkout, visual QA by #126 and founder.

**Current execution scope:** source-only regression. Real browser, CI, production WordPress, completed film, paid checkout and provider-confirmed revenue remain **NOT TESTED**. Do not silently convert BUILT to LIVE or VERIFIED.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Next controlled experiment/change | Evidence state | Owner |
|---|---|---|---|---|---|
| Zen12 Premium | Eligibility → authorized link | Named partner acceptance, website/social/email rights and link absent | Authenticate real account and written terms; then confirm exact merchant destination | **HARD HOLD** | Founder / Mind |
| FV-owned Mind guide | Checkout | Eligible rights-cleared SKU unverified | Read authenticated Payhip inventory, rights, taxes/refunds, actual fulfillment and one test order only if separately approved | **UNKNOWN / NO ACTIVATION** | Commerce |
| Zen12 A vs B | Guide → purchase | No affiliate authorization; B not a playable video | Preserve text parity and build artifact under QA, no A/B deployment | **BUILT SOURCE / NOT LIVE** | Mind / Site QA |
| Grok → article → Focus | Human landing → confirmed lead | Asset IDs, in-app path, Jetpack acceptance unverified | Existing asset reconciliation + provider confirmation without duplicate signup | **UNVERIFIED** | Grok / Praxxis / Claude |
| Paid order → net | Settled revenue | Merchant/Payhip records, fees/refunds and denominator absent | Authoritative 7/30-day cohort reconciliation | **NOT COMPUTABLE** | Commerce / Analytics |

## Release and collision boundaries

All sixteen commercial gates in `mind/r239/CLAIM-SOURCE-OFFER-AND-REVENUE-GATES.json` are HARD_HOLD. No WordPress CMS/nav/settings, Jetpack, Dispatch newsletter, affiliate merchant, email, Grok queue, scripts, payments, homepage PR #49, Mind hub #172 or issue #150 edits. No live testing of a checkout; no commissions assumed. Founder approval remains mandatory for production or sale activation.

**Independent Praxxis correction:** Prior R238 source QA found three edited R237 artifacts had stale FNV integrity pins, and R238's plan assertion could pass the empty string. This isolated branch refreshes the exact reviewed pins, replaces the broken assertion, adds negative empty-plan tests and introduces deeper complete-registry drift controls. Earlier R237/R238 results cannot be cited as proof those inherited tests would pass at the new head until actually rerun.