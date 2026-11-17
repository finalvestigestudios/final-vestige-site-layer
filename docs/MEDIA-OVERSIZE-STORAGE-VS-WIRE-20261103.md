# November 3: WordPress oversized-original storage is NOT a 76% page-weight reduction

## Evidence and decision
Snapshot: authenticated WordPress.com Gutenberg and media library inventory **October 30, 2026**, 110 image media items (64,900,772 original bytes); 61 published investigations / 355 stored inline <img> source references. Evidence is pinned in the companion machine file and verified by offline code. No guest-browser request, cache/CDN response, compression, decoding, mobile screenshot or measured wire bytes was collected in this run: this environment's HEAD probes failed DNS resolution for finalvestige.com and i0.wp.com (curl HTTP 000; not server outages).

**13 originals exceeding 1.5 MiB total 43,522,829 bytes (41.51 MiB)**, or **67.06% of measured stored original bytes** (NOT measured site download traffic). **Seven** have exact `src` matches within the 61-post Oct 30 source snapshot, totaling **23,619,602 original bytes** (22.53 MiB). The **six** other originals total **19,903,227 bytes** (18.98 MiB), but could appear as featured, theme, product or other assets; absence from this inline-only corpus does NOT establish they are unused. The existing 1024px Jetpack URLs for some originals are *not* evidence that browsers requested these bytes.

### Seven originals to prioritize for real browser and rights audit
| Media ID | Original bytes | Exact post slot | Conditional derivative size (not produced) |
|---|---:|---|---|
| 1258 | 5,553,669 | 621:1 | 960×649 |
| 1257 | 4,798,395 | 621:0 | 960×720 |
| 39 | 2,892,087 | 34:0 | 960×540 |
| 43 | 2,836,245 | 38:0 | 960×540 |
| 40 | 2,552,136 | 35:0 | 960×540 |
| 41 | 2,498,247 | 36:0 | 960×540 |
| 42 | 2,488,823 | 37:0 | 960×540 |

The two Malbone originals (1258, 1257) are the largest **confirmed inline source matches**. Five other linked originals (IDs 39–43) are PNGs in posts 34–38. Preserve any fine lines, transparency, annotations and meaningful text when comparing WebP/AVIF/JPEG *proposals*; no automatic format conversion or lossy processing is approved.

### Six originals not directly linked in this snapshot
- Media 388: 8,176,362 bytes; 960×639 maximum plan. Current use outside inline investigation <img> unknown.
- Media 389: 2,822,969 bytes; 960×634 maximum plan. Current use outside inline investigation <img> unknown.
- Media 382: 2,318,980 bytes; 960×640 maximum plan. Current use outside inline investigation <img> unknown.
- Media 482: 2,293,016 bytes; 960×540 maximum plan. Current use outside inline investigation <img> unknown.
- Media 405: 2,201,573 bytes; 960×1200 maximum plan. Current use outside inline investigation <img> unknown.
- Media 293: 2,090,327 bytes; 960×1200 maximum plan. Current use outside inline investigation <img> unknown.

### Methodology to verify or reject claimed 76% reduction
1. **Freeze comparable baselines:** logged-out mobile and desktop browser, same set of 61 public post URLs and image positions, same viewport/DPR, cache cold then warm separately, same service-worker state, scroll to load lazy images, 3+ repeat passes per condition. Store timestamp and deployed revision/HTML content hash. Log failed/decode image assets, not simply network errors.
2. **Join image evidence to actual use:** `img.src`, `img.currentSrc`, `srcset`, `sizes`, `naturalWidth`/`naturalHeight`, `img.decode()`, CSS/object-fit, alt/credit and visual screenshot. CDP Network.requestWillBeSent / responseReceived / loadingFinished `encodedDataLength`, final URL, HTTP code, MIME, transfer size, cache flags, redirect chain; capture errors. Resource Timing alone is unreliable for cross-origin entries without Timing-Allow-Origin. Filter true image bytes; exclude HTML/JS and duplicate browser/CDN cache hits under the declared metric. Do not infer bytes from file size or response Content-Length alone.
3. **Control denominator:** state whether comparison is **sum of cold per-page image wire bytes** or **unique image downloads across a 61-post navigation session**—both valid but different. Hold the test cohort constant; count missing/broken requests separately (do not misreport zero-byte failure as optimization). Use median per-page or aggregate matched-page sums, report both before and after and exact list of changed assets.
4. **Compute only after actual bytes:** `reduction_pct = 100 * (baseline_image_wire_bytes - after_image_wire_bytes) / baseline_image_wire_bytes` with baseline > 0, matched pages and device; guard missing bytes and instrumented browser 304/cache. An unmeasured “76%” is neither achieved nor validated.
5. **Safe staged release:** obtain item-specific rights/attribution (including archive third-party collections); use visually matching rights-cleared assets, derivatives no wider than **960px**, never upscale; preserve aspect ratio and captions/ALT; upload separate WordPress media only after explicit approval, then visual/decoding/CLS/transfer before-after and rollback. Never replace Gutenberg block JSON en masse or touch homepage designer's CSS. Coordinate guest-browser data gathering with Site QA #154; this branch owns storage sizing, asset candidates and measurement contract.

### Test / safety boundary
`node qa/media-recovery/validate_oversize_storage_priority_20261103.cjs` checks the immutable snapshot joins, exact totals, 960px geometry and **NULL browser/weight measurements**. `node qa/media-recovery/test_oversize_storage_priority_20261103.cjs` is a mutation regression suite; independent precommit V8 exercised source checks and six fail-closed negative mutations, but **native Node/CI and logged-out browser not yet run**. There were no media downloads, localizations, production WordPress writes, homepage changes or purchases.

Site QA #154 retains P0 guest browser targets **285:5, 285:2, 287:5, 418:1–2, 407:1**. This is a distinct byte-accounting and size-reduction lane, NOT a duplicate image-broken-source draft.
