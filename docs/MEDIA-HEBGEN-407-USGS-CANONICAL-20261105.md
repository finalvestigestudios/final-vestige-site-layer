# Hebgen Lake 407 — Primary USGS image provenance, 2026-11-05

**Read-only live WordPress verification: all eight original <img src> URLs match the pinned October 30 corpus, and all eight USGS item-page Original links point to those exact URL paths.** This is strong original-source identity evidence, not visitor-browser HTTP confirmation.

| Image | Official archival catalog | Photographer/credit | Independent source viewer |
|---|---|---|---|
| 407:0 | [USGS original](https://www.usgs.gov/media/images/earthquake-damage-1959-hebgen-lake-event-yellowstone-plateau) | J. B. Hadley, USGS Fact Sheet 2005-3024, 1959 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |
| 407:1 | [USGS original](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) | J. R. Stacy, USGS, 1959 | UNSUPPORTED_BINARY_OCTET_STREAM_WRAPPER |
| 407:2 | [USGS original](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake) | Professor William B. Hall, Montana School of Mines, 1959-08-21 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |
| 407:3 | [USGS original](https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959) | Mrs. Steven W. Nile, Montana School of Mines association, 1959-10-18 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |
| 407:4 | [USGS original](https://www.usgs.gov/media/images/rockslide-damage-golden-gate-area-near-mammoth-hot-springs) | Photographer not identified on USGS item, 1959 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |
| 407:5 | [USGS original](https://www.usgs.gov/media/images/sapphire-pool-upper-geyser-basin-erupting-after-1959-hebg) | Photographer not identified on USGS item, 1959 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |
| 407:6 | [USGS original](https://www.usgs.gov/media/images/seismic-geyser-eruption-1970) | John Brandow, USGS, 1970 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |
| 407:7 | [USGS original](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) | Mike Poland, USGS, 2023-06-27 | SOURCE_IMAGE_RENDERED_IN_RETRIEVER |

## P0 fault scarp 407:1
The live article links to the official USGS record at `/hebgen-lake-fault-scarp-1959-0`; the USGS Original download link points to the same `img7535.jpg` S3 URL as the live WordPress `src`. The text/image retriever reported **wrapper 400 unsupported binary/octet-stream**, NOT observed image HTTP 400/Chrome failure. Retain `visitor_broken=null` until Site QA #154 runs logged-out full-scroll browser, checks image `currentSrc`, `naturalWidth`, CDP request ID, and actual network response.

## Rights and historical fidelity
All eight official USGS item pages individually state **Sources/Usage: Public Domain** (not simply inferred from agency ownership). [USGS copyright policy](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits) cautions that some non-USGS photos on its pages can retain third-party copyrights. **407:2** credits William B. Hall, Montana School of Mines; **407:3** credits Mrs. Steven W. Nile. Their individual item pages say Public Domain, but preserve creator attribution and review the exact binary prior to any mirror. **407:7 is a 2023 photograph** by Mike Poland: never retitle as 1959 eyewitness imagery.

## Conditional media optimization staging
Never upscale. Width cap 960px **only after confirming source intrinsic dimensions**; use `min(960, verified_original_width)` and preserve aspect. Only 407:2/3/7 have stored HTML width/height (1024×719, 1024×730, 1024×771). If binary inspection verifies those ratios and width>=960, *conditional* output geometry is 960×674, 960×684, 960×723. The other five have no declared geometry. Actual files were not downloaded or decoded by this workflow and no proposed binary dimensions were fabricated. For any later approved rights-cleared media migration: retain original URLs, full ALT/captions/credits, record old post content/media IDs and rollback, stage one image at a time, and require guest-browser visual parity plus measured wire bytes before publication. No rights-based upload, cache, or production post write is authorized.

## Verification
Machine [8-row audit](../qa/media-recovery/hebgen_407_usgs_eight_original_links_20261105.json), [offline fail-closed validator](../qa/media-recovery/validate_hebgen_407_usgs_eight_20261105.cjs), and [native Node-ready source tests](../qa/media-recovery/test_hebgen_407_usgs_eight_20261105.cjs). Isolated V8 exact-script validator: baseline + 32 mutations PASS; full native Node/CI and actual browser tests pending. This batch does **not** replace Site QA #154's browser collector or other drafts.

Baseline unaffected: 61 posts, 355 images, 288 external-source refs; 13 WordPress originals >1.5 MiB occupy 43,522,829 **stored** bytes, not visitor transfers. 42 claimed broken remain unverified, 76% transfer improvement unmeasured, **0 production image repairs**. No WordPress writes, third-party binary caching, media downloads or subscriptions.
