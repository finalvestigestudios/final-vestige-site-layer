# R17 — Zen12 presell conversion, optional film and evidence-first navigation specification
**Owner:** Mind & Affiliate Studio only · **Status:** UNPUBLISHED · **Release:** HOLD · **First checked:** 2026-10-31  
**Protected:** PR #49 homepage; Issue #150 art; PR #172 Mind hub; Issue #174 Dispatch; current live CMS/Jetpack Focus configuration.

## 1. Product-specific source and audience fit
**Offer:** Zen12, not Hypnosis Live Total Focus or Brainwave Shots Focus Shot. Sources: official [Inspire3 catalog](https://inspire3.com/), [Zen12 About](https://zen12.com/about), [exact Zen12 checkout](https://zen12.com/getstarted). Checked 2026-10-31. The checkout advertises 12 levels/48 MP3s, companion materials/support and live checkout sales content. The about page advertises four formats per level—relaxation music, guided meditation, white noise, nature sounds—with 12-minute listening sessions. It also markets 12-minute equals 1-hour equivalence, guaranteed automatic brainwave effects and wide mental/health gains, **not independently substantiated for the exact bundle**. No fixed pricing, discounts, checkout countdown, refund period or celebrity endorsements in publishable copy. Seller's own text is documentation of **what the merchant says**, not empirical proof.

Audience motivation: readers interested in a **repeatable 12-minute audio routine**, not people seeking a cure or guaranteed faster-than-meditation results. Real objection: will they pay for audio when a free timer works? Original answer: if variety of short structured files is valuable, weigh that practical convenience against cost and unverified benefits. No borrowed approved swipe file, no marketing rights assumed. Final Vestige has no documented firsthand Zen12 user testing.

## 2. Editorial architecture
Entry: TikTok/organic search on "invisible gorilla explained", "why people miss a gorilla when counting passes", "monkey business illusion other changes", "radiologist gorilla CT study" (candidate topics, NOT claimed keyword volume). Canonical published article is still **pending** and must not receive a fake public slug.

The user reaches an independently useful >1,800-word sourced investigation; sees original 2010 attention reversal, a clear 2013 expert qualification, and two-minute **free** observation exercise; can link to already-live [Puységur](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) for methodology, and [Focus](https://finalvestige.com/focus/) for a practical free resource. Then, distinctly separated below the investigation, may read a Zen12 choice guide—without mandatory email opt-in. Guide headings and recommendations must be neutral enough that a user who never buys still gains value.

Suggested future /mind/ hub cards, not live navigation writes:
- Attention & perception: new gorilla investigation; the source-controlled attentional-blink, change-blindness, McGurk, Thatcher and Stroop investigations **only after individual publication**, otherwise do not link as live URLs.
- History of suggestion: published Puységur archive and future vetted Mesmer/Franklin pieces.
- Reflection: Focus Fieldbook as the **single** signup pathway.
- Tools under review: Zen12 format review, Hypnosis Live Total Focus, Brainwave Shots Focus Shot, each anchored to exact merchant offer, each with near-link disclosure and activation hold until approval.

Article SEO draft: title "The Invisible Gorilla, Explained: Why Knowing the Trick Doesn't Make You See Everything" (66 chars); description "The 1999 gorilla study was only the beginning. In 2010, familiar viewers still missed other changes; in 2013, experts faced a different test." Proposed slug `/mind/invisible-gorilla-attention/` only after founder route review. No fake ratings, no Product/Review schema, no unsupported medical FAQ markup.

## 3. Pilot question
**Hypothesis, not a known result:** does an original, useful, optional 40-second silent video in a Zen12 buyer's guide improve *informed progression* to an approved product link, compared with the identical useful text guide? Both arms must contain **exactly the same core visible text**, current evidence, disclosure and accessible source list. No A variant deliberately worsened to flatter B.

A = full standalone textual Zen12 guide; article, demonstration, official feature summary, limitations, free alternative, seller/independent sources, clear inactive or authorized CTA as permitted.  
B = same exact wording and position plus a self-contained 40-second original film **as optional illustration**, no autoplay, no loop, no preloading of MP4 until user intent, full transcript available without JavaScript, native controls, VTT text cues and descriptive poster. Candidate film exists in review assets for prior [PR #229](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/229), not newly created here and **not hosted in this draft**. Its original poster and caption file must be obtained and audited before a real B render. Do not show a faux player or link to missing media.

### Conditional implementation only after staged review
```html
<!-- EXAMPLE ONLY: DO NOT PASTE LIVE OR ACTIVATE. Replace three placeholders only with verified self-hosted media URLs after review. -->
<figure aria-labelledby="zen12-film-caption">
  <video controls preload="none" playsinline
         poster="[VERIFIED_SITE_POSTER_URL]"
         aria-describedby="zen12-film-caption">
    <source src="[VERIFIED_SITE_MP4_URL]" type="video/mp4">
    <track kind="captions" srclang="en" label="English captions"
           src="[VERIFIED_SITE_VTT_URL]" default>
    <p>Video is optional. Read the full transcript below.</p>
  </video>
  <figcaption id="zen12-film-caption">Optional original 40-second film about attention; not a Zen12 clinical demonstration.</figcaption>
  <details><summary>Read the film transcript</summary>
    <p>Attention can make a room feel complete. In the 1999 experiment, viewers counted basketball passes while an unexpected visitor crossed the scene. Many missed it. Knowing to look for the gorilla did not reliably reveal other changes in a 2010 follow-up. A twelve-minute pause might fit your day. It cannot promise that you will notice everything. Zen12 sells twelve-minute audio sessions; the benefits claimed for those recordings have not been independently established here. Decide from the evidence—not the surprise.</p>
  </details>
</figure>
```
**Transcript and captions:** production film is intentionally silent, so VTT should caption essential *on-screen* text, not fabricate spoken narration. Preserve a meaningful textual alternative, checking synchronization scene-by-scene and not just VTT existence. A film about the gorilla may use original abstracts; never reuse protected experimental film, faces, audio, brand assets or testimonials without rights.

### Accessibility / performance gates
Actual checks on staged WordPress after Gutenberg processing: desktop and mobile 360,390,768,1440,1920; 200%/400% zoom and reflow; keyboard-only; visible focus; high contrast/forced-colors; screen-reader NVDA/VoiceOver; reduced-motion; video pausing/controls; caption sync (or full essential-text alternative if silent); media aspect ratio and caption contrast; no-JS transcript; no horizontal scroll; source links working and no target=_blank surprise. Poster responsive `width:100%;height:auto`, video maximum 40–45 seconds and locally hosted, WebP poster, compressed H.264 MP4, `preload=none`, no vendor embeds. Prefer no video if performance, reading continuity or accessibility regresses. **Do not assert any CWV/Lighthouse score without running real tests.**

## 4. Fail-closed ethical commercial block
Show clearly adjacent to any later authorized outbound merchant link:
> **Affiliate disclosure:** If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.

Then a relevant action such as **"Review the current Zen12 offer on the merchant site"**, with exact verified earning URL only after written account acceptance and SKU eligibility and permitted tracking terms. It must be identifiable as going off-site. If authorization missing, **disabled button with "Merchant link unavailable — verification pending"** and a free Focus alternative. A reference link in a source list is only a documentary citation, not the hidden checkout CTA. Do not append affiliate parameters to research sources or silently transform them into earning links.

**Hard commercial gate = all TRUE:** partner written approval, exact approved offer/SKU, permitted creative/video/social/email rights, approved tracking link & method, checkout/terms reviewed, claim/substantiation QA, accessibility/staging QA, founder approval. At present **every account-specific partner gate UNKNOWN/HOLD**. No promises about earnings, products, specific reader experience, consumer results, pricing, discounts, refunds or limited-time offers.

## 5. Privacy-safe experiment; disabled until authorized
Avoid collecting email, full URL/referrer strings, IP, IDFA, cookies, localStorage, fingerprint or individual user journeys. Do not expose a user-level pseudonymous ID. If experiment has approval, use server-side randomization with *coarse aggregate buckets* rather than browser persistence; disclose allocation limitations (return visitors can see different arms). Options include sequential matched-period comparison if traffic too sparse, but confounding must be documented; no certainty claims from before-after alone. Do not implement tracking until there is a legitimate lawful basis and an actual review.

Pre-register:
- Primary: among consented and eligible visits, proportion of sessions invoking *an approved outbound CTA*, **not purchases**.
- Secondary: engagement with the free exercise, link to existing Focus, and manually started video, aggregated; source category `organic/search|short-form|internal|other`, not raw query/referrer.
- Guardrails: no decreased source-link interaction, no degraded WCAG/JS-off usability, no CWV regression beyond predefined thresholds, no bot/PII collection, no duplicate Focus forms.
- Never call a click a purchase or infer revenue, commission or conversion from outbound events. Partner-provided aggregate sales (if available and permitted) are a separate reconciliation lane.
- Predefine required sample size and time horizon using conservative baseline and minimum worthwhile detectable change **only after real traffic baselines**; no invented sample/p-values. Report effect uncertainty and design limitations. With low traffic, prefer qualitative usability interviews rather than false statistical certainty.

Security: no third-party JS, tracking image, hidden redirect, cloaked link, user query parameter or raw checkout logging; `rel="sponsored noopener noreferrer"` only for approved earning links if external new-tab usage is required (default same-tab simpler); approved merchant domain allowlist; never allow arbitrary user-provided URL in CTA. Any instrumented outbound event must be explicitly reviewed and turned on by a separate approved release. Current privacy module stays **OFF**.

## 6. Readiness and coordination
**Evidence:** primary journal studies https://doi.org/10.1068/p281059, https://doi.org/10.1068/i0386, https://doi.org/10.1177/0956797613479386; seller https://inspire3.com/ , https://zen12.com/about , https://zen12.com/getstarted ; NIH https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety ; FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

Send site QA #126 the isolated branch, primary sources, exact QA script, the inactive CTA, no-JS schematic and the staged-film gate. Ask homepage art #150 for nonblocking visual consistency feedback ONLY, without changing their branch/PR #49. Dispatch #174 may reference the already-published Focus/Puységur links and source studies, **not unpublished drafts or outbound affiliates**. Leave six Dispatch issues and the existing Jetpack welcome untouched.

**Release: HOLD.** No CMS edits, nav writes, campaign sends, tracking, external sales or deployment have been authorized in this branch.