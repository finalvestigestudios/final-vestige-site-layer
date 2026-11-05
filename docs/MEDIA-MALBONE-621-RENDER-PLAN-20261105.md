# Malbone #621 — WordPress virtual rendition and visual safety gate (November 5, 2026)

**Independent Media Recovery only; no homepage changes or Site QA PR #154 modifications. Read-only inspection; production writes prohibited.**

## Newly verified live facts

WordPress post [Six Miles an Hour](https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/) (ID 621, status published, modified 2026-09-09T12:03:35) has six inline images in its stored HTML; **all six lack explicit width/height and stored srcset**. These are potential layout/selection problems, **not measured browser CLS**. Two `sizeSlug:large` blocks have stored `src` pointing to full JPEG originals rather than the registered large rendition. A theme/Jetpack runtime rewrite might still occur.

| Image | WordPress original source | Dimensions | **stored original** | Existing virtual 768px candidate | Conditional width≤960 derivative |
| --- | --- | --- | ---: | --- | --- |
| 621:0 / #1257 | https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg | 4000×3000 | 4,798,395 bytes | https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original-768x576.jpg (768×576) | 960×720 |
| 621:1 / #1258 | https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg | 5667×3831 | 5,553,669 bytes | https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original-768x519.jpg (768×519) | 960×649 |

Combined: **10,352,064 bytes (9.87 MiB) stored, NOT observed visitor wire bytes** (~23.8% of the earlier 43,522,829 bytes stored in 13 WordPress media originals >1.5 MiB). WordPress also lists 1024-wide `large` variants (1024×768 / 1024×692), but they exceed the 960px maximum. **All listed intermediate sizes are marked `virtual:true`** in WordPress's own response: existence, successful HTTP delivery, image decoding and file size are all unknown. Never treat a WordPress metadata entry as proof the derivative was generated or delivered. Do not delete originals or rewrite post blocks.

## Historical provenance and rights

**1257:** Published caption identifies a 2021 Prospect Park tunnel view credited GeneralPunger, Wikimedia Commons, CC BY-SA 4.0. The exact Commons file revision, edit lineage and license for the uploaded `edit-017` derivative were **not independently verified**. Preserve creator credit, CC BY-SA link, edit disclosure; assess share-alike for adapted assets. **Item-specific rights HOLD.**

**1258:** Caption identifies NYPL 1903 Brooklyn transit map and claims US public domain. NYPL's [rail-transit research guide](https://libguides.nypl.org/nyc-rail-transit/companies) references **image ID 5003296**, and the [NYPL rights policy](https://qa-digitalcollections.nypl.org/about) explicitly distinguishes public-domain, rights-managed and undefined item captures. Exact item's rights and altered binary identity have **not been checked**. A smaller map may become unreadable; preservation of place names and ability to view a high-resolution detail are visual-release requirements. **Item-specific rights HOLD.**

## Safe route to actual performance improvement

1. Existing Site QA #154 retains its six P0 logged-out source-failure targets **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. This Malbone work is secondary: do not duplicate the Chrome CDP collector.
2. Later measure this exact published post at **360px mobile and 1280px desktop** in a cold logged-out browser: recorded `currentSrc`, real Image request+response IDs and status, decoded natural dimensions, cache booleans, encoded transferred bytes, and before/after screenshots. Distinguish editor raw `src` from runtime `currentSrc`.
3. Independently verify virtual **768px** candidate URL response and decode; compare visibility/legibility with source. Do not assume 1024px counts as ≤960. If 768px is too small, after item-specific rights and binary SHA-256 validation, stage **960×720 / 960×649** from a lawfully obtained original in the existing no-overwrite offline stager (PR #1145), ensuring no crop drift and preserving attribution. The map may warrant a separately approved high-resolution zoom/link for reading labels.
4. Compare genuinely cold CDP encoded image transfer for identical post, viewport and cache controls, plus layout/visual parity; report **pair-level wire delta only**. Do not claim sitewide **76%** improvement from metadata or compressed-file size.
5. Any future WordPress upload, caption, Gutenberg block update or release requires separate rights, staging screenshot, rollback and publication approval. This PR makes no changes to production or media binaries.

**Unverified:** the reported 42 broken external images, the 76% transferred-image reduction, any browser loading failure in post 621, and any production repair. Machine audit + validator + mutation tests are under [qa/media-recovery](../qa/media-recovery/). V8 exact-source assertions run; native Node CI and guest browser still required.
