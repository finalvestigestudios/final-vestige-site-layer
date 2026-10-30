# Zen12 independent product guide — FIRST CONVERSION PILOT

**October 30, 2026 | Unpublished, source-controlled prototype | Owner: Mind & Affiliate Studio | Issue #171**

This is a **new isolated branch** from `main`, separate from existing Mind hub PR #172, homepage flagship PR #49 / Issue #150 and newsletter PR #175 / Issue #174. NO WordPress changes, navigation edits, outbound affiliate activation, media uploads or mailing-list changes.

## What was researched (actual seller pages, not only catalog)
1. `https://inspire3.com/` — identifies Zen12 as brand under Inspire3.
2. `https://zen12.com/` — current full long-form vendor sales page with pain-point messaging (lack of time, restlessness, chatter, no quick results), tiers and four styles.
3. `https://zen12.com/about` — claimed 12 levels/4 audio styles, 12-minute format, brainwave assertions and safety advice.
4. `https://zen12.com/research` — seller's claimed scientific basis; **not** independent product-specific validation.
5. `https://zen12.com/getstarted` — live checkout excerpt showed a full-course bundle and discount price on 2026-10-30, but cannot establish the future affiliate destination's price or whether the offer is available to user. Checkout also displays phone fields, terms and seller return guarantee. Prices are intentionally absent from published copy.
6. `https://zen12.com/welcome` — free audio signup explicitly says it also subscribes visitors to **the merchant's own** newsletter. Do not confuse with FV Jetpack/Fieldbook.
7. `https://affiliates.inspire3.com/` — public partner recruiting, **not** evidence Final Vestige is approved or has valid tracking links. Member-only creative library and allowed email promotion still need authenticated verification.

## Empirical sources and limits
- Original attentional blink: https://pubmed.ncbi.nlm.nih.gov/1500880/ (Raymond et al 1992) and https://pubmed.ncbi.nlm.nih.gov/8189198/ (Shapiro et al 1994); this concerns RSVP task interference, NOT meditation or proof of Zen12 effects.
- General meditation review: https://pubmed.ncbi.nlm.nih.gov/24395196/ (Goyal et al, JAMA Internal Medicine 2014); some modest benefits across studied programs, **not a trial of Zen12**.
- Binaural beats review: https://pubmed.ncbi.nlm.nih.gov/37205669/ (Ingendoh et al, PLOS ONE 2023), 14 EEG studies, **5 supportive, 8 contradictory, 1 mixed**; high heterogeneity, no specific support for the seller's twelve-minute equivalence assertion.
- NIH NCCIH: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Files / intended IA
- `page-zen12-guide.blocks.html`: fully styled, responsive WordPress Custom HTML draft at **proposed** `/mind/zen12-guide/`; no active affiliate checkout link. True external source links only.
- `article-attentional-blink.md`: standalone, researched non-commercial entry-point article with primary sources, no fabricated "web experiment" result, proposed `/mind/attentional-blink-second-target/`.
- `claim-matrix.json`: 15 claims, seller-vs-independent claims, risk flags, no affiliate URLs.
- `video/40-second-film.md`, `video-module.release-gated.html`, `captions.vtt`: complete optional video concept, script and release-gated player/CC. **A film is not yet produced or hosted.** Landing page uses useful accessible transcript rather than a broken fake video player.
- `measurement.md`: privacy-safe, consent-reviewed **proposal** for A/B, funnel events, suppression of PII.
- `tests/test_gate.py`: reproducible static content/release gate tests.

## Copy architecture and why it matches the merchant
The seller's actual page foregrounds lack of time, mental chatter, restlessness, promises "meditates for you" and one-hour equivalence. Our original copy keeps the true **customer objection and format fit** (short sessions and multiple styles) while sharply separating unverified efficacy. Progression: relatable moment -> honest reframing -> free observation exercise -> factual product features -> limits and third-party science -> who it may fit -> optional eligible CTA. Avoid stealing seller headline, testimonials, carousel, countdown or aspirational guarantees. Source links and free /focus/ offer mean the guide has value **even if no affiliate link ever goes live**.

## Release blockers (hard stops)
- Authenticated FV partner status, exact deep link, promotional rights and newsletter/email permission **unverified**. No actual affiliate CTA.
- Product-specific clinical/EEG claims **unsubstantiated**; therefore excluded. No "1 hour in 12 minutes" FV claim.
- Pricing and seller policy may change; no price advertised until verified just before release, from actual affiliate destination.
- Media script/VTT exist; final original MP4/poster, independent audiovisual disclosure check and bandwidth/browser metrics pending.
- Proposed `/mind/` hub and guide URL aren't live; main published source paths are /focus/, /editorial-standards/, /affiliate-disclosure/, /free-resources/puysegurs-animal-magnetism-files/.
- Actual WordPress rendering, accessibility manual check, full Lighthouse metrics, CWV and independent QD not complete.
- Newsletter campaign is separately owned; no WordPress email changes, sends or Jetpack subscription duplication.

## Source-control release sequence
Independent review -> actual media creation + QA -> optional variant validated -> partner authorization + official tracking verification -> editorial/FTC QA -> founder publish approval -> approved CMS changes separately. Current code is intentionally draft.

**Repro test:** `python -I -m unittest discover -s mind/zen12/tests -v`. Do not report tests executed unless actually run against exact PR commit. Branch-head source structure validations are not a substitute for rendered browser QA.
