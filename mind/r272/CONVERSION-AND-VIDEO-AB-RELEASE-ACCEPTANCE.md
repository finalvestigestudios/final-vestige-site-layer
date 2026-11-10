# R272 commercial acceptance, source repair and release plan
**2026-11-10 · Mind & Perception only · UNPUBLISHED · DRAFT · HARD HOLD**

## Decision: repair the existing purchase argument instead of adding another landing-page variant

The inherited R268 Zen12 A/B guides formerly used a semantic-satiation study (repeated words and EEG N400) as their lead scientific micro-story. That is a meaningful psychological effect, but it is **not** the evidence most relevant to a customer deciding whether “brainwave audio” justifies a purchase. R272 changes the identical science section in both inherited A/B guides to directly relevant 2023 binaural-beat EEG systematic review, 2024 auditory-arousal/cognition systematic review and randomized mindfulness-app meta-analysis. The new material explains perceptual beat -> EEG signal -> behavioral outcome -> named commercial product as four distinct evidence gates.

The rest of the buyer experience is intentionally stable. A remains text-only. B remains the same complete buyer guide with a 42-second original static poster and corrected transcript **concept**, not hosted playable video. A true video treatment cannot be claimed until an accessible native video file, transcript, timed captions, poster, playback/no-JS and performance have been independently QA'd. The existing R257 film is not silently treated as published media.

The Mind /mind/ source prototype is already in canonical PR #172 and prior Mind branch drafts; do not create a duplicate live hub or alter a real WordPress page. Homepage flagship PR #49, the art lead's #150, Site QA #126, Dispatch #174, and Claude's analytics engineering stay in their own lanes.

## Offer and audience before more pages

**One reader question:** “I am interested in a simple, structured meditation-audio library. What does Zen12 Premium actually provide beyond a free timer and what is the evidence?”

**Primary offer candidate: Zen12 Premium**, the exact standard seller proposition at https://zen12.com/hnp . The seller advertises 12 levels and 48 MP3s; an alternative https://zen12.com/secret/ is a separate coupon-framed proposition. These are **not interchangeable** campaigns. An accessible public page is not a verified publisher-specific earning link, partner approval, cart total, subscription/refund condition or verified deliverability.

**Fallback candidate: an FV-owned Mind digital product** only after independent verification of its rights-cleared product files, product identifier, published offer, actual checkout, delivery access and refunds. Earlier inventory described Products 001–015, but no eligible Mind SKU has been authenticated. The currently published **Seven Day Focus Fieldbook** is a **free** 52-page document and one existing Jetpack/Dispatch lead pathway; its downloads and subscribers are not paid orders.

**Alternative commercial products:** Hypnosis Live's *Total Focus* is a different 33-minute seller-described hypnosis recording with an exact offer at https://hypnosislive.com/mental-skills/total-focus . The directly extracted versus indexed pricing observations conflict (Dispatch #171 latest handoff); do not promote either price as an authenticated checkout. Brainwave Shots is a *family* on Inspire3's official catalog; do not build a product-specific offer guide until one exact authorized track and seller page are identified. Neither item substitutes for Zen12 Premium by default.

## The original CTA and the mandatory control

The proposed buying block on each R268 guide preserves a **disabled HTML <button>** with its explanation. This is an honest disabled control, not a spoofed “check out” link. The preceding and immediately following content explains which evidence is unverified. When publisher acceptance, exact issued earning URL, permitted WEB channel, accepted terms, checkout, claim substantiation and founder approval are verified, the owner may prepare a distinct production review of a legitimate <a rel="sponsored nofollow"> element. It should appear beside:

> If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.

Disclosure proximity is a necessary condition, not approval to make objective medical or financial claims. Ensure that the disclosure appears at the point where the reader can take an earning action, visibly and legibly on mobile, not only behind an expandable section or general policy page.

**Free route:** a plain first-party anchor to https://finalvestige.com/focus/ remains available independent of buying or joining the newsletter. Do not insert another signup form, import subscribers, fire email automations or modify the welcome message. A person may read the full report or purchase guide without submitting an email.

## Creator-to-product fit: three bounded research hypotheses

| Topic / actual corresponding editorial asset | Grok video / asset evidence required | Source-appropriate path | Offer fit |
|---|---|---|---|
| Change blindness; published https://finalvestige.com/2026/11/02/change-blindness/ | Published asset_id, original TikTok/YouTube URL, date, hook, image/video rights, signed-out mobile link | Relevant article -> optional existing Focus Fieldbook -> optional Zen12 buyer guide | **Low/medium hypothesis.** A perception illusion cannot establish product efficacy. |
| Attentional blink; R263 unpublished https://github.com/finalvestigestudios/final-vestige-site-layer/blob/42a1a653774aa524d3767e87207ac50ede46911a/mind/r263/THE-HALF-SECOND-YOUR-ATTENTION-COULD-NOT-KEEP-UNPUBLISHED.md | Same evidence, but **NO PUBLIC DESTINATION** yet | Keep creator handoff in HOLD; future editorial article -> Fieldbook | **Medium attention-topic fit, not causal audio evidence.** |
| Puységur / history of hypnotism; published https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Existing asset_id, published URL, chronology, permission, factual hook | Historical record -> related Mesmerism article -> existing Fieldbook; optional separately vetted hypnosis guide | **Medium interest fit / low efficacy proof.** Do not use historical testimony as medical evidence. |

Prax​​xis and Grok own creator ID inventory and original platform publication. This lane proposes *no* new social assignment. Existing Drive TASK-008 and dated handoff are the coordination surface; a real claim of campaign matching requires its actual data, not our thematic guess. Claude owns public analytics implementation, not this PR.

## Controlled A/B decision

**Hypothesis only:** For people arriving with meaningful interest in practical audio choices, the identical evidence-first Zen12 guide with an *optional* original 42-second video may increase qualified, genuine guide-to-purchase progression compared with text alone. It may also reduce performance and comprehension; that possibility must be measured.

- **A:** Complete text-only source guide.
- **B:** Identical copy, same source links, free alternative, FAQ, disabled commercial state and near-control disclosure, plus optional captioned, transcript-accessible 42-second asset. No forced or preloaded playback.
- **Primary commercial endpoint:** independently verified paid order or cleared affiliate commission net of refunds and fees, only once live approval exists. Pre-approval A/B is **not a commercial experiment**; only UX usability and synthetic QA may run.
- **Guardrails:** no extra JS analytics and no duplicate Jetpack list. Support no-JS consumption, accessible keyboard focus, captions/WebVTT matching actual media, transcript and reduced motion. Keep mobile LCP and CLS budgets; the video must be opt-in and lazy-load. Candidate widths: 360, 390, 768, 1440, 1920 px. Test touch and screen readers, real browser and WordPress sanitizer under Site QA's control.
- **Experimental integrity:** randomize only with authorized consent-appropriate first-party mechanism; keep eligibility and traffic-source definitions comparable, preserve asset_id and variant only as non-PII aggregated reporting; pre-register the success criterion and the stopping rule. No inflated “winner” from tiny samples. A B variant showing a *poster only* is not the requested video-versus-text treatment and must be marked NOT TESTED.
- **Security:** no inline playback scripts, no form injection, no third-party beacon/pixel, no SVG external reference, no programmatic redirects, no open target; require rel="sponsored nofollow noopener noreferrer" on any future earning link (subject to actual partner terms). No external URL is active as an earning URL here.

## Event and revenue measurement contract — do not install a second tracker

Claude / Issue #820 is the authoritative analytics implementation owner. This document is a **schema proposal and acceptance test**, not a script deployment.

- Approved standard UTM idea: `utm_source=tiktok|youtube&[verified source]&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=<actual_published_asset_id>`. Only implement paths supported by the posting platform and the real Grok asset inventory. Do not invent asset IDs.
- **Qualified-human sessions**: deduplicated, consent-respecting, bot-filtered visits under one documented definition. A pageview is not a qualified human session. If the source platform prevents direct links, document the bio link intermediate steps rather than inferring attribution.
- **Landing visit -> editorial CTA -> Focus confirmed subscriber**: first-party events where observable, source-joined only at an aggregate privacy-safe level. Do not assume a form submission is confirmed by Jetpack or that a PDF download is a subscriber.
- **Commercial**: `affiliate_outbound_click` is *not* `affiliate_sale`; `checkout_start` is *not* `merchant_confirmed_paid_order`; `merchant_confirmed_paid_order` is *not* `settled_net_revenue`. Independently confirm gross order, paid status, commission recognition, refunds and fees from merchant-accessible records. Do not request sensitive individual visitor data to “fix” attribution.
- **KPI**: `1000 * realized_net_revenue / qualified_human_sessions` for fixed 7-day and 30-day acquisition cohorts; report underlying counts, product margin/refunds, attribution coverage and confidence warning. When either the numerator or denominator cannot be authenticated, **NOT COMPUTABLE** is the only defensible outcome; never quietly replace missing values with zero.
- **Synthetic QA fixtures**: exercise authorized/no-authorized link toggle; bot-like visit exclusion, duplicate event idempotency, misattributed medium, user who never confirms signup, click with no sale, refunded sale, net negative sale and zero qualified-session denominator. No real purchase without approval.

## Release acceptance — prioritized blockers

| Offer -> funnel step | Blocker now | Change or experiment | Pass / fail evidence | Owner |
|---|---|---|---|---|
| Zen12 -> eligible recommendation | No named FV acceptance, issued URL or channel rights | Independently authenticate account-specific agreement and exact earning link | **FAIL/HOLD**: public portal and promo email are not acceptance | Founder + Mind |
| Zen12 -> real payment | Standard and coupon paths differ; final checkout/refund unknown | Verify selected authorized offer, eligible cart, fulfillment and refund conditions | **UNTESTED/HOLD** | Founder + Commerce |
| Owned Mind product -> checkout | No rights-cleared live eligible SKU independently identified | Read actual existing Products 001–015, Payhip and license inventory | **UNVERIFIED/HOLD**, not “no sales” | Commerce |
| Grok -> qualified page | No authenticated exact matching asset IDs and destination receipts | Grok/Praxxis verify preexisting media only | **NO VERIFIED MATCH** | Praxxis + Grok |
| Article -> Focus/Dispatch | Confirmed lead attribution not reconciled | Validate existing one-list route and provider-confirmed delivery | **UNVERIFIED** | Claude + Dispatch |
| Optional film -> guide comprehension | Hosted playback, no-JS and signed-out accessible browser untested | QA exact 42-second asset vs A | **NOT A LIVE VIDEO TEST** | Site QA |
| Guide -> actual earnings | No paid transaction/commission and fee/refund reconciliation | Merchant report + controlled 7/30-day cohort | **NOT COMPUTABLE** | Commerce + #820 |
| Independent governance -> release | Founder release approval absent | Site QA acceptance, editorial + merchant rights, founder release decision | **HARD HOLD** | Founder |

## Ownership and evidence custody

- **BUILT (repository)**: R272 corrected the inherited two guides in an isolated Mind branch; added new original long-form investigation, source matrix, contract and independent QA suite. Branch SHA and execution results are recorded in Issue #171 and #820 when verified.
- **TESTED (source-level)** is not a complete mobile, merchant or video acceptance.
- **LIVE**: the previously existing free Fieldbook and historical research only; none of R272 is published.
- **VERIFIED NET REVENUE**: unknown; not evidenced by email promotions, pageviews, click counts or hypothetical conversion rates.

No WordPress CMS, menus, homepage PR #49, Mind hub PR #172, art lead #150, newsletter, social production, tracking vendor, spend, payment setting, deploy or merge is authorized by this document. Editorial conclusion and affiliate commercial copy remain separate; this PR is a review proposal only.

### Exact live source/official research register

[FTC Affiliate Endorsement FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) · [FTC Health Guidance](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance) · [Inspire3](https://inspire3.com/) · [Zen12 standard](https://zen12.com/hnp) · [Zen12 promo](https://zen12.com/secret/) · [Total Focus](https://hypnosislive.com/mental-skills/total-focus) · [EEG review](https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/) · [auditory review](https://pubmed.ncbi.nlm.nih.gov/38458383/) · [meditation-app RCT review](https://pubmed.ncbi.nlm.nih.gov/33049431/) · [NCCIH](https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety) · [live Fieldbook](https://finalvestige.com/focus/) · [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) · [Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
