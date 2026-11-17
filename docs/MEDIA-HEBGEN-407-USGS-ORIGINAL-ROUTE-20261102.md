# Hebgen post 407 — USGS original-path recovery and eight-image rights crosswalk

**Read-only media engineering, 2026-11-02.** Scope is published post 407 (*The Lake Wasn't There Yesterday*), its eight exact frozen WordPress `img src`/ALT slots, and primary USGS catalog records. No production WordPress write, media download/republication, homepage change, or subscription spend.

## High-value finding — 407:1 has a catalog-original URL that differs from the published URL

- **Published dependency:** `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg` — independent web retriever rejected an **unsupported binary/octet-stream** with wrapper code **400**. This is **not** an observed origin HTTP 400 or a logged-out Chrome image failure.
- **USGS authoritative catalog:** https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959 — expressly says **Sources/Usage: Public Domain** and names photographer **J. R. Stacy (USGS)**.
- **USGS catalog's “Original” hyperlink:** `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg`. That **different path rendered as an image** in independent image viewer, displaying the 1959 fault scarp, with a roughly **1000×1000 viewer presentation**. It has the same archival filename `img7535.jpg`; **a matching content hash and original-master metadata were NOT obtained**.
- **Proposed restoration:** prefer a screenshot-verified, **same-scene** USGS original URL/rights-checked WordPress cache if Site QA's guest browser confirms real image failure. Conditional derivative **960×960**, not a measured master or produced binary. Image identity, production writes, licensing and caching **HOLD**.

This is a **specific path-relocation candidate**, unlike the unrelated substitute photographs often returned for disaster topics. The catalog's “Original” label does not establish an archival full-resolution master, a binary hash match, or permission to bypass a human rights review.

## Full eight-slot verified batch

Frozen source: `qa/media-recovery/parts/02.json` Git blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`. The WordPress article source URL and eight ALTs are unchanged from that snapshot; this sprint **did not perform a fresh authenticated WordPress readback**.

| Image key | Independent retrieval of *published* URL | Official USGS primary record | Credited creator / date | Conditional ≤960px geometry |
| --- | --- | --- | --- | --- |
| 407:0 | **Displayed** | [Floating Hebgen Lake house](https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau) | Unnamed catalog creator; circa 1959 | **960×642** from viewer preview |
| 407:1 | **Unsupported octet-stream wrapper 400** | [Hebgen fault scarp](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) | J. R. Stacy, USGS; circa 1959 | **960×960** from *alternate official catalog preview* |
| 407:2 | **Displayed** | [Madison Slide](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake) | Prof. William B. Hall; August 21, 1959 | **960×674** from stored HTML 1024×719 |
| 407:3 | **Web retriever inaccessible; no numeric HTTP status** | [Earthquake Lake dragline](https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959) | Mrs. Steven W. Nile; October 18, 1959 | **960×684** from stored HTML 1024×730 |
| 407:4 | **Displayed** | [Golden Gate rockslide](https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs) | Creator not named; circa 1959 | **960×623** from viewer preview |
| 407:5 | **Displayed** | [Sapphire Pool eruption](https://www.usgs.gov/media/images/sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg) | Creator not named; circa 1959 | **960×613** from viewer preview |
| 407:6 | **Displayed** | [Seismic Geyser](https://www.usgs.gov/media/images/seismic-geyser-eruption-1970) | John Brandow, USGS; 1970 | **678×1000**, preserve narrower original preview, **no upscale** |
| 407:7 | **Displayed** | [Earthquake Lake, June 2023](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) | Mike Poland, USGS; June 27, 2023 | **960×723** from viewer preview |

All eight catalog records independently state **Public Domain**. This is a primary-source record claim, not a determination that *every related photograph, rendition, or downstream copy* is unrestricted. Preserve private-photographer credits for 407:2 and 407:3, as well as exact image provenance; no automatic reproduction/caching approval. Records 407:2 and 407:3 were indexed in primary USGS search but their individual catalog page opens timed out; title/creator/usage statements were also indexed in USGS's official reporting. Viewer displays are **not** Chrome guest HTTP status, wire-byte measurement, and not proof that images will load on FinalVestige.com.

## Safe caching / visual-integrity execution plan (not authorized by this sprint)

1. Site QA #154 obtains a logged-out Chrome screenshot and image element `currentSrc`, `naturalWidth`, actual CDP Image request and response for **407:1**, then **407:3**, preserving failures and redirects. If the existing URL decodes, **do not replace it** merely because our text retriever rejected it.
2. Compare the rendered primary USGS catalog photo side by side against the website's intended photograph and ALT; verify individual reproduction rights, credited photographer, cropping, and any third-party restrictions. Explicitly preserve 407:7 as **2023 retrospective imagery**, not a 1959 photograph.
3. For an approved image, inspect its source binary **only with authorization**, hash image bytes and measure master geometry, create a ≤960px derivative **without upscaling**, strip unnecessary metadata without destroying archival legibility, and record resulting bytes, visual parity, format, ALT and credit. The listed 960px geometries are *conditional plans*, not generated files.
4. Stage under a distinct filename (e.g. `fv-hebgen-fault-scarp-usgs-stacy-960.jpg`) in a nonproduction review environment. Prepare one exact image-slot replacement diff, preserve Gutenberg blocks and other media, and create a rollback manifest. Only a **separate explicit WordPress production approval** permits caching/editing.
5. Repeat identical viewport/cache-disabled CDP screenshots and **request-ID-attributed** wire-byte capture before and after a permitted change. Do not derive a **76%** reduction from original-storage bytes or from eliminating a failed image's zero-byte request.

## Machine evidence, reproducibility and bounds

- [Eight-image machine ledger](../qa/media-recovery/hebgen_407_usgs_original_route_crosswalk_20261102.json) includes all eight exact published original URLs/ALTs, authoritative USGS links, independent retrieval outcomes, no-upscale plans, rights holds and **null visitor-browser statuses**.
- [Strict offline validator](../qa/media-recovery/validate_hebgen_407_usgs_20261102.cjs) pins frozen Git blob, sources, dates, scene identity, rights and statuses. [Twenty-two tests](../qa/media-recovery/test_hebgen_407_usgs_20261102.cjs) define one valid baseline and 21 unsafe mutation cases.
- One baseline and **21/21** adversarial mutations were exercised and passed in an isolated V8 execution of the validator logic against the exact committed ledger/snapshot source. Native Node execution and live browser CDP remain pending; execute `node --test qa/media-recovery/test_hebgen_407_usgs_20261102.cjs` in native CI.
- Site-level census remains **61 published posts / 355 stored image references / 288 external-origin references** (286 direct + 2 Jetpack), **13** original WordPress uploads >1.5MiB. The reported **42 broken images are unverified**, the alleged **76% wire-weight saving unmeasured**, and **0** images repaired in production.
- This work does **not** change Site QA PR #154 or the interim lead's homepage visual design.
