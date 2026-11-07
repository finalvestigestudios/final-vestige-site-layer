# EX2 archival image origin-selection experiment — 2026-11-07 UTC

**Review-only; RELEASE HOLD.** Stacked on draft PR #1358 exact parent `4272cc5860ce6f56a9460c50891001a4372b0d89`. Frozen PR #49 unchanged. Canonical seven-chapter Blueprint is **not modified**. This adds an optional reproducible **derived WordPress Playground variant**, not a new chapter or production release.

## Material, source-grounded discovery
At all tested sizes, both archival `img` elements have first-party `src=https://finalvestige.com/wp-content/uploads/...`, but their browser-selected `currentSrc` comes from **`https://i0.wp.com`** because their `srcset` alternatives point to WordPress's image CDN. Prior claims that the configured `src` alone proves the browser received first-party bytes are invalid.

WordPress media #473 (NASA Apollo 1 image S67-19766) is a 1041×810 WebP, media-record original size **78,346 bytes**. Media #474 (Franklin Victory Point note, Wikimedia public-domain scan of an 1869 printed reproduction; museum object Royal Museums Greenwich HSR/C/9/1) is a 960×1526 JPEG, media-record original size **466,043 bytes**. All responsive sizes returned by WordPress for these two media items have **`virtual: true`** and `source_url` at `i0.wp.com`; guessing on-origin files such as `-300x233.webp` would invent assets. NYPL media #1258 remains excluded from the canonical candidate; its appearance in published Page 6 is a separate rights review.

## Isolated experimental change
`make_first_party_media_variant.py` refuses all source blobs except `137c74a476005684a28f5ff9a36e75c6b03268f7`, removes exactly the two `srcset`/`sizes` pairs from the two archival `img` elements, and asserts derived Git blob `f7091ba1383a5c9438ef893d62bf35d18a6e2462`. It generates a private browser-launchable Playground bundle. All seven chapters, 72 Margins records, five /focus/ destinations, CSS, JS, images, alt descriptions and source citations remain unchanged. Only selected network request destinations change.

**Why this is NOT an automatic release win:** Responsive CDN image candidates can save substantial transfer bytes on mobile. Forcing original files may increase mobile consumption and worsen LCP/engagement. The sizes above are WordPress *metadata*, not measured mobile transfer sizes; the originals total 544,389 metadata bytes, but are lazy-loaded and need not transfer before interaction. Do not claim an improvement in load speed or conversions.

## Reproducible browser experiment
```bash
python experience2/home-flagship/playground/make_first_party_media_variant.py \
  experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json /tmp/fv-ex2-review
python experience2/home-flagship/playground/verify_first_party_media_variant_browser.py \
  experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json --output /tmp/fv-origin-select.json
```
Requires Python Playwright and Chromium for the second command; no WordPress production access or external request is required. The verifier **aborts all image requests deliberately**; it tests browser URL selection, *not successful delivery*. The local equivalent source experiment observed **24/24 viewport × DPR × JS configurations**, **48/48 first-party `currentSrc` selections** for the derived variant, and a negative control in which the unchanged canonical source correctly selected `i0.wp.com`. Six widths: 320, 360, 390, 768, 1440, 1920; device scale factors 1 and 2; JS enabled and disabled. Source mutation was rejected. Independently captured 390×667 and 1440×900 **offline first screens were pixel-identical** before/after this media-only variant (external requests blocked in both).

These are locally executed *equivalent* checks; **GitHub-hosted exact-commit CI, real isolated WordPress/Assembler, real network response bytes, axe/WCAG, Safari, CWV/Lighthouse and Jetpack signup are NOT established**. GitHub CI and QD are not declared PASS.

## Release/commercial decision
**HOLD / experiment only.** Keep CDN-responsive canonical variant in place until private WordPress/Assembler can compare actual `currentSrc`, transferred bytes, decoded dimensions, response hashes, visual quality, mobile LCP and evidence engagement across both options. Preference is the route that maintains visitor performance and authentic provenance, not the one with prettier origin metadata. No revenue or confirmed subscriber gain is claimed.

**OFFER → FUNNEL → BLOCKER → CHANGE → PASS/FAIL → OWNER:** Existing 52-page Focus Fieldbook → evidence trust / source display before CTA → CDN-vs-origin claim ambiguity and unknown mobile transfer costs → source-pinned origin-only comparison variant, no production change → 24 browser route-selection passes and one negative control; actual transfer/performance **BLOCKED** → interim homepage engineering + Site QA for acceptance; Claude for real attribution and signup/checkout; Grok/Praxxis for acquisition. Maintain contextual disclosures for any independently verified affiliate offer; no new product claims or links.

**No live CMS writes, merge, deploy, publishing, site setting, subscriber data, analytics, affiliate activation, expense or frozen PR #49 changes.**
