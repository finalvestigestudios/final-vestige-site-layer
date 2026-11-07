# Final Vestige media recovery: Lituya Bay post 277, source and visual fidelity

**Audit date:** 2026-11-07. **Scope:** only third-party images, not homepage aesthetics.
**Published article:** https://finalvestige.com/2026/08/19/the-boat-went-over-the-trees-lituya-bay/
**Frozen inventory:** `qa/media-recovery/parts/04.json` at commit `f69a12cd9241ea0f39cfcb74c669bb6f7fb10357` (source census 2026-10-30). The frozen post modification time was 2026-08-21T00:32:52. **A fresh WordPress edit-source read and live guest browser capture were unavailable**: do not describe these six URLs as the currently loaded `currentSrc` values.

## Findings that alter the restoration decision

- **277:0** [commercial origin](https://www.datosfreak.org/wp-content/uploads/2019/01/Tsunami-maremoto-Lituya-Alaska-1958-1.jpg) **rendered in the independent web viewer** as a *two-panel annotated collage*, not the single aerial photograph implied by the frozen stored alt. The upper diagram includes arrows and numerical annotations; lower panel contains labels. A generic 1958 USGS aerial would be a **different graphic**, not an exact replacement. Proposed *editorial review*, not posted: “Annotated two-panel reconstruction and aerial illustration marking the 1958 Lituya Bay tsunami's run-up.” Authorship and graphic component rights UNKNOWN; no rehosting.
- **277:1** ResearchGate figure URL could not be fetched by independent viewer (tool `DisabledError`). **This is NOT an HTTP 403 or a guest-browser failure.** A historic USGS aerial is a topical alternative, not an established identical figure.
- **277:2** commercial S3-hosted historical scar image rendered; no exact USGS original matching the composition established. Provenance/copyright HOLD.
- **277:3** commercial greeting-card image URL inaccessible to viewer. It is not evidence of origin 404, nor is the image or reproduction permission known. USGS archival shoreline trimline photographs have analogous subject matter, NOT known image identity.
- **277:4** Medium-hosted image rendered with **red and yellow arrows overlaying a 1958 Lituya Bay aerial**. The Commons [annotated version](https://commons.wikimedia.org/wiki/File:Lituya-Bay-overview-with-arrows.png) is a 750 × 580 PNG; the [original unannotated USGS photograph rendition](https://commons.wikimedia.org/wiki/File:Lituya_Bay_overview.jpg) is 750 × 580 JPEG. The [official USGS page](https://www.usgs.gov/media/images/lituya-bay-1958) credits **Don J. Miller** and identifies a public-domain 1958 image. The old frozen alt omits the arrows. *Switching to the clean photograph would remove interpretive markup*: preserve arrows or explicitly approve changed editorial meaning; exact pixel/crop matching and arrow authorship remain HOLD.
- **277:5** published Commons direct image rendered as a **false-color 2020 Landsat 8 NASA graphic with labels, inset and historic line markings**, not an unannotated satellite photograph. The [Commons item](https://commons.wikimedia.org/wiki/File:Lituyabay_Earth_Observatory_image_2020.jpg) records **720 × 480 original** (489 KB), credit **Lauren Dauphin, NASA Earth Observatory**, USGS Landsat data and a NASA public-domain declaration, sourced to the [NASA article](https://science.nasa.gov/earth/earth-observatory/lituya-bays-apocalyptic-wave-147557/). **No 960px enlargement**: maximum derivative is native 720 × 480. Existing alt's “forest regrown around the shoreline” assertion is not established solely from the image. Proposed accurate alternative: “False-color Landsat 8 view of Lituya Bay in 2020, with labeled 1958 rockslide area and tsunami forest trimline.” Check NASA item's reuse conditions and avoid suggesting endorsement.

**All six original frozen source URLs and method-separated web-viewer observations are in** `qa/media-recovery/lituya_277_six_sources_20261107.json`. Retrieved/rendered `277:0,277:2,277:4,277:5` = **4**; viewer-blocked/inaccessible `277:1,277:3` = **2**. **Origin HTTP response status: not captured for any of the six. Actual guest-browser failures: none established.**

## Rights, pixel dimensions and cache/media staging controls

| Documented candidate | Original documented geometry | Safe derivative maximum | Condition |
|---|---:|---:|---|
| USGS 1958 Lituya Bay official aerial | Not verified from downloaded bytes | Unknown; don't generate | Primary catalog; compare exact crop |
| Commons USGS clean aerial | 750 × 580 | **750 × 580** | Remove arrows only after editorial approval |
| Commons USGS aerial with arrows | 750 × 580 | **750 × 580** | Confirm overlay creator/rights and precise rendition |
| Commons USGS Lituya spur | 750 × 576 | **750 × 576** | Alternate subject/composition; no automatic match |
| Commons USGS trimline | 700 × 440 | **700 × 440** | Alternate subject/composition; no automatic match |
| NASA 2020 false-color graphic | 720 × 480 | **720 × 480** | Preserve annotations, date, credits; no enlargement |

The **960px rule is a maximum, not a minimum**; use width `min(native_width, 960)`, height `round(native_height × width/native_width)`. These dimensions are **archive/catalog renditions**, not evidence of native dimensions actually shipped by Final Vestige. Catalog public-domain indications are not blanket grants for commercial annotations, third-party publisher crops, or recognisable persons. Do not download any media, create a WordPress attachment or change published blocks without per-item rights, attribution and visual-identical approval.

**Conditional WordPress media plan (no action taken):** accept Site QA's real guest-browser failure evidence first; choose *exact* rights-cleared candidate and verify binary pixels, crop, annotations and metadata; record source URL, archive record, screenshot pair, license/credit, master SHA-256; create no-upscale optimized derivative and responsive size variants in an isolated staging environment; attach proper credit and accurate alt/caption; only after explicit publish approval, plan a single scoped post change with rollback. If no exact match is suitable, retain a working hotlink while seeking rights or propose a separately approved editorial replacement; no silent historical substitution.

## Site QA handoff — use existing #154 / #1395 collector, do not duplicate

After the six existing P0 image slots (285:5, 285:2, 287:5, 418:1, 418:2, 407:1), use logged-out desktop ~1440px and mobile ~360px viewports, scroll all article images into view, disable cache, and capture `img.currentSrc`, request/redirect chain, real response status, MIME, encoded transfer bytes, `img.complete`, `naturalWidth`/`naturalHeight`, decoding outcome and side-by-side visual crop screenshots. Prioritize **277:1 and 277:3** for possible genuine failures, then **277:0, 277:4, 277:5** for misleading pictorial descriptions and markup/false-color identity. Do not equate retriever errors with customer failures.

## Site-wide weight accounting, no unsupported performance claim

Keep cohorts distinct: original **61 posts / 355 source image references / 288 offsite** in Media Recovery #183 versus independent Site QA #154's **286 offsite** (delta unresolved); later **66 posts / 361 references** cannot be mixed into the same denominator. A claim that **42 images are broken** needs per-slot guest Chrome evidence; current record does not show it. A claimed **76% image-weight reduction** needs measured before and after *encoded transferred image bytes*, not stored WordPress originals or theoretical converted file sizes. Collect cold, repeatable full-scroll waterfalls with controlled user-agent, viewport, CDN and cache state; aggregate `(sum(before_bytes)-sum(after_bytes)) / sum(before_bytes)` for an unchanged page cohort, report both absolute bytes and percentage alongside LCP/CLS. Include any failed transfers and redirects, don't sum unweighted post percentages. Thirteen >1.5MiB original WordPress library entries total **43,522,829 stored bytes**, not measured bandwidth. Existing Jetpack proxies may reduce real downloads.

## Isolated technical gate

- Audit JSON: `qa/media-recovery/lituya_277_six_sources_20261107.json`
- Validator: `qa/media-recovery/validate_lituya_277_20261107.cjs`
- Tests: `qa/media-recovery/test_lituya_277_20261107.cjs`
- **Independent committed-file replay:** 35/35 tests passed (one authentic fixture + 34 negative mutations) using a Node-compatible isolated V8 harness. Native `node --test` against the final Git checkout and GitHub CI still required. The validator fails closed on invented browser statuses, inflated image sizes, unverified identity, missing alt disclaimers, unlicensed caching and WordPress writes.

**Production:** zero fixes, zero uploads/downloads/caching, zero WordPress writes, zero homepage design changes, zero paid subscriptions. Proposed archival candidates are NOT cleared assets.
