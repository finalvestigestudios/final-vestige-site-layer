# FV Media — 15-original DPR/960px staging matrix (2026-11-12)

**Scope:** Historical 61-post/355-inline/288-offsite inventory remains separate from 66-post expanded census. Worklist is on draft #183 (not main), Site QA owns #154; this audit is an independent, source-only P1 plan on draft #1703. Frozen P1 input Git blob `925fadb52b873af7e30f48f586f8e743c0a4c10c`.

## Concrete result
- **15** WordPress image originals exceed 1.5 **decimal** MB; total **47,096,779 stored bytes**, NOT browser transfer. Eleven appear inline in eight posts; other four are not proven unused, do not delete.
- **Five** inline 1672×941 PNGs (media 39–43; posts 34–38) have **zero registered WordPress subsizes**, use **13,267,538 stored original bytes**, and have HTML 1024px width hints. Hints do not prove CSS painted width.
- New **270-case** matrix tests each original conditionally at 320/390/480/640/768/960 CSS px and DPR 1×/2×/3×, computes physical required widths, and proposes *nonexistent* source-bounded candidate variant dimensions.
- A blanket **960 physical px** derivative geometrically covers 390 CSS px at 2× (780 pixels needed), but **not** 390 CSS px at 3× (1170), or 640 CSS px at 2× (1280). Crucially, the five 1672-wide PNG originals **cannot even meet 960 CSS px at 2×** (1920 needed) without upscaling. This is conditional, not a claim of observed blur.
- Variant widths are capped at 1920; when even native pixels or the proposed widths do not meet a scenario the record explicitly says so. Reuse rights, scene fidelity, image credit, cropping, intrinsic pixels, map label legibility and actual `currentSrc` still need independent review.

## Safe implementation sequence
First resolve six P0 suspected missing images with Site QA's existing logged-out Chrome collector and real URL/HTTP/decode evidence. Only after that record P1 actual painted CSS widths, device DPR, `currentSrc`, full-scroll lazy-loaded image responses and uncached `Network.loadingFinished.encodedDataLength`. Check existing WordPress-generated subsizes/Jetpack transformations first, instead of blindly recompressing full originals. For authorized images only, prepare *staging-only* responsive source candidates preserving original scene and attribution, then inspect mobile/high-DPR crops, CLS, and text/map legibility; preserve original media and a reversible mapping. No automatic bulk Gutenberg block rewrites.

The advertised **76% savings remains an unmeasured hypothesis**, requiring strictly paired cold browser requests, de-duplicated transfer bytes, full page image coverage and identical visual framing/content. Website storage-byte totals cannot validate a network-byte result.

## Boundaries
No external-source binaries were downloaded or cached; no variants, `srcset`, WordPress changes, homepage design, deployment, merging, or paid service calls. All source URLs, rights holds and unknown guest HTTP statuses preserved. This plan deliberately does not overlap Site QA's browser collector.
