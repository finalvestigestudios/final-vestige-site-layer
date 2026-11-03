# R89 — The Sound You Saw / Zen12 evidence pilot (UNPUBLISHED)
**2026-11-03; isolate all files under this directory; no CMS write, release, merge or affiliate activation.**

## Design intention
An original source-grounded McGurk investigation that exposes the limits of sensory inference, plus a separate Zen12 offer guide matching the actual seller's page rather than generic self-help copy. A/B: identical article guide core; B alone adds an original optional 40s educational video **storyboard, poster and visible transcript**. B is not a playable film and must not be represented as one. There is no test outcome and no performance claim.

## Source-of-truth
Official brand https://inspire3.com/ ; exact offer https://zen12.com/hnp ; About https://zen12.com/about ; seller research https://zen12.com/research ; public checkout https://zen12.com/getstarted ; privacy https://inspire3.com/privacy/ . All inspected November 3, 2026. Public https://affiliates.inspire3.com/ is recruitment only; **no FV-specific acceptance or creative rights confirmed**. Exact full refund/terms unavailable. Buyer identity-sharing possibility requires opt-out agreement before approval. Never publish checkout prices or unverified payout links.

Independent: McGurk and MacDonald 1976 https://doi.org/10.1038/264746a0; Brown et al. 2018 https://doi.org/10.1371/journal.pone.0207160; Teramoto and Ernst 2023 https://doi.org/10.1038/s41598-023-33791-y ; Ingendoh et al 2023 https://doi.org/10.1371/journal.pone.0286023. FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Contents
- investigation.md: original independent editorial research, no commerce.
- zen12-guide-core.html: exact same guide embedded **without modification** in A and B.
- zen12-a.blocks.html: proposed Gutenberg Custom HTML text-only.
- zen12-b.blocks.html: same text + optional original 40s storyboard and no-JS transcript.
- mind-hub-noncanonical.blocks.html: four-stream reviewer prototype, never supersedes PR #172.
- 40-second-film-captions.vtt: contiguous 0–40s captions, not proof of a rendered film.
- claim-source-permissions.json: line-by-line source and gate matrix.
- attribution.mjs: synthetic-only disabled aggregation, no network or PII.
- tests.mjs: source-controlled Node test suite.
- REVIEW-QA.md: deployment and manual QA checklist.

## Reproduction / QA
From repository root: `node --test mind/the-sound-you-saw-mcgurk-r89/tests.mjs`.
Before any publication: actual native Node tests, hosted CI, WordPress Gutenberg staging, browser keyboard/touch/screen-reader axe/WCAG 2.2 AA, real 360/390/768/1440/1920 renders, Lighthouse, caption sync to first-party-hosted original final MP4, reduced motion, media performance budget. Do not assert these checks passed unless run. For a future A/B use server-issued non-identifying randomized variants and minimal categorical aggregate analytics only AFTER privacy terms, QA, consent/rules and founder activation; never place buyer PII in analytics or merchant parameters. Do not use an active A/B framework now.

## Coordination
Site QA #126 reviews disclosures, exact offer, disabled link and readable no-JS transcript. Homepage Art #150 reviews visual language only; homepage PR #49 untouched. Dispatch #174 receives buyer-guide status ONLY; its campaign/newsletter drafts and Jetpack's existing welcome message must not be changed here. The canonical /mind/ PR #172 remains untouched. **All gates closed** until written founder authorizations and per-product partner terms exist.
