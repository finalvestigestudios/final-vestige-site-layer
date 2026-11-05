# Media Recovery: last two P0 source wrappers and visual-integrity gate

**Pacific audit date:** 2026-11-04, after 21:30 PST. **Scope:** Media Recovery PR #183 only, with Site QA #154 as the independent guest-browser owner. No WordPress, homepage, media binary, licensing, deployment or subscription mutation.

## Evidence matrix — exact live-published links

| Slot | Exact external source in published WordPress | Independent retrieval observation | Confirmed origin HTTP | Logged-out Chrome HTTP / decoded pixels |
|---|---|---|---|---|
| 285:5 Three Mile Island | `https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg` | Retriever wrapper **404** | **UNKNOWN** | **UNKNOWN** |
| 418:1 Scotch Cap | `https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG` | Retriever wrapper **403** | **UNKNOWN** | **UNKNOWN** |

These complete independent *retriever-wrapper* checks of the two P0 links that the earlier four-source Nov 4 ledger had not checked. Results are **not visitor-browser failures**, and an external tool's HTTP-looking failure code must **never** be copied into a visitor/origin HTTP status field. Read-only WordPress post 285 (modified Nov 2, published) confirms an ALT describing an aerial view of Three Mile Island; post 418 (modified Aug 28, published) identifies Anthony L. Petit in both ALT and caption. Original live source URLs remain unchanged. The 42 reported broken images have **not** been validated in logged-out Chrome.

**USCG authoritative item:** [official USCG image catalog 2002905913](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) associates VIRIN `210330-G-DE713-0002.JPG` with the historical portrait of the Scotch Cap station chief (NOT damage/debris). The catalog explicitly labels this particular photo public domain and cleared for release, but requires suitable credit and compliance with DoD/official-marks/endorsement limitations. This is a much stronger item-specific rights lead than guessing federal images are universally free. Exact binary/master hash and actual pixel geometry remain unknown. The rendition URL's `/1920/1080/` path must not be treated as verified master dimensions.

**Three Mile Island alternative:** [Commons file Three mile island 062010.jpg](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) lists an original 819×614 and an uploader's public-domain dedication. That is a June 2010 plant photograph; its framing and identity have **not** been shown to match the currently published aerial-view ALT or original Say Media photo. **No automatic drop-in swap.** Any derivative from this specific 819px catalog original is capped at **819×614**, not enlarged to 960. Rights metadata itself does not establish historical/scene equivalence.

## Measurable engineering change: protect visual integrity before claiming image-wire savings

The [guest browser classifier](../qa/media-recovery/browser_probe_core.cjs) now retains **`natural_height`** from the browser's decoded image, alongside its pre-existing `natural_width`.

The [paired cold-wire comparator](../qa/media-recovery/compare_cold_image_wire_v1.cjs) now refuses an otherwise plausible byte-reduction claim if:
- either capture lacks positive intrinsic width **or height**;
- the historical image's rendered ALT changes between baseline and candidate;
- the aspect ratio changes by more than 1% (cropped scene or altered diagram possible);
- the candidate is intrinsically larger in either axis (upscale requires review);
- the candidate substitutes a tiny asset (below the smaller of 320px and baseline width, or 160px and baseline height);
- any individual CDP caching-proof boolean is absent instead of explicitly false.

These checks reject known unsafe shortcuts such as a 1×1 placeholder masquerading as a 76% performance win. They deliberately **do not** certify photographic identity, correct historical scene, pixel-level similarity, accessibility or reuse rights. Output always sets `visual_parity_verified:false`, and can only describe one controlled cold-browser pair. Proper visual screenshots, source record, license/credit, article captions and reversible staging remain separate approval gates.

### Exact repository engineering commits
- `6f8cc37b761f744d77c2628baf38cd8df7676c8e` — browser intrinsic height recorded.
- `9a072da373b44ca05c038da09e4a0f5906b3ed2f` — browser core regression added.
- `f9ea173a62514ef42e1fc3263c92a6d8bacd4eee` — comparator geometry/ALT/cache guards.
- `c6c973ce7c10c72ae19cd4edd2be6b71aece8dc2` — comparator regressions, including tiny-image, cropped-photo and missing-cache-field negative tests.
- `b4e4f753c360141aa9d3d29582b395e917d4177f` — [two-source machine ledger](../qa/media-recovery/p0_remaining_two_source_wrapper_20261105.json).

**Testing:** Exact committed modules and tests replayed in isolated V8 compatibility environments: **30/30 paired-comparator tests (114 assertions)** plus **13/13 browser-core tests (27 assertions)**, both without failures. Ledger passed **15/15 deterministic checks** on exact original stored URLs, segregated tool-wrapper versus real HTTP fields, cache HOLD and no-upscale. The V8 test harness uses a URL/URLSearchParams compatibility shim and is **not native Node or actual Chromium**. Native repository CI and actual logged-out Chrome are still outstanding; none of these checks establishes a production repair.

## Performance baseline and staging

Frozen posts **61**, image slots **355**, origin-external **288**, 13 WordPress originals strictly >1.5 MiB with **43,522,829 stored bytes**. Five first-party PNGs in posts 34–38 represent **13,267,538 stored bytes**, with proposed owned/rights-reviewed 960×540 derivatives. Stored original bytes are not visitor transfer bytes. **Reported 76% image-wire reduction remains UNMEASURED.** No production image fixes by this workstream.

**Safe next steps for Site QA:** logged-out desktop and mobile Chromium on slots 285:5 and 418:1 plus the unchanged existing higher-priority set 285:2, 287:5, 418:2 and 407:1. Record `currentSrc`, decoded natural dimensions, exact CDP response/redirects/bytes and screenshots, not wrapper errors. For any true failure, reconcile the scene and caption with primary catalog, verify rights, lawfully acquire and hash asset, and stage <=960px (without enlargement) in a controlled offline location. No WordPress uploads, post rewrites, or unlicensed caching until separate release approval.

**No work is duplicated in Site QA #154; no existing site design or production file was touched.**
