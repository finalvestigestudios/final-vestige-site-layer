# Hebgen 407:1 — two USGS catalogs, different Original routes (Nov 16, 2026)

## What changed (read-only)

Fresh authenticated WordPress `posts_get` EDIT and VIEW agree on post 407 (modified `2026-10-29T18:30:30`) and 0-based slot 1. Its `<a>` points to the **USGS `.../hebgen-lake-fault-scarp-1959-0`** item; its authored `<img src>` points to `.../s3fs-public/img7535.jpg`; the WordPress VIEW image is Jetpack `i0.wp.com/.../img7535.jpg?ssl=1`. Neither EDIT nor REST VIEW establishes guest browser image success/failure.

Critically, the **USGS catalog actually linked by WordPress** exposes an *Original* link ending `/s3fs-public/img7535.jpg`. Public web-reader `click` returned `(400) Unsupported content-type: binary/octet-stream` for that link; the `(400)` is an **image-reader failure**, not proof that the origin or browser returned HTTP 400. A second **separately published USGS catalog** at `.../hebgen-lake-fault-scarp-1959` exposes an *Original* ending `/s3fs-public/thumbnails/image/img7535.jpg`; the public image reader rendered it. The WordPress Jetpack proxy was inaccessible to this reader. Therefore the sibling route is a significantly more actionable single-slot fallback candidate, **not** a demonstrated browser outage, exact-byte proof or authorization to rewrite posts.

Both USGS item records identify the same image title, photographer J. R. Stacy and **Public Domain** source designation. Photo sameness across crops and bytes still needs actual side-by-side visual comparison and image metadata; no binary has been downloaded. Leave live attribution and ALT untouched.

## Source custody, delivery and rights

- On-post source catalog: https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0
- On-post source Original and current authored URL: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg
- Sibling official catalog: https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959
- Sibling Original: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg
- WordPress REST VIEW proxy: https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg?ssl=1

Do not infer native image dimensions from public-reader previews. Conditional derivative is `w=min(960,native_w);h=round(native_h*w/native_w)` with **no upscaling**, preserving crop/visual identity and USGS photographer/source credit. Do not cache, mirror, alter Gutenberg block markup, change global Jetpack, upload media or ship any site modification before independent per-item rights/credit review and guest-browser proof.

## Exact acceptance and Site QA handoff

Use **existing Site QA #154** logged-out browser collector (do not duplicate) to capture P0 slot 407:1 `currentSrc`, original and proxy HTTP GET response/MIME/redirect/transfer bytes, `naturalWidth`/`naturalHeight`, screenshots and image error events. Compare *both official* Original URLs in the same environment. Distinguish upstream MIME error from proxy/guest behavior. If the displayed slot is actually broken and the sibling image is visibly identical, prepare a one-slot **reversible QA-only staging proposal** with before/after screenshot, attribute/credit parity, capped 960px derivative and rollback instructions; no production WordPress write without separate authorization. If guest view succeeds, close as dependency risk, not breakage.

## Metrics kept separate

61 articles / 355 source image refs (historical); 66 posts / 361 inline image refs (later); 42 reported broken images not guest-confirmed; 76% visitor image weight reduction **not measured**; latest 20 original WordPress media files above 1.5 decimal MB store 64,385,752 bytes, which does **not** indicate transferred browser bytes. No downloads, homepage changes, production writes, deploy, merge or spend.

[Machine audit](../qa/media-recovery/hebgen_catalog_alias_fidelity_20261116.json) · [validator](../qa/media-recovery/validate_hebgen_catalog_alias_fidelity_20261116.cjs) · [native Node tests](../qa/media-recovery/test_hebgen_catalog_alias_fidelity_20261116.cjs)
