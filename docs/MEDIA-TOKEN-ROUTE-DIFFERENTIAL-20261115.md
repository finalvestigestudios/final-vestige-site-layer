# Media recovery: two upstream \`itok\` routes — differential evidence (15 November 2026)

**Status: HOLD; independent read-only QA.** Scope is post image keys **288:5** (Honda Point) and **418:5** (Hilo 1946). This extends the existing [68-slot token-fidelity ledger](../qa/media-recovery/query_token_fidelity_68_20261115.json) and does not change Site QA #154's collector, WordPress, or homepage design.

## New three-route observations for each image

The external web retrieval interface **rendered both token-bearing original-source JPEGs**. That same interface returned *inaccessible/tool error* for both un-tokened original variants and both Jetpack-transformed WordPress-view URLs. These are **6 retrieval-interface observations**, **not six HTTP status codes**, not real guest-browser network evidence, and not proof that the missing token caused visitor-visible breakage. Both images can already exist in a Jetpack cache even when the original without a token cannot be retrieved. Nothing was downloaded or mirrored.

| Key | Source with \`itok\` | Same source without \`itok\` | WP Jetpack view | Visitor status |
| --- | --- | --- | --- | --- |
| 288:5 Honda Point | Image rendered in web retriever | Tool inaccessible | Tool inaccessible | **Unknown** |
| 418:5 Hilo | Image rendered in web retriever | Tool inaccessible | Tool inaccessible | **Unknown** |

The [machine-readable six-route ledger](../qa/media-recovery/token_route_differential_2_20261115.json) contains all six exact HTTPS URLs and \`null\` for origin HTTP status, guest HTTP status, natural image width and transferred bytes. See [offline fail-closed validator](../qa/media-recovery/validate_token_route_differential_20261115.cjs) and [12 Node tests](../qa/media-recovery/test_validate_token_route_differential_20261115.cjs). The **12/12 native Node 22 tests passed on local files with identical Git blob SHAs** to this PR.

## Source authenticity and copyright

- **288:5, U.S. Naval Institute image:** Original image was rendered with \`itok=ex2XHVlK\`; publisher redistribution or hotlinking permission **unknown**. Navy [NH 69587](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69587.html) is a **different aerial frame**, held with Naval Historical Foundation / Admiral William V. Pratt credit. It is not a drop-in replacement and rights are not cleared.
- **418:5, U.S. Geological Survey image:** Original with \`itok=ASMRCahz\` rendered in the web interface. [USGS catalog](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946) describes debris covering a vehicle and labels the catalog image **Public Domain**, but says the original photographer/source is **unknown**. Pixel-equivalence, metadata and legal reuse of the exact version remain on hold.
- Drupal's [published token/CDN discussion](https://www.drupal.org/project/drupal/issues/1934498) explains why image-derivative URLs can be sensitive to \`itok\`; absence of the token alone does not establish HTTP 403.

## Isolated, reversible WordPress/CDN decision path

1. Site QA #154 must complete the **existing six P0 cold mobile/desktop guest-browser checks first**. Then use its existing CDP collector for 288:5 and 418:5, scrolling each element into view and recording \`currentSrc\`, all image Network request/redirect/response records, MIME, \`naturalWidth\`, actual encoded transfer bytes, cache provenance, and focused screenshots. Compare the token-bearing source, non-token source, and actual Jetpack view route under matched conditions. Neither a web-reader tool error nor a raw-origin 403 is accepted as browser failure.
2. If a route genuinely fails, require exact photographed scene/crop, confirmed source identity, item-level copyright/license/credit, and permission to cache/upload. Do **not** automatically remove Jetpack, proxy around upstream restrictions, or silently choose a different historical frame.
3. When authorized, stage a *single*, reversible WordPress Media candidate: preserve original source/caption and rollback data; max width **960px without upscaling**, proportional height \`round(H * min(960,W)/W)\`; **native W/H are not verified**, so review output dimensions remain \`null\`. Generate responsive sizes only after a legitimate file is available and rights are approved, retaining required attribution and inspecting crops for visual integrity. No production block rewrite is authorized.
4. Validate before/after images on cold mobile and desktop, with real CDP transfer bytes and screenshots. The historical **61 posts / 355 images / 288 external-source dependencies**, alleged **42 broken** and proposed **76% reduction** remain separate and unverified by this six-route experiment. Latest separately verified WordPress originals: **20 above 1.5 MB / 64,385,752 stored bytes**, not visitor transfer.

**No media binaries copied, no WordPress writes, deployments, merges, homepage design changes, or subscription spending.**
