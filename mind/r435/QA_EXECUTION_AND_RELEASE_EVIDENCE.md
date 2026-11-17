# Mind R435 — Exact GitHub source read / QA receipt

**16 November 2026 (PT) · UNPUBLISHED · COMMERCIAL HARD HOLD**

## Scope and proof

- Exact isolated branch: `mind-r435-puysegur-hypnosis-evidence-commerce-20261116`.
- Initial source commit `d32029b614c837749b47a73684079e0b1f25cffd`.
- Verifier correction commit `6dff2de78bc39e118656f4c1b5b4ba037dffc46f`.
- Source contents were **reread from the actual GitHub branch** with `fetch_file` after the correction. The isolated V8 inspection then passed **63 / 63 static assertions**. These are source-level tests, not a native Node or website integration run.
- Source/article research covers live FV Puységur archives, existing Focus, official Inspire3/Zen12/Hypnosis Live/Brainwave Shots exact product pages, peer-reviewed research and FTC guidance (links below). No unapproved merchant links or product efficacy claims activated.
- Claim table: **34 entries, 16 cited evidence URLs**; commercial checklist: **28/28 HOLD**.
- Buyer A/B copy: identical substantive buyer sections in both drafts by construction; B adds an *optional, non-playable* poster/storyboard/transcript/VTT concept, not a real video or completed A/B test. Six WebVTT cues end at **00:00:42.000**.
- The hub is HTML source only, not a saved WordPress CMS draft or a published `/mind/` route.
- GitHub static tests checked HTML5, lang, mobile viewport, noindex, CSS keyboard focus and reduced-motion hooks, absence of active scripts/iframes/forms/video, absent earning link AND absent even ordinary clickable merchant links, inactive purchase control, prospective FTC disclosure and copy-limit structure.
- An earlier source inspection failed four overly broad checks that treated the noncommercial navigation text “Buyer questions” as an active purchase anchor and demanded numeric `12 levels` despite accurate “twelve levels.” Those verifier checks were narrowed in the new commit; **63/63 subsequently passed**. Do not report the earlier failing run as a success.

## Exact source blob ledger from passing read

| Path under mind/r435/ | GitHub blob SHA |
|---|---|
| THE_SLEEPING_WITNESS.md | `debeb16fbab39f40dcf0ca56499e9c540a58e0c0` |
| ZEN12_A_TEXT.html | `3296e0f41ac8adddb8337a69ee871905080b9133` |
| ZEN12_B_FILM_CONCEPT.html | `773dd573b1dc4a02376ac8fffd3d6175d851d5c9` |
| MIND_HUB_WORDPRESS_SOURCE_ONLY.html | `618da3ae6798f4a49d7c2a3601d1222cf1dad325` |
| film.vtt | `fab613d958d4d2e57cfb29e23e9d309d69b25f4f` |
| CLAIM_SOURCE_PERMISSION_MATRIX.json | `ae2084a0bd50b36f8565da54f9d0adf433fecb5e` |
| CONVERSION_ACCEPTANCE.md | `e03515df778ebecd421a0f2293dc793f5984cc85` |
| verify.mjs | `d132c7f572514328e354816be8ce6d978fc44c84` |

## Commercial-link hardening after initial review

Two initial buyer-guide versions cited public Zen12 seller pages as clickable links. This was not an affiliate referral, but it conflicted with the founder's stricter mandate to withhold commercial product links entirely. Both A/B drafts were updated to cite the precise seller URL as plain text rather than clickable merchant href. The verifier now rejects all active Inspire3, Zen12, Hypnosis Live and Brainwave Shots hrefs, even non-earning links. **Final read-only exact-GitHub-source execution: 63/63 static assertions pass**, 28/28 release gates HOLD. Earlier 60/60 check was superseded by this stronger test.

## Explicitly NOT TESTED / release blockers

1. **Commercial:** No verified Final Vestige-named Inspire3 acceptance, approved channels/SKU, issued earning link, exact referred price/refund, merchant sale or settled commission. Read-only Gmail checks surfaced irrelevant consumer mail and no matching named approval. Existing 52-page Focus Fieldbook is FREE, not a verified sellable owned SKU.
2. **Native execution:** `node mind/r435/verify.mjs` has not run in a native checkout; source assertions executed in isolated V8 against fetched blobs. Hosted CI/status, native Git tree byte-for-byte package run and production build not tested.
3. **Real UX:** Browser viewport 360/390/768/1440/1920, accessibility/WCAG 2.2 AA, color contrast, VoiceOver/NVDA, Lighthouse/CWV, WordPress sanitizer, actual local film encoding/playback, content images/credits and third-party product checkout not tested.
4. **Attribution:** No approved instrumentation or actual qualified-human traffic data; `affiliate_outbound` is not a paid order; verified net revenue per 1,000 qualified humans remains NOT COMPUTABLE.
5. **Creator:** The three Mind creator topics are research-only candidates. No existing real published media IDs or mobile links authenticated. Do not seize Grok's work.
6. **Production:** No CMS/navigation/homepage #49 or #150, Mind #172, Jetpack/Dispatch, social post, paid SaaS, merchant link, merge, release or spending authorized.

## Actual source URLs

- https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- https://finalvestige.com/focus/
- https://inspire3.com/
- https://zen12.com/about
- https://zen12.com/secret/
- https://hypnosislive.com/
- https://brainwaveshots.com/focus-shot
- https://doi.org/10.1002/jhbs.21974
- https://doi.org/10.1002/acp.3730
- https://pubmed.ncbi.nlm.nih.gov/39032268/
- https://pubmed.ncbi.nlm.nih.gov/38268815/
- https://pubmed.ncbi.nlm.nih.gov/38569321/
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance

**Release required:** founder approval plus independent source/commerce/QA acceptance. Exact final branch commit is supplied in the PR and subsequent Issue #171 handoff after this receipt commit.
