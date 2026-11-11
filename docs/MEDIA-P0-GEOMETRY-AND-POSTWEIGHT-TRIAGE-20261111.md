# P0 image crop parity and post-weight triage — 2026-11-11 UTC

**Status: isolated draft PR #1703 only. No guest-browser evidence, media download/cache, rights clearance, staging approval, WordPress edits, production deployment, homepage design edits, or spend.**

## New visual risk: Three Mile Island slot 285:5
Currently embedded original: `https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg`. The SayMedia URL expressly requests `ar_16:9,c_fill,w_1200`, **not evidence of delivered browser dimensions**. The original publisher explicitly credits [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg). That source is **819 × 614** (approximately 4:3), described as a June 6, 2010 photograph with the uploader's public-domain dedication. Its catalog lists a **235 KB source file**, not guest-transfer bytes.

**A straight replacement with 819×614 would change the aspect ratio of the 16:9 source-requested presentation.** A *hypothetical* 16:9 crop at 819px wide would be ~819×461 and discard approximately **153 vertical source pixels (24.9%)**. It is **not approved**: the original CDN crop, focal point, source visual equivalence, layout, licensing and user-facing interpretation remain unverified. No upscaling beyond 819px. Do not silently transform the archival source to 960px or treat the 2010 image as a 1979 accident photograph.

Sources: [publisher image credit](https://discover.hubpages.com/entertainment/The-China-Syndrome-Blockbuster-Movie-Becomes-Eerie-Prophecy) · [original Commons file/rights/geometry](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg).

## Actionable oversized-media exposure by post (stored-original bytes, NOT visitor transfers)
- Post **299**: **13,318,311 B**, media IDs 382, 388, 389, stored source style `jetpack_fit_transformed_in_stored_src`.
- Post **621**: **10,352,064 B**, media IDs 1257, 1258, stored source style `direct_original_in_stored_src`.
- Post **34**: **2,892,087 B**, media IDs 39, stored source style `direct_original_in_stored_src`.
- Post **38**: **2,836,245 B**, media IDs 43, stored source style `direct_original_in_stored_src`.
- Post **35**: **2,552,136 B**, media IDs 40, stored source style `direct_original_in_stored_src`.
- Post **36**: **2,498,247 B**, media IDs 41, stored source style `direct_original_in_stored_src`.
- Post **37**: **2,488,823 B**, media IDs 42, stored source style `direct_original_in_stored_src`.
- Post **269**: **1,543,002 B**, media IDs 1714, stored source style `direct_original_in_stored_src`.

Total 15 originals >1,500,000 B: **47,096,779 B**. Inline-linked 11 originals across 8 posts: **38,480,915 B**. Other four **8,615,864 B** have no inline use in the 66-post census; other surfaces may still use them, so they must not be deleted. Five original PNGs without WordPress subsizes: IDs 39, 40, 41, 42, 43, combined **13,267,538 B**; hypothetical 960×540 derivatives **not approved** pending creator rights and scene fidelity.

Highest **stored** total is Vasa post 299, but its three stored image source URLs already use Jetpack `?fit=1024` transformations. Therefore ranking storage alone could misallocate optimization effort. Prioritize **actual cold visitor network measurements** on directly embedded Malbone post 621 and five PNG posts 34–38, only after Site QA #154 verifies P0 missing images. Keep Halifax map post 269 on a small-label legibility hold.

## Correct 76% savings denominator
The stated 76% is **a target, not a measured result**. `savings = (sum(actual cold baseline encoded image transfer bytes) - sum(actual cold candidate encoded image transfer bytes)) / sum(actual cold baseline encoded image transfer bytes)`. Match *the same posts, rendered images, responsive currentSrc, DPR, viewport, caches disabled and requests deduplicated*. Different archival scenes, a post mix change, browser cached responses, mere original-file storage sizes, synthetic test bytes, or mock statuses invalidate the figure. This work does **not** duplicate PR #154's CDP collector or PR #183's wire-byte comparator.

## Strict QA/rights workflow
1. Site QA #154 provides **genuine logged-out browser status, request URL/currentSrc, intrinsic W/H, cache flags, encoded network bytes and screenshot** at mobile and desktop for six P0 slots in fixed order 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Retriever wrapper 404/403/500 is not HTTP proof.
2. For a proven failure, use same-photo provenance first, manual photo/crop/ALT identity and item-specific rights review. A government hosting domain alone does not establish commercial rehosting rights.
3. Only after separate staging approval: generate responsive <=960px variants without upscaling, preserve zoomable map/schematic annotations, include correct credits, stage one isolated change, repeat browser QA, document rollback. **Do not upload/rewrite production posts without distinct authorization.**
4. Current release state remains HOLD. All six visitor failure statuses and wire bytes are unknown, so no images are approved for rehosting or production.

Machine audit: `qa/media-recovery/p0_geometry_postweight_triage_20261111.json`; validator and 17-case Node-compatible adversarial regression suite alongside it.
