# Mind R397 — conversion-first acceptance, attribution and creator handoff

**Date:** 2026-11-15 America/Los_Angeles. **Status:** SOURCE-CONTROLLED DRAFT / HARD HOLD. This document defines an experiment; it is not an analytics deployment, consumer email, partner acceptance, live WordPress draft or released landing page. No real conversion evidence was obtained.

## The business decision, before more design

**Candidate offer:** Zen12 Premium, a seller-described twelve-level / 48-MP3 meditation-audio package. The audience is a person looking for a short, guided, repeatable listening routine, not a person seeking a proven cure, cognitive transformation, or a supernatural mechanism. **Hard blocker:** Final Vestige publisher acceptance, product-and-channel terms, earning URL, actual referred checkout, paid settlement and refund terms remain unauthenticated. No active purchase link may appear. A free, already published 52-page Focus Fieldbook exists and remains the only permitted immediate destination.

**Seller-price evidence is not a payable FV price:** The Zen12 catalog was displayed at $87.99, its retrieved direct order screen at $87.00, and a distinct coupon route at $37. We must not make a misleading specific-price promise, repeat seller urgency, or claim any coupon qualifies for FV. Seller advertises one-year refund, which is not a processed refund or an independently verified term.

**Fallback offer gate:** An FV-owned, actually purchasable, rights-cleared Mind SKU would supersede speculative affiliate warm-ups *only if* Commerce verifies the owner, intellectual-property license, checkout, published terms, delivery, refund method, fees and a test order. None was authenticated here. No substitute business has been invented.

## Creator topic → source article → noncommercial pathway → optional offer

Only *proposed topic matches*. An invented asset_id, video URL, or Grok upload will never be accepted. Grok owns creation/posting. Praxxis independently verifies actual published immutable asset_id, exact hook, rights, post time, working mobile URL and permitted campaign fields in the existing TASK-008. No creator assignment is made here.

| Candidate source-grounded creator hook (not a script) | *Already live* evidence destination | Reader's next useful step | Hypothesis for optional offer (ON HOLD) | Counterclaim to avoid |
|---|---|---|---|---|
| “How can a large change disappear from view?” | https://finalvestige.com/2026/11/02/change-blindness/ | Published science → optional https://finalvestige.com/focus/ | Zen12 if visitor independently wants guided short audio | “The change-blindness effect proves Zen12 strengthens attention” |
| “Why did Franklin test magnetism without assuming a magnetic force?” | https://finalvestige.com/2026/11/02/mesmerism/ | Experimental controls and historical source → optional free Focus | Hypnosis Live *Total Focus* only if exact SKU and mental-skills channel rights confirmed | “18th-century tests proved modern hypnosis MP3s work” |
| “When does a witness's extraordinary experience become evidence?” | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Source dossier: failures, predictions, consent → free Focus | Zen12/Brainwave Shots only where user intent genuinely matches and authorization exists | “Magnetic somnambulism confirms brainwave-audio effects” |

**Additional R397 research:** *The Face That Looked Normal Upside Down*, a new source-controlled Thatcher illusion article. **NOT LIVE**, so no public video may point at a fabricated article URL. Grok may consider it only after publication approval and independently checked destination. An original abstract orientation schematic is not a recreation of a validated stimulus.

## A/B hypothesis and implementation boundaries

- **A:** full independent text-only Zen12 buyer guide. It contains a no-cost activity, evidence/limits, seller-described package, distinct checkout price snapshots, buyer objections, close disclosure, and a truly disabled withheld merchant CTA.
- **B:** exactly the same substantive buyer text plus an optional, user-expanded, original schematic poster, 42-second transcript and six WebVTT cues. This is **storyboard-only**; no playable video file is built or shipped. In a future test, use user-initiated native video with local poster/transcript, preload='none', no third-party embedding, no forced play, captions, low-bandwidth fallback, and keyboard/no-JS support.
- **Testable hypothesis:** B improves **verified paid orders/net realized revenue per qualified-human session** versus A among matched high-intent visitors. This is not an asserted outcome. Risk: B may increase weight/load time or distract from independent evidence, producing lower conversion or worse accessibility.
- **Before experiment:** authenticate payable offer and founder approval; build original rights-cleared media; QA physical mobile widths 360, 390, 768, 1440, 1920; browser axe/WCAG 2.2 AA/manual keyboard and screenreader; test native page with script disabled; compare content parity and disclosure proximity; verify CPT/CMS sanitizer; test referral checkout in an explicitly permitted sandbox or approved real test flow, no card handling by FV.
- **Assignment:** ask Claude to reuse existing first-party measurement and allocation technology, not add new JavaScript, cookies, paid service or a second pixel. If no compatible consent-safe randomization is available, retain both as prototypes and mark A/B NOT RUN rather than pretending a controlled comparison. Never allocate by personally identifying parameters.

## Privacy-aware event contract (not deployed)

| Event name | Required data | Forbidden / caveat |
|---|---|---|
| `qualified_landing` | timestamp rounded by day, page_key, approved `asset_id`, `utm_campaign`, source platform, variant A/B if assigned, pseudonymous session_key if existing consent permits | no IP address, name, email, unique device fingerprint; separate known bot or non-human traffic |
| `focus_cta_click` | same campaign fields and destination logical ID `existing_focus` | a click is NOT a subscribe or confirmed lead |
| `jetpack_lead_confirmed` | event only from existing provider's consent/confirmation, aggregate campaign mapping when demonstrably feasible | no email address or signup claim from PDF visibility |
| `affiliate_click` | hashed or otherwise first-party nonidentifying campaign reference, merchant SKU logical ID, page_key, variant, day | **must never be called a paid sale**; no link cloaking or unauthorized redirect; currently NOT ACTIVE |
| `partner_paid_conversion` | independently reported order/commission settlement reference from authorized partner; consentful aggregation as legally permissible | may be unavailable; no invention from clicks |
| `owned_paid_order` | independent merchant-reconciled order status, SKU, gross revenue and fees without customer PII in analytics | requires actual rights-cleared FV paid SKU; NOT VERIFIED |
| `refund_or_chargeback` | aggregate transaction correction by eligible cohort and SKU | reduce realized net revenue |

**Required identity hygiene:** Use existing approved UTM conventions, never ingest arbitrary URL parameters from third parties into event labels. Bound and validate `asset_id` with Grok's actual immutable asset record and a short whitelist. Do not infer individual subscriber-to-buyer identity absent explicit lawful consent and reliable provider data. No event dispatch code is added in this PR.

**Metrics:** For each 7-day and 30-day matured acquisition cohort:
- Qualified-human sessions = consent-compatible, verified nonbot landing sessions with valid source asset and user interaction rules, counted once per existing first-party session definition.
- Verified paid conversion rate = (merchant-confirmed settled paid orders)/(qualified-human sessions); only if join is defensible.
- Verified lead-to-customer conversion = (confirmed buyers linked to confirmed consenting leads)/(confirmed leads with attribution rights); otherwise **NOT COMPUTABLE**.
- Realized net revenue = settled gross receipts or commissions **minus** refunds, chargebacks, platform/payment fees, affiliate adjustments and allocable direct acquisition costs when known. Costs and revenue cannot be invented as zero.
- **Primary KPI** = realized net revenue / qualified-human sessions × 1000; display with 7-/30-day window, denominators, cohort maturity and small-sample caveat. When source-to-order attribution is missing, show **NOT COMPUTABLE**, not zero or a guessed rate.
- Decision threshold for tiny samples: report raw counts and wide uncertainty; do not call an experiment a win before predeclared sample size, observation period, refunds lag, consent checks and quality gates. Never optimize solely for clicks.

## OFFER → STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL evidence → OWNER

| Priority | Offer → funnel step | Blocking issue | Proposed controlled change/experiment | Current proof/status | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → attributable paid commission | No FV account-specific acceptance, approved SKU/channel or earning URL | Obtain written partner authorization + actual referred checkout and settlement terms | **FAIL / missing authorization**; public portal and targeted Gmail do not suffice | Founder/Commerce |
| P0 | FV-owned Mind product → paid order | No authenticated payable right-cleared Mind SKU | Audit owned SKU, checkout, licensing, delivery, refunds and live terms | **UNKNOWN, HOLD** | Commerce |
| P1 | Grok post → source article | No authenticated Mind `asset_id` and route | Praxxis verifies 3 posts/rights/mobile destinations via TASK-008 | **NOT VERIFIED** | Grok/Praxxis |
| P1 | Article → confirmed Focus lead | Native Jetpack provider confirmation/delivery not tested | Reuse existing opt-in; test consent/delivery without replacing welcome | **NOT TESTED** | Claude/Dispatch |
| P1 | Buyer guide A/B → settled paid order | Only static guide and film concept, no authorized merchant | Build video; offline/browser review; authorized controlled experiment | **STATIC ONLY**, no live test | Mind/Claude/Site QA |
| P0 | Paid order → realized net | No orders, fee/refund settlement or matched human denominator | Reconcile 7/30-day cohorts with approved reporting | **NOT COMPUTABLE** | Commerce/Claude |

## Release constraints / handoffs

Do NOT change WordPress CMS/navigation/settings, existing homepage PR #49/Issue #150, canonical Mind PR #172, Dispatch Issue #174 or existing welcome message, Grok queue or live social content, paid acquisition, analytics production or merchant links. New source files only inside `mind/r397/` on an isolated draft PR. Site QA #126 reviews claims/disclosures and actual-browser performance. Homepage art owner receives only hub context, no homepage edit. Correspondence to #171, #820 and handoff Drive docs is research-only, not publication.

**Current observed inventory correction:** Connected WordPress read-only enumeration on 2026-11-15 returned **66 published posts and 92 published pages**, whereas Issue #171's founding snapshot reported 61 and 79. This is an inventory delta, NOT proof of 13 Mind pages. No published `mind` page slug was in the retrieved published pages. The historical 61-article brief was consulted; all 66 posts were enumerated but not each read in full. The live Focus and Puységur page content were read by WordPress directly.