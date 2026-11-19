# Hebgen Lake post 407: eight-image USGS custody and safe recovery gate

Date: **2026-11-16, ~18:30 Pacific**. This is **read-only archival/media QA**, not a production remediation or a logged-out Chromium capture. No post, homepage, theme, media library, or third-party binary has been modified, copied or downloaded. Site QA [PR #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) retains ownership of the guest-browser collection; Media QA [draft PR #2747](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747) consumes that evidence.

## What is new

Authenticated WordPress EDIT and VIEW snapshots of [post 407](https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/) both report modification `2026-10-29T18:30:30`. Exactly **eight** authored USGS S3 images map to eight published `i0.wp.com` proxy IMG sources. All eight have ALT. **Five of eight** lack explicit width/height, and **all eight** lack `srcset` and `sizes`. These are structural responsiveness/layout-shift risks, **not measured CLS or visitor bytes**.

All **8/8** subjects have item-specific official [USGS multimedia catalog](https://www.usgs.gov/products/multimedia-gallery/all-multimedia) records that state **“Public Domain.”** Those labels support editorial reuse review but do **not** bypass binary identity, visual framing, credit, and explicit approval before WordPress staging.

| Slot | Official catalog record | Editorial credit / distinct finding |
|---|---|---|
| 407:0 | [Damaged house/Grace Miller](https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau) | J. B. Hadley, USGS (confirmed by [USGS 2005 fact sheet](https://pubs.usgs.gov/fs/2005/3024/)) |
| **407:1** | **[Hebgen fault scarp, 1959](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959)** | **J. R. Stacy, USGS. Current authored origin is `/s3fs-public/img7535.jpg` (independent retriever rejected octet-stream). USGS catalog “Original” points instead to `/s3fs-public/thumbnails/image/img7535.jpg` and this catalog route rendered in the independent reader. This is an exact primary-source *scene* candidate, not yet pixel/frame/hash-certified.** |
| 407:2 | [Madison Slide, Aug. 21 1959](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake) | Professor William B. Hall, Montana School of Mines |
| 407:3 | [Dragline outlet work, Oct. 18 1959](https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959) | Mrs. Steven W. Nile. First direct retriever request inaccessible, but clicking “Original” in the USGS item loaded the **same URL** successfully; this demonstrates why a single retriever error is insufficient to claim a visitor 404 |
| 407:4 | [Golden Gate rockslide](https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs) | Official USGS record public-domain; [parallel record](https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs-yellowstone-n) credits NPS |
| 407:5 | [Sapphire Pool, 1959](https://www.usgs.gov/media/images/sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg) | USGS public-domain item, creator not specified |
| 407:6 | [Seismic Geyser, 1970](https://www.usgs.gov/media/images/seismic-geyser-eruption-1970) | John Brandow, USGS |
| 407:7 | [Earthquake Lake and Madison Slide, June 27 2023](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) | Mike Poland, USGS |

**Delivery evidence scope:** public web retriever displayed six authored URLs directly; the dragline original rendered after a USGS catalog click despite its initial tool-inaccessibility; the scarp's current authored URL was rejected by the retriever as `400 Unsupported content-type: binary/octet-stream`, while the different official Original route rendered. No numeric HTTP statuses from a logged-out visitor, `currentSrc`, `naturalWidth`, MIME, content hashes, screenshots, `Network.loadingFinished.encodedDataLength` or cold-cache transfer bytes were collected. The displayed photographs are **tool-level evidence only**.

## Exact reversible candidate, P0 407:1

- Existing source: `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`
- **Authoritative USGS “Original” link:** `https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg`
- Current WordPress VIEW proxy: `https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg?ssl=1`
- Catalog rights: **Public Domain**; attribution **J. R. Stacy, USGS**. Preserve accurate historical label; assess original/candidate same photograph, framing and image metadata with decoded pixels before substitution.
- This is a **route candidate**, not an authorized post-block rewrite, even though the official image is reader-displayable.

## Image dimensions, performance, and staging

For slots 407:2, 407:3, 407:7, current rendered IMG tags contain ratios 1024×719, 1024×730, 1024×771. **Conditional** no-upscale display plan, *only if actual decoded native dimensions permit it*, is 960×674, 960×684, 960×723. **Other five slots have no verified native geometry**: do not invent 960px heights or upscale a sub-960px master. All eight should retain meaningful ALT and appropriate source credits and, if staged, explicit `width/height`, responsive `srcset/sizes` and tested aspect ratio; no Gutenberg full-post string rewrites.

If the Site QA collector confirms a real failed guest image request, **then**, and only following item rights and visual approval: (1) capture immutable source URL, original WordPress revision and current `currentSrc`; (2) inspect canonical USGS original through an authorized download route, verify file signature/MIME, decoded dimensions, checksum and frame/crop against source; (3) produce max-960px, aspect-ratio-preserving derivative (WebP preferred when supported, with JPEG fallback if necessary), optimized metadata and visible credit; (4) use **staging** first for WordPress media upload/cached first-party delivery, avoiding origin hotlink fragility; (5) QA logged-out mobile/desktop lazy-load, CLS, ALT, captions, 2xx actual bytes and cache-warm/cold transfer; (6) preserve the exact previous block/media reference and reverse staging if the image differs. No production writes without approval.

The proposed **76%** transfer reduction is **not measured**: the 20 known originals above 1.5 MB total **64,385,752 stored bytes**, which is not equivalent to visitor downloads. Site QA's historical **61 posts / 355 inline references** is a frozen baseline, and the reported **42 broken originals** are *not* 42 browser-confirmed failures. Track new 66-post inventories separately.

## Reproducible evidence / enforcement

- [Eight-slot primary source + exact WP URL/status manifest](../qa/media-recovery/hebgen407_usgs_eight_custody_20261116_1830pt.json)
- [Fail-closed offline manifest validator](../qa/media-recovery/validate_hebgen407_usgs_eight.cjs)
- [38-case adversarial test suite](../qa/media-recovery/test_hebgen407_usgs_eight.cjs)

Native Node command (run from repo root):
```bash
node qa/media-recovery/test_hebgen407_usgs_eight.cjs
```

On this run **38/38** tests executed against the exact generated manifest and evaluator under **isolated V8**; native Node and GitHub CI are not claimed. The validator rejects invented guest HTTP statuses, unmeasured bandwidth wins, source drift, false release approvals, misidentified USGS catalogs, 960px distortions, and unverified binary identity. No duplicate Site QA browser collector was created. The requested `docs/IMAGE-WEIGHT-WORKLIST.md` was 404 on the checked main and Site QA branch as of this run.
