# R402 conversion acceptance and creator-routing contract
*2026-11-15 PT | Mind & Perception only | source-controlled DRAFT | release HARD HOLD*

## Decision that matters this sprint

**Official merchant-format correction:** Brainwave Shots' FAQ describes **isochronic tones**, not binaural beats, and says headphones are not required: https://brainwaveshots.com/faq . The Focus Shot product page says its 30-minute protocol alternates between 12 Hz and 18 Hz, but no authorized file waveform was inspected: https://brainwaveshots.com/focus-shot . Prior Mind buyer guides commonly cited binaural-beat studies. They may remain as clearly labeled *background auditory science*, not as validation of Focus Shot. R402 establishes this cross-modality firewall in the article and claims matrix. Site QA should search existing pending guides for phrases that infer isochronic efficacy from binaural results, correct those before any publication, and not overwrite owner branches.

**Revenue obstacle:** Public Inspire3 affiliate portal https://affiliates.inspire3.com/ describes generic participation. It does not establish Final Vestige-specific approval, earned commission, authorized Zen12 SKU or permitted social/email channels. Targeted connected Gmail search returned consumer and promotional material, not a private publisher authorization or earning URL. Absence in that search does *not* prove none exists elsewhere. No currently payable rights-cleared FV-owned Mind product was independently authenticated; the 52-page Focus Fieldbook is free. No commercial offer can responsibly be activated yet.

The near-term useful live destination remains the existing Focus Fieldbook, but **confirmed lead is not assumed**, and *lead is never paid order*. Pilot A/B development is valid as pre-release engineering, not proof of sales.

## Exact offer-to-audience fit (qualified, not imaginary)

| Original Grok candidate topic (research-only, not a new posting assignment) | Verified canonical reader destination | Reader question | Free pathway | Optional verified product only after authorization | Status |
| --- | --- | --- | --- | --- | --- |
| Change blindness: "Why did the person vanish from the scene?" (source topic: Simons & Levin 1998) | https://finalvestige.com/2026/11/02/change-blindness/ | Can I improve my ordinary attention without being sold a miracle? | https://finalvestige.com/focus/ | Zen12 structured meditation course, with separate limited evidence review | Article LIVE; actual Grok media ID / permission / landing sessions UNVERIFIED |
| Franklin's 1784 blindfold experiments: "What did the apricot tree really prove?" | https://finalvestige.com/2026/11/02/mesmerism/ → https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | What is hypnosis, and how can I avoid confusing suggestion with treatment? | Same Focus Fieldbook, optional not mandatory | Hypnosis Live Total Focus, *only* for audience interested in a guided file rather than proven therapy | Canonical article LIVE; Grok asset ID UNVERIFIED |
| Product science: "Why are 12–18 Hz on an audio product page?" | R402 unpublished scientific article; **do not route traffic to a draft or fabricate a live URL**. Interim relevant live destination: https://finalvestige.com/focus/ | Does rhythm improve focus or is it only a marketing specification? | Same Fieldbook and free baseline | Brainwave Shots Focus Shot, described as isochronic by seller; no binaural-study efficacy inheritance | Source-only article, no published social route and no product permission |

The candidate phrases above are research/editorial recommendations to Praxxis for its existing Grok TASK-008 https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit and dated handoff https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit . **No asset_id, media ID, posting schedule, social copy or rights assertion was invented.** Existing creator team must supply an actual public immutable media ID, exact hook, published URL and permission before an asset-specific UTM is assigned.

## One high-intent Zen12 pilot

- **Audience:** a reader who has tried to work in silence, wants a practical repeatable session format, and is now comparing downloadable meditation courses rather than seeking treatment.
- **Landing draft A:** `ZEN12_TEXT_A.html` full, honest, evidence-first text guide.
- **Landing draft B:** `ZEN12_OPTIONAL_FILM_B.html` with **identical shared buyer content** plus an original static 16:9 poster, 87-word 42-second voiceover storyboard, visible accessible full transcript, and six contiguous WebVTT cues.
- **No encoded or playable film exists.** B is a concept, not an actual video test. Require a rights-cleared rendered asset with `preload="none"`, `controls`, captions, poster, no autoplay, local origin, CSP-safe loading, content sizing, mobile/LCP budget and transcript preserved after media creation. Do not force playback.
- **Actual live destination in each draft:** existing, free https://finalvestige.com/focus/ using the same Jetpack list.
- **Merchant button:** native `disabled`, no earning `href` or seller checkout hyperlink. Disclosure immediately beside it: "If Final Vestige later offers an approved purchase link and you buy through it, Final Vestige may earn a commission at no extra cost to you."
- **Product source matches:** https://zen12.com/getstarted standard public order shows 12 levels / 48 MP3s, seller snapshot total $87.99 before tax (subject to change). https://zen12.com/secret/ is a separate coupon/sales presentation. Neither is FV-referred checkout evidence.
- **Refund limitation:** seller states a guarantee but buyer must review complete current terms; do not invent actual refunds, use testimonials as neutral proof, or present seller urgency as our own.
- **Controlled experiment hypothesis:** After all commercial + release gates, A/B compares whether useful optional video improves *verified paid orders per qualified-human session*, without reducing comprehension, causing abandonment, damaging CWV or increasing misleading clicks. Pre-register assignment and attribution; text-copy parity except video block; equal CTA/disclosure and offer eligibility. A/B is **not ready to enroll** now.

## Measurement contract: paid settlement beats click dashboards

A qualified human session may be attributed to one real Grok asset only when its click path actually supports the asset-specific URL and permitted URL format. Candidate first-party parameters: `utm_source=youtube|tiktok`, `utm_medium=organic_social`, `utm_campaign=mind_<topic>_2026_11`, and `utm_content=<verified_asset_id>`. Any source is *unattributed* if channel-profile navigation, webview stripping or missing ID makes assignment ambiguous. Do not infer an individual video's paid conversion from the channel that delivered a view.

Read-only stages, each a separate fact with proof and timestamp:

1. Consent-appropriate qualified-human `landing_session` with approved first-party campaign ID and bot filtering. Unknown until actual data.
2. Relevant `mind_guide_cta` to canonical page. A click is not a lead, sale or proof of delivery.
3. `focus_request` (form submit observation where permitted); still **not** a confirmed subscriber.
4. `focus_provider_confirmed` from Jetpack's existing provider consent/confirmation status, with correct opt-out and no PII in analytics; source join only if permitted and technically verifiable. If not joinable: report lead aggregate separately.
5. `affiliate_click` only after authenticated publisher approval and actual activation, distinct from step 6; no scripts added by this lane.
6. `merchant_paid_order_confirmed` / `merchant_commission_settled` from independently trusted merchant or FV-owned seller ledger, within approved partner terms, then `merchant_refund_or_clawback` and payment fees. Never derive these from web analytics alone.

**Primary KPI:** `1000 * (settled attributable publisher commission + realized attributable FV-owned order margin - refunds - fees - chargebacks) / qualified_human_sessions`. Calculate 7-day and 30-day *mature cohorts* only, use merchant reporting cutoffs and explicitly state pending refunds/attribution loss. For paid conversion rate use independently confirmed paid orders ÷ qualified-human sessions; for lead-to-customer require consent-appropriate, actually joinable confirmed leads and customers. Suppress rates or flag huge uncertainty for tiny cohorts; if denominator, paid ledger or authorized join absent, KPI = **NOT COMPUTABLE**, not $0. No cookie fingerprinting, no PII in UTM, no unapproved duplicate analytics SDK.

The opt-in email list is the **one existing Jetpack/Dispatch system**; do not add another lead form, replace Focus welcome, send campaigns, or edit Dispatch issues. Claude owns production analytics/engineering; Dispatch owner controls emails; Praxxis/Grok own social; founder owns commercial and release approval.

## Acceptance and release firewall

| Priority | OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | CURRENT PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| P0 | Zen12 → authenticated payable commission | No named FV publisher/Zen12 SKU channel/earning URL | Private partner approval, approved URL + sub-ID, permitted social/email channel rights, referred checkout, returns, settlement reporting | **HOLD**, public portal and consumer email do not suffice | Founder/Commerce |
| P0 | Existing FV-owned Mind product → payable order | Rights-cleared active SKU, delivery and return evidence not authenticated | Verify one actual saleable asset end-to-end before substituting it for Zen12 | **HOLD**, no active owned SKU proof; free Fieldbook not paid | Founder/Commerce/Claude |
| P1 | Exact product-claim → independent buyer guide | Isochronic Focus Shot was incorrectly liable to be equated with binaural research | New R402 modality boundary and claims matrix; audit other draft guides | **SOURCE BUILT**; article and matrix require editorial/QD review | Mind/Site QA |
| P1 | Grok asset → qualified live article | No actual linked media IDs and rights | Praxxis verify 3 original public IDs, claims, timestamps, destination, real clickability | **HOLD** media ID unknown; no publishing action | Praxxis/Grok |
| P1 | Article → confirmed free reader | Actual Jetpack provider lead/delivery not checked | Test existing confirmed opt-in + welcome + free PDF without duplicating list | **HOLD** provider and email tests unexecuted | Claude/Dispatch |
| P1 | Guide text vs. optional film → paid checkout | No authorized merchant, playable film or consent-safe join | Only after gates, limited random assignment with A/B text parity and both mobile accessible | **NOT RUN**; storyboard B only; no sale test | Mind/Site QA/Commerce |
| P1 | Settled transaction → net revenue | No merchant-paid ledger or qualified-human sessions | Reconcile 7-/30-day cohorts including fees, refunds and reversals | **NOT COMPUTABLE**; no paid transaction proof | Commerce/Claude |
| P2 | Mind archive → navigation | Published /mind/ route and CMS sanitizer review absent | Source-only responsive four-stream hub, then owner review; no menu/homepage edits | **BUILT SOURCE ONLY**; no CMS draft saved | Mind/Site QA/Homepage art |

## Reproducible pre-release tests

`node mind/r402/verify.mjs` from repository root uses only Node built-ins. It verifies:
- UTF-8 and structure; citation source URLs; modality-specific wording;
- no executable scripts or external video/embed, no active merchant `href` in A/B;
- accessible native disabled merchant controls; adjacent disclosure;
- exact text parity under `id=shared-buyers-guide` in A/B;
- B visible transcript and VTT text match, six contiguous seven-second cues totalling 42 seconds;
- no duplicate form, no autoplay, no redirect, no unauthenticated sales link;
- claim matrix 20 HOLD gates, source provenance, prohibition on categorizing seller claims as direct research proof;
- hub canonical links without speculative /mind/ destination.

The verifier is a static safety net, **not** actual WCAG audit, real browser/CWV, CMS sanitization, media playback, provider consent, merchant checkout, transactional or marketing outcome test. Site QA must inspect at 360, 390, 768, 1440 and 1920px; 200% zoom, keyboard, screen reader, low bandwidth and reduced-motion.

## Scope and coordination boundaries

Only `mind/r402/` additive, isolated. Do not touch homepage PR #49, issue-owned homepage art #150, canonical Mind hub PR #172, newsletter Issue #174 copy, Grok TASK-008 queue, existing Jetpack Focus welcome, WordPress menus/settings/live pages, paid accounts, or any production trackers. No merge, deploy, publish or affiliate activation without explicit founder release approval and the missing commercial documentation.

Links for review: founder charter https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818 ; conversion controls https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820 ; Mind source of truth https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 ; Dispatch https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; site QA https://github.com/finalvestigestudios/final-vestige-site-layer/issues/126 ; homepage art https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150 .
