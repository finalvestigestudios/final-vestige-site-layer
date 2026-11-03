# Mind R104 — Founder / Independent QA / Art / Dispatch review handoff

**Status: DRAFT ONLY, HARD HOLD. No WordPress, newsletter, menu, analytics, link or homepage production changes.**  
**Scope:** New independent investigation about choice blindness; exact-offer Zen12 editorial buyer guidance; unpublished accessible A/B pilot; four-stream hub *alternative* only; claim evidence register; disabled, synthetic-only attribution plan; native Node test source.

## Why this sprint matters beyond another generic conversion page

The *choice-blindness* primary experiment is a new, distinct Mind & Perception search/TikTok destination. The research itself is strictly noncommercial. Its theme provides an editorial reason to explain how readers can evaluate commercial claims without being rushed into a purchase. The buyer guide is a **separate** independently written product page, not a commercial conclusion added to the investigation. It asks what the visitor needs, gives a genuinely useful free twelve-minute preference exercise, compares the precise seller packages, then presents both reasons to consider and reasons to skip.

**Original episode title:** *The Choice You Didn't Make*  
**Meta description draft (not in CMS):** "Researchers switched the choices people made. Many didn't notice—and explained the outcome anyway. Explore choice blindness, its limits, and the original studies."  
**Proposed slug:** `/mind/choice-blindness/` — unpublished; do not create a broken menu link.  
**Topic family:** perceptual decision-making, introspection, expectations, experimental deception; historical analogy to Puységur without mechanism equivalence.

## TikTok / organic bridge (editorial only)

**Short concept 1 (20–25 s):** "They picked one photograph. The researcher gave them the other. Then asked why they chose it. Some people explained a choice they hadn't made. That's the 2005 'choice blindness' experiment. But it doesn't mean every decision is fake: read the method before you borrow the conclusion." CTA to published investigation **only after actual publication**.

**Short concept 2 (20 s):** "A supermarket taste test. Someone chose their favorite jam. The sample was swapped. Many didn't catch it. Researchers tested preferences, not mind control. The difference matters." Cite Hall et al 2010 onscreen, no manufactured footage or invented participants.

**Short concept 3 (30 s):** "Twelve minutes is how long a recording lasts. It isn't proof of an hour's meditation. Here's a free three-occasion listening-preference test and the study that explains what remains unknown." Link to independent Zen12 guide **only after publication approval**. If short includes a later commission link, require clear audible/onscreen affiliate disclosure and authorized channel.

## Working navigation (all proposed; NO CMS write)

- `/mind/` → Perception & Attention → **new choice-blindness investigation** (unpublished). Existing published related page: https://finalvestige.com/2026/11/02/change-blindness/
- `/mind/` → History of Suggestion → published https://finalvestige.com/2026/11/02/mesmerism/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- `/mind/` → Practice & Reflection → established https://finalvestige.com/focus/ (single existing Jetpack Focus funnel, no new form, subscription requirement, or email sequence).
- `/mind/` → Tools Under Review → Zen12 source guide; future Total Focus source guide (both currently draft, never describe as published).
- Preserve existing six historical categories; no mechanical seventh tile, no replacing homepage PR #49. **Canonical Mind hub is PR #172; review alternative markup but do not supersede it.**

## Site and merchant verification snapshot (3 Nov 2026)

- Issue #171 initial inventory was 61 posts. Authenticated WordPress read-only posts list shows **66 published posts** as of 3 November, including Change Blindness and Mesmerism. Puységur is published page ID 1377; Focus Fieldbook is published page ID 1579.
- Original published Puységur page includes a historical source-trail and explicit evidence limits. Existing Focus page uses original Jetpack/Focus conversion flow; preserve.
- Inspire3 official catalog: https://inspire3.com/
- Exact seller offer: https://zen12.com/hnp ; 12-minute MP3 sessions, four styles, beginner/advanced six levels and premium/full twelve levels (48 MP3). Merchandise details are seller assertions.
- Exact full-course checkout: https://zen12.com/getstarted ; shows 12-level / 48-file offer, mobile phone form, promotional timer and an order summary. **Do not copy price, countdown urgency or testimonial outcomes.**
- Seller privacy: https://inspire3.com/privacy/ ; potential marketer calls/SMS and buyer identity data shared with referring affiliates. **Do not import any buyer identity reports.**
- Seller Terms: https://inspire3.com/terms/ ; prior Issue #171 direct verification covers advertised one-year refund and later manual card-refund procedure, but direct fetch was unavailable in this particular run. **Reverify before launch.**
- Inspire3 affiliate portal: https://affiliates.inspire3.com/ is generic public program material, **not proof of Final Vestige acceptance, exact-offer earning URL, or approval for TikTok/website/email**. Approved Zen12 creatives or swipes not accessible without partner credentials. We use only original art and words.
- FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; health claims: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
- Independent entrainment review: https://doi.org/10.1371/journal.pone.0286023 — mixed EEG evidence, not Zen12 product efficacy.

## A/B experiment: clarity, not promised conversion

**Version A:** complete self-sufficient text guide, source context, free exercise, privacy/refund review, prospective disclosure beside a hard-disabled action.

**Version B:** **the exact same substantive guide text**, with one *original* inline SVG poster, an expanded optional 40-second six-scene storyboard/transcript and a WebVTT file for a **future** first-party film. No pretend playback element. Both are standalone Custom HTML drafts with scoped CSS, 48px CTA, visible focus, mobile stack, prefers-reduced-motion and usable no-JS content.

**What is tested now:** static source parity, fail-closed commercial buttons, original visual-only difference, link restrictions, readable transcript, source references, zero scripts/forms, synthetic event validation. **What is not tested now:** actual 40-second playback, captions synchronized to media, mobile Chromium layout, live WCAG 2.2 AA, Core Web Vitals, recorded traffic or purchase outcomes. A/B performance cannot be inferred.

**Before any genuine A/B test:** founder and QA sign off on publication and a privacy/security design. If actual instrumentation is allowed, measure only explicitly permitted categorical *outbound intent*, never identifiable users, referrers with query strings, IP, exact timestamps, session IDs, email, order IDs or buyer names. Do not request sales attribution if merchant cannot guarantee aggregate-only information. Real experiment requires clearly defined visitors/exposure and a legitimate denominator; synthetic rows and clicks do not equal sales.

## Reproducible developer QA

After checking out this exact branch on a machine with Node >=20:

```sh
node --test mind/review-r104-choice-blindness-zen12/pilot.test.mjs
```

The committed test suite defines **12 Node test bodies**. Independently, the source at the final committed GitHub file blobs was checked using a JavaScript V8 adapter: **52/52 assertions passed** (content identity, source IDs, disclosure-adjacent control, merchant links absent, no executable/tracking elements, SVG/transcript, six sequential VTT cues 0–40 s, 16 source records, 40 claim decisions and 32 closed release gates, rejection of identifying fields, synthetic cells <20 suppressed, live recording hard-blocked). This is **not** a claim that native Node, CI, real-browser a11y or Lighthouse passed. Test bodies are committed for CI.

## Claim review and operations

- `evidence-gates.json` has **16 source references, 40 claim/permission decisions and 32 CLOSED release gates**. Product-specific results, guaranteed efficacy and artificial scarcity omitted.
- `attribution.mjs` does **not** run in a website and has no side effects. It enforces four fixed categorical fields and minimum cell count twenty for a synthetic-only demonstration; `recordLiveEvent()` always throws. There is no JS in either landing design.
- No customer capture, popup, new newsletter, affiliate link, pixels, duplicate Focus flow, third-party video embed, trial download, or branded merchant creative.
- Any actual product affiliate CTA remains **blocked** until written partner approval and exact offer URL, channel permission, buyer PII exclusion, FTC and privacy signoff, real QA, and founder publication/release approval.

## Handoffs

**Homepage art lead / Issue #150:** New Mind portal concept remains editorial-only. Do not alter or merge into flagship PR #49. If visual integration is desired, decide separately after QA.

**Site QA / Issue #126:** Independently examine source-to-claim mapping, native Node suite, real 360/390/768/1440/1920 browser sizes, WCAG keyboard/readability/no-JS, and any later first-party video synchronization. Treat direct seller references as *seller assertions*.

**Dispatch / Issue #174:** This lane owns presell landing pages only. Issue 03 Zen12 and Issue 05 Total Focus must retain HOLD_MERCHANT; these drafts are **not** published destinations and no mail may be sent based on them. Existing Jetpack welcome must be untouched. No newsletter issue changes made.

**Founder:** Review editorial quality and A/B UX, not estimated conversion rates. All publication and merchant activation gates remain closed.
