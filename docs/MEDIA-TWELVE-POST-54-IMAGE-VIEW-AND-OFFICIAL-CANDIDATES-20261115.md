# 2026-11-15 — additional 12-post / 54-image live WordPress VIEW audit and six official-source restoration leads

## Scope, evidence and status

Media Recovery independently read 12 **published** posts, WordPress REST `posts_get(context=view)` only: 1926, 1924, 1922, 1920, 1917, 434, 433, 431, 428, 425, 413 and 367. This is a **distinct cohort** from the previous P0 four-post / 26-slot and six archival-post / 42-slot cohorts. It is also not the alleged set of **42 browser-broken** images. No logged-out browser network/decoding or image binary fetch was run.

- **54/54 exact WordPress VIEW `img src` URLs** inventoried; routes are **27 direct Wikimedia Commons, 19 third-party origins through Jetpack, 8 FinalVestige originals through Jetpack**. No invalid URLs, no empty ALT on this sample.
- **46/46 third-party-origin images lack an explicit `srcset` and `sizes`** in REST view markup. The **8/8 first-party originals** have both and have explicit width and height. Overall **35/54** image tags omit at least one intrinsic-dimension attribute. This identifies an inline authoring/responsive-delivery risk to review; it is **not** browser-proven CLS, breakage, or extra transferred bytes.
- Apollo 1 post **434** uses five NASA-origin images through Jetpack. Their declared view dimensions include widths up to **1920px**, with no explicit `srcset` or `sizes` on those five tags. Declared attributes do not prove native dimensions, selected `currentSrc`, or actual bytes.
- Published change-blindness post **1922** contains zero inline `img` tags in this read-only view. This is not itself a missing-image finding.
- Prior independently verified WordPress attachment census: **132** image originals; **20** above 1,500,000 decimal bytes, totaling **64,385,752 stored bytes**. The four recent large **featured** images on posts 1917, 1924, 1920 and 1926 total **15,278,087 stored bytes**, but are not their posts' stored inline image files. Storage bytes are not guest traffic.

## New primary-source crosswalk — all restoration/caching HOLD

The separate six-record [NASA / Library of Congress candidate map](../qa/media-recovery/nasa_loc_six_official_candidates_20261115.json) ties exact currently rendered proxy URLs to **NASA official-host image IDs S67-15717, S66-58038, KSC-20170124-PH_KLS01_0164, S67-21294, KSC-20170124-PH_KLS01_0090** (Apollo 1 slots 434:1–5) and the **1905 Wallace Sanborn sheet 428:5**, Library of Congress item [sanborn01687_005](https://www.loc.gov/item/sanborn01687_005/). These are source/catalog candidates, **not confirmed visually identical replacement binaries**.

The [NASA media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally allow factual editorial imagery with NASA attribution but warn about third-party content, recognizable people, agency identifiers and non-endorsement. Item-specific review remains necessary. The [Library of Congress Sanborn catalog](https://www.loc.gov/item/sanborn01687_005/) labels the 1905 collection item public domain and provides recommended credit. A map must stay zoomable/legible; no source image was downloaded or cached.

For NASA candidates, manifest `conditional_width_960_display_aspect_px` derives **only** from WordPress view-declared display dimensions and is *not* an authorized export or measured native geometry. Exact dimensions are blocked until lawful file access, intrinsic inspection, rights clearance and no-upscale validation. For the LoC map the proposed dimensions remain null.

## Safe next work; Site QA coordination

1. Site QA **#154** retains responsibility for the original **six P0 cold guest Chromium checks**: `currentSrc`, cold CDP Image request/redirect/response chain, cache flags, HTTP, `naturalWidth`/`naturalHeight`, screenshots, and mobile/desktop proof. No duplicate collector was introduced here. The reported **42 broken originals remain unconfirmed**.
2. Once a specific image is *visitor-confirmed missing*, review exact historical scene, author/license, primary catalog and attribution. Preserve ALT and chronology. Only then consider a **lawfully obtained** file with SHA-256 and native geometry.
3. On separate **isolated staging** (not production), compare a reversible WordPress Media Library candidate or existing lawful cache at max **960px width**, proportional and never upscale. Preserve maps' zoomable masters and visual legibility; compare desktop/mobile rendered pages and before/after real cold-image bytes.
4. Do not change site homepage design (interim lead's scope), published Gutenberg blocks, production WP media, subscriptions or payment controls. No third-party media scraping/mirroring, no production writes, merges or deployments.

The earlier frozen baseline is **61 posts / 355 stored images / 288 external-origin dependencies**. Site-wide **76% transferred-byte reduction remains unmeasured**.

## QA / provenance

- [Exact 12-post / 54-image audit](../qa/media-recovery/wp_twelve_remaining_posts_view_routes_20261115.json), Git blob `0174b969d519450801e3ed1597d8be1d02d7aab6`.
- [Fail-closed validator](../qa/media-recovery/verify_live_view_12_20261115.cjs), requires 12 exact posts, 54 distinct positional slots, classification of Jetpack by **underlying origin**, matching image attribute counts, unknown guest statuses, zero rights/write grants and max-960 HOLD.
- [19-case regression suite](../qa/media-recovery/test_verify_live_view_12_20261115.cjs): **19/19 passed in isolated V8 Node-compatible shims against committed files**; native Node and GitHub CI still pending.
- [Six official-source candidate manifest](../qa/media-recovery/nasa_loc_six_official_candidates_20261115.json), Git blob `32570c9091adf9fc556f4ce79bf915cb1452a84e`.

Neither 42 alleged failures nor 76% network saving was inferred from source markup.
