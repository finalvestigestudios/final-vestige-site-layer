# Florida Memory image continuity — seven exact catalog matches (2026-11-06)

**Scope:** published article [They Buried the Dead Apart](https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/) (WordPress post 432). **Evidence/QA only:** no homepage work, production writes, third-party downloads/caches or subscription spend. Extends existing media draft #1228. Site QA draft #154 retains visitor-browser verification; this does NOT duplicate that collector.

## Evidence and root concern

Read-only `wpcom_mcp_posts_get` in edit context verified **seven stored inline `<img>` references** from `www.floridamemory.com/fpc/...` and seven image tags without explicit width/height in stored markup. Runtime HTML may differ. The existing references all point to their **same original catalog image identifier** (not unrelated visual substitutes).

All seven raw JPG URLs were attempted through the text web retriever on **November 6, 2026**. **Each returned an internal retriever wrapper 500 after a www → apex host redirect**, with the apex image inaccessible to that retriever. These are NOT guest-browser response codes, NOT proven origin HTTP 500s and NOT evidence of seven broken images. Source image binaries, decoded dimensions, network transfer bytes, screenshots, crop identity and actual browser outcome all remain **unknown**. The seven corresponding catalog records were discovered through the primary archive's indexed pages; their direct URLs were not independently guest-browser tested.

| Post image | Original catalog ID | Primary item page | Catalog identity | Link housekeeping |
|---|---|---|---|---|
| 432:0 | PR04493 | https://floridamemory.com/items/show/4144 | Woodlawn cemetery funeral, 1928 | already points to specific record |
| 432:1 | RC17068 | https://floridamemory.com/items/show/38362 | Avenue A flooding, **Belle Glade**, Sept. 1928 | currently goes to group exhibition |
| 432:2 | RC10673 | https://floridamemory.com/items/show/33289 | Belle Glade automotive garage destroyed, 1928 | already specific |
| 432:3 | N031889 | https://floridamemory.com/items/show/141398 | State Board of Health HQ, Pahokee, 1928 | already specific; catalog marks M. Safan(?) uncertain |
| 432:4 | RC04344 | https://floridamemory.com/items/show/27848 | coffins beside Belle Glade canal, 1928 | currently goes to group exhibition |
| 432:5 | RC07668 | https://floridamemory.com/items/show/30741 | victims' burial, West Palm Beach, 1928 | currently goes to search results |
| 432:6 | MSF-PB11548-001 | https://floridamemory.com/items/show/340182 | historic African-American mass-burial site **photographed in 2001** | already specific |

**Historical-integrity corrections for later editorial review:** RC17068's precise location (Avenue A in Belle Glade) should not be lost behind a generic flooding caption; preserve distinction between the original 1928 disaster and the **2001** site photograph. Never substitute RC04343 for RC04344 (similar subject, different image).

**Source rights:** Florida Memory's [ordering FAQ](https://floridamemory.com/share/order-info/faq.php) explicitly says its images are offered under **Creative Commons Public Domain Mark 1.0 (PDM)** and require archive credit under **Florida Statutes §257.35(6)**. PDM identifies a public-domain status; it is not a license conferring new permission. Preserve existing caption credit `State Archives of Florida / Florida Memory`; **item-level rights/identity review remains HOLD** before any rehosting.

## Safe repair pipeline (conditional only)

1. **Site QA #154:** logged-out Chrome desktop/mobile checks on all seven URLs. Log final image request URL and HTTP status, decoded `naturalWidth`/`naturalHeight`, response bytes, true transfer sizes, screenshot, runtime `srcset` and any Jetpack rewriting. Only then classify genuinely broken images; do not convert retriever wrapper errors to origin failures.
2. For confirmed failures, first compare the same catalog's current image/rendition with displayed original, including cropping and historic subject. Verify the item-specific rights, credit and quality. No scraping or proxy mirroring of unrelated images.
3. The catalog provides physical photoprint size, **not intrinsic pixel geometry**. Therefore proposed derivative pixels are **NULL**, subject to original pixel readback. If rights permit, use a controlled WordPress **staging** derivative no wider than **960px**, with no enlargement, appropriate aspect ratio, intrinsic dimensions and responsive sources. Retain the archive item credit/link. Do not rewrite Gutenberg blocks in bulk.
4. Test visual similarity, caption accuracy, ALT, image layout stability (CLS), full-resolution preservation where needed, license/credit visibility, desktop/mobile transfer before/after and cold cache. Obtain explicit separate production release approval.

The original **61 articles / 355 image refs**, latest **66 / 361**, alleged **42 broken originals**, and proposed **76% reduction** are tracked separately: alleged failure count is **not** guest-browser verified, and the 76% saving is **not** cold transferred-byte measured. The 13 oversized WordPress originals totaling 43,522,829 stored bytes are likewise **not** visitor wire bytes.

## Files and repeatable tests

- `qa/media-recovery/florida_memory_seven_20261106.json`: seven exact source/catalog URL rows, provenance, rights/credit, explicit unknown browser status/pixels and zero-publication gates.
- `qa/media-recovery/validate_florida_memory_seven_20261106.cjs`: offline fail-closed audit validator.
- `qa/media-recovery/test_florida_memory_seven_20261106.cjs`: 22 normal/mutation checks covering source identity, cannot-invent-status, license, dimensions, rights, cache, WordPress, and 2001 chronology.

Run: `node --test qa/media-recovery/test_florida_memory_seven_20261106.cjs` and `node qa/media-recovery/validate_florida_memory_seven_20261106.cjs`. No browser/production writes should occur. The user's requested `docs/IMAGE-WEIGHT-WORKLIST.md` returned **404 on both main and this PR branch** at audit time; do not treat it as reviewed.
