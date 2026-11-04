# Media Recovery #183 — Hebgen Lake post 407: USGS exact-original comparison and one path discrepancy (Nov 3, 2026)

**Scope:** Eight exact stored 2026-10-30 Gutenberg `src`/ALT references from `qa/media-recovery/parts/02.json` (Git blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`). This is **not** a new WordPress CMS read, a guest-browser test, or a measured transfer experiment. Site QA PR #154 owns browser verification. Do not edit the homepage or any QA scanner.

## Material result: seven exact USGS originals, one suspicious published path

Opened eight USGS canonical catalog pages and their primary linked image URLs. **Seven catalog `Original` URLs exactly equal the seven stored Final Vestige source URLs**, and those seven original image URLs **displayed in the independent image viewer**. This supports source provenance; it is *not* numeric HTTP 200, successful Chrome decode, or matching binary checksum.

**407:1** is the single exception. The frozen published source is:

`https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`

The official [USGS 1959 Hebgen fault-scarp record](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959), credit **J. R. Stacy**, currently links its **Original** image to:

`https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg`

The USGS-linked image **visibly displayed**; the published bare `/img7535.jpg` was rejected by the independent text retriever as **unsupported `binary/octet-stream`**. The wrapper code **400 is not an HTTP response from the source**. It is not proof the visitor sees a broken picture. This is a precise same-publisher candidate path to test **first**, *before* any rehosting or replacement.

**407:3:** Prior audit `hebgen_407_usgs_octet_cross_transport_20261103.json` marked its original URL inaccessible without a numeric status. A later independent viewer invocation of the USGS canonical **Original** link displayed `EarthquakeLake3.jpg` with its exact stored source URL; this fresh transport observation changes its status to **viewer-displayed** (not browser-confirmed). Avoid turning a temporary retriever failure into a false site outage. The USGS credit is **Mrs. Steven W. Nile**.

## Full original-link map

| Slot | Official USGS image record | Exact original URL matches stored src | Credit |
|---|---|---|---|
| 407:0 | [House in Hebgen Lake](https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau) | yes | USGS fact sheet names J. B. Hadley |
| 407:1 | [1959 fault scarp](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) | **NO — /thumbnails/image/ missing in published path** | J. R. Stacy |
| 407:2 | [Madison Slide, 21 Aug 1959](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake) | yes | William B. Hall |
| 407:3 | [Earthquake Lake dragline, 18 Oct 1959](https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959) | yes; **fresh viewer displayed** | Mrs. Steven W. Nile |
| 407:4 | [Golden Gate rockslide](https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs) | yes | Catalog does not identify individual creator |
| 407:5 | [Sapphire Pool eruption](https://www.usgs.gov/media/images/sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg) | yes | Catalog does not identify individual creator |
| 407:6 | [Seismic Geyser 1970](https://www.usgs.gov/media/images/seismic-geyser-eruption-1970) | yes | John Brandow |
| 407:7 | [Earthquake Lake, 27 Jun 2023](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) | yes | Mike Poland |

USGS labels all eight catalog records **Public Domain**, but several credit non-USGS photographers. Preserve each exact credit and conduct item-specific rights/crop verification before any local copying. Archive-page metadata does **not** establish identical downloaded bytes or every derivative's rights.

## Proportional geometry and staging plan

Known frozen **HTML box** dimensions, *not independently verified binary intrinsic sizes*: **407:2** 1024×719 → conditional **960×674**; **407:3** 1024×730 → **960×684**; **407:7** 1024×771 → **960×723**. For other five slots, record target width/height **null** until intrinsic master dimensions and exact crop are verified. Never enlarge a smaller image to 960px.

1. Site QA #154 logs out and lazy-scrolls post 407 on desktop and mobile; capture the actual `img.src`/`currentSrc`, final GET URL/status/MIME, `naturalWidth/Height`, `decode()`, screenshot, and CDP image `encodedDataLength`. Prioritize **407:1** and use **407:3** as a control; avoid assuming a common S3 hostname means common failures.
2. Only if 407:1 fails in real Chrome, compare the visibly displaying official USGS alternative for subject, crop, quality, and rights. Do **not** replace 407:3 merely because an earlier text retriever could not open it.
3. After per-item rights review, **request separate approval** for a single staging-only WordPress media derivative: retain the exact ALT, caption and source credit; stage a ≤960px no-upscale image with checksums, responsive `srcset`, width/height, a first-party URL and reversible original-source mapping. No automatic post block rewriting.
4. Verify staging on logged-out desktop/mobile and compare *actual transferred bytes* under identical conditions before claiming performance savings.

## Committed source-only verification

- [Eight-slot machine-readable ledger](../qa/media-recovery/hebgen_407_primary_path_audit_20261103.json) records the exact original URLs, canonical USGS links, dated observation methods, per-item rights HOLDS, conditional geometry, and null numeric HTTP/browser fields.
- [Offline archive-link and rights validator](../qa/media-recovery/validate_hebgen_407_primary_link_20261103.cjs) cross-reconciles frozen exact source+ALT, explicitly checks the one path difference, rejects false HTTP/MIME/decode/bytes and blocks unapproved cache/edit claims.
- [30-case positive/adversarial suite](../qa/media-recovery/test_hebgen_407_primary_link_20261103.cjs): **30/30 pass in isolated V8 execution of exact GitHub-committed source files**, *not yet native Node or CI*. The validator's native CLI additionally checks frozen part 02 Git blob identity.

**Site-wide baseline unchanged:** 61 articles, 355 stored image references, 288 external-origin refs, 13 first-party originals >1.5 MiB. The reported **42 broken** and **76% weight reduction** remain **unverified/unmeasured**. **Zero production repairs**; no image binaries downloaded/cached, WordPress writes, homepage changes or subscription spend.
