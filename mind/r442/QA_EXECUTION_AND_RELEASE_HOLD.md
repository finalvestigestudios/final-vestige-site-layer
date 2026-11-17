# Mind R442 — QA, source chain, limitations, release hold
**Date:** 2026-11-17 PT
**Branch:** `mind-r442-binaural-beats-sales-proof-20261117`
**Source tree tested before this receipt:** `ed8bc33faeff4e84e6e944167b484d2a9e057325`
**Merge/release:** HARD HOLD. This receipt does not approve or deploy anything.

## Exact read-only source execution

Fetched all eight committed source files back from GitHub on the new isolated branch. Applied **118/118 passing** independent V8 assertions, including 10/10 adverse synthetic mutations. Mutations were performed only in memory; no test files, business settings or live records were changed.

**Test coverage:** byte-for-byte identical base buyer text after stripping B-only optional film section and variant title; three proper standalone HTML documents; lang, viewport, offline noindex, no scripts/iframes/video/form/autoplay, no active merchant links, first-party links, no deployed tracking implementation; keyboard focus and responsive styling; genuine native disabled commercial buttons, same-unit prospective FTC disclosure before CTA, qualified seller efficacy claims, no invented endorsement/price; B original SVG/poster, complete transcript, six-cue captions 00:00–00:42; 34 claims / 13 source URLs / 28 HOLD gates; disabled affiliate and null paid metrics; four hub streams, preserved canonical routes; positive, negative and limited research findings, Puységur connection, net-revenue KPI and hard hold.

**Adverse source changes detected (10/10):** commercial button enabled; seller href inserted; earning disclosure removed; script inserted; extra signup form inserted; poster caption removed; invented price inserted; affiliate eligibility switched on; paid sale fabricated; final VTT cue deleted.

**Iteration:** Initial read-only source audit yielded 104 passing / 3 failing due solely to a careless detection rule treating the English text *tracking pixel* as evidence of a deployed pixel. That rule was corrected to look for actual 1px image tags, script APIs or known analytics tags. Subsequent full source audit passed **118/118** including mutation traps. The committed Node verifier was also repaired to use correctly escaped regex literals. This is test logic correction, not a finding that live tracking exists.

**Scope boundaries:** The on-branch `verify_r442.cjs` is a reproducible **native Node test script**, but **native execution on a checkout has NOT been performed** in this run. The isolated V8 assertions above were executed against GitHub-fetched blobs and are not proof of actual browser rendering. A container network attempt to reach GitHub failed DNS resolution; hosted GitHub CI, independent production WP sanitization, 360/390/768/1440/1920 browser capture, WCAG 2.2 AA, Lighthouse/CWV, encoded film/caption playback, actual Jetpack signup, actual checkout and paid settlement are **NOT TESTED**.

## SHA-verified source manifest at tested source state

| File | GitHub blob SHA |
|---|---|
| THE_FREQUENCY_THAT_PROMISED_FOCUS.md | `c0d70944fd724999d9895ace1786742d45c417ca` |
| ZEN12_A_TEXT_ONLY.html | `a2c7c5429e9f27466157879cbd96a66e3861087b` |
| ZEN12_B_OPTIONAL_FILM_CONCEPT.html | `3b56bf2325b4086effea379f5c465a29753d48cf` |
| R442_CAPTIONS.vtt | `c772c07ec91ef111cbef2427ef5ee662f9534b18` |
| MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html | `3ae862f0eb70e66f9518bd3491da2ee63e875732` |
| CLAIM_SOURCE_PERMISSION_MATRIX.json | `825ac7fa63a197bc19bafd0dd4eb4b84676d66f0` |
| OFFER_FUNNEL_CREATOR_REVENUE_ACCEPTANCE.md | `6b21504e285486f7d742f59959aba6458a8f1608` |
| verify_r442.cjs (post-correction) | `7c307245cdb6fc3bc18d75cf961f7c7cce5ff606` |

## Research provenance rechecked before authoring

- Ingendoh, Posny and Heine (2023), systematic review 14 studies: https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/
- Scientific Reports 2025 80-person parametric study: https://doi.org/10.1038/s41598-025-88517-z (search/indexed text accessed; direct journal HTML fetch redirected to inaccessible identity provider, recorded limitation)
- 2020 binaural vs monaural auditory research: https://pmc.ncbi.nlm.nih.gov/articles/PMC7082494/ (search/indexed abstract accessed; subsequent full-page fetch prompted CAPTCHA, recorded limitation)
- Official seller landing: https://inspire3.com/ , https://zen12.com/about , https://zen12.com/secret/ , https://brainwaveshots.com/focus-shot , https://hypnosislive.com/mental-skills/total-focus
- Public live FV: https://finalvestige.com/focus/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; published change blindness https://finalvestige.com/2026/11/02/change-blindness/
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- GitHub authoritative issue #171 and #820 read; Dispatch #174 latest commercial HOLD handoff reviewed. Existing Grok TASK-008 and dated handoff Docs read via connected Drive, not web search.

## Commercial acceptance

**28/28 release gates HOLD** pending exact named Final Vestige Inspire3 account approval, SKU permissions per site/social/email, permitted creative, issued earning URL, referred checkout, verified current price/returns and actual payout/settlement reporting. No rights-cleared paid FV Mind SKU was authenticated; existing /focus/ is FREE. Candidate social videos are NOT matched to published asset IDs. No verified paid sale or qualified-human denominator: **net revenue per 1,000 is NOT COMPUTABLE**. `affiliate_click` is not `merchant_confirmed_order`.

## No-change custody

No homepage PR #49, Issue #150, Mind PR #172, Dispatch #174, live WP CMS/navigation/settings, Jetpack welcome, email send, Grok posts/queue, affiliate link, analytics tag, merge, deployment or spending was touched. Art and Site QA own their separate review, and the founder retains production/commercial release authority.
