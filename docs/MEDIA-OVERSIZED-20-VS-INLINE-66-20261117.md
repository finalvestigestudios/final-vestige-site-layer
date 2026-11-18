# Media originals above 1.5 MB: stored bytes vs real inline references (2026-11-17)

**Read-only.** Sources: 132 current WordPress image-library media records and complete 66 published-post WP VIEW HTML (361 image slots). GitHub evidence is in `qa/media-recovery/live_media_over_1_5mib_20261117_1624pt.json` (20 item-level records with exact URLs, dimensions and conditional no-upscale sizing) and `qa/media-recovery/live_20_oversized_to_66_post_inline_crosswalk_20261117.json` (exact post:slot matches, attachment parent and responsive flags). The filename contains legacy “mib”; the v2 JSON explicitly distinguishes decimal and binary thresholds.

## Verified threshold trap

- **1.5 MB decimal = 1,500,000 bytes:** **20 stored image originals** totaling **64,385,752 original bytes**, precisely reconciling the earlier 20-item report.
- **1.5 MiB binary = 1,572,864 bytes:** **19 originals** totaling **62,842,750 original bytes**. The difference is precisely **media item 1714**, `2026/10/halifax-explosion-map.png`, **1,543,002 bytes**, which falls between the thresholds.
- Both are counts of stored **media library originals**, not visitor network requests and **not bandwidth savings**.

## Fresh 66-post exact-src crosswalk

Only **11 of those 20 media originals** occur as exact source-origin paths in the published VIEW `img src` attributes (11 matching visual slots; **38,480,915 original stored bytes**). The other **nine** (25,904,837 original bytes) have no exact *inline src* match in these 66 posts. This **does not** establish that those nine are unused: they may appear as featured images, background assets, srcset-only variants, downloads or in other post types.

**Confirmed inline path matches** include Vasa post **299** (8,176,362-byte model photo 299:1, 2,822,969-byte ship photo 299:0, 2,318,980-byte support photo 299:7), Malbone **621** (5,553,669-byte archive 621:1 and 4,798,395-byte tunnel 621:0), Halifax map **269:1**, and five first-party PNG illustrations at posts **34–38** (2.49–2.89 MB originals).

**Important responsive-image distinction:** Six of the eleven inline image tags have both `srcset` and `sizes`, and all five legacy PNG tags lack both. **However, the five legacy PNGs already have Jetpack `src` values requesting `resize=1024,576`**, not URLs proving that their multi-megabyte originals are downloaded. This is a strong reason to **measure the real guest GET and transfer bytes** before optimizing media library originals.

Highest stored original with no exact inline match is **Piri Reis 7,422,309 bytes** (attachment parent 1917); Mesmer **4,462,854 bytes** (parent 1924) is another. Their parent IDs do not prove the file is delivered inline, nor that optimization is pointless if used as featured images.

## Safe action queue, after Site QA guest image evidence

1. **P0 visitor-visible broken images** remain 285:5, 285:2, 287:5, 418:1, 418:2 and 407:1, with exact src pinned in the live 66 rollup. Existing Site QA collector owns logged-out desktop/mobile checks.
2. **P1 actual delivered bytes:** In the collector capture on Vasa 299, Malbone 621, and first-party illustrated posts 34–38: `currentSrc`, final GET/redirect/MIME, decode, HTTP status, *unique* cold transferred image bytes, screenshot and LCP/CLS. If Jetpack serves 1024px or lower, count delivered bytes and not original storage size.
3. **P1 candidate asset review:** For any proven heavy image actually transmitted, confirm individual rights, actual master SHA-256, crop/scene fidelity, native dimensions and a no-upscale width cap of 960px. Compute sizes proportionally; do not silently change the historical photograph or attribution.
4. **Only after permission and visual QA:** Create a reversible staging-only WordPress media/Jetpack variant plan with image ID, alt/caption/credit, responsive `srcset` and rollback reference. No Gutenberg raw block rewrites, unlicensed downloads, blind caching or live uploads.
5. **76% performance claim:** Do not claim savings until same-image-slot before/after guest-browser waterfall evidence (no false savings from failed images), confirmed screenshots, LCP/CLS and the exact-byte calculation.

**Scope:** No WordPress writes, homepage visuals, image retrieval/rehosting, draft duplication, merges, deployments or spending.
