# Final Vestige image recovery: Lituya Bay #277 — six exact external originals (2026-11-10)

**DRAFT / READ-ONLY / DO NOT MERGE OR DEPLOY.** This is image-source integrity and performance research only, separate from homepage visual design. Site QA draft [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns the existing browser/CDP collector and six P0 image checks. No WordPress writes, media binaries/downloads, caching, publisher scraping, costly APIs, homepage changes or production deployment.

## Material findings: original figure and 2020 satellite mislabeled

A November 10 **authenticated read-only** `posts_get(context=edit)` returned published post **277**, [*The Boat Went Over the Trees*](https://finalvestige.com/2026/08/19/the-boat-went-over-the-trees-lituya-bay/), last modified `2026-08-21T00:32:52`. **Six out of six** literal current `<img src>` URLs **and ALT descriptions** exactly match the frozen October 30 source inventory.

- **277:0 — P1 editorial mismatch:** the exact published image visibly is a **two-panel annotated scientific composite** (wave geometry and run-up model over an aerial overview). Its ALT says merely "Aerial view ... showing ... shoreline and runup scar." Annotation copyright is unverified. A stand-alone Don J. Miller USGS photo is **not a like-for-like replacement** for the diagram. Propose, for editorial review only: "Two-panel diagram of the 1958 Lituya Bay wave, combining annotated run-up geometry above an aerial view of the bay below."
- **277:1 — research figure:** the ResearchGate original endpoint was inaccessible to the web retriever. The catalog calls it *Fig. 10* of a 2013 Robinson/Davies paper, comprising **three photographic panels** credited to USGS. The 2013 figure/arrangement may be copyrighted despite the underlying government photographs. Treat it as a compound research figure, not a generic archive JPG. Do not copy the ResearchGate derivative.
- **277:2 — commercial S3 original:** preview depicts the steep cliff slide scar, but exact match to the separately catalogued 1958 USGS rockslide frame is **unproven**. Replacement candidate [USGS Don J. Miller photograph](https://commons.wikimedia.org/wiki/File:Lituya_Bay_rockslide_1.jpg), **750 × 586**, is **scene-level alternative only**.
- **277:3 — commercial merchandise thumbnail:** the original URL points at an `imagerenderer.com` **greeting-card product preview**. The storefront separately attributes the scene to D. J. Miller / USGS but sells a syndicated photo through Science Photo Library. Do not mirror the merchant preview; instead obtain the *independently identified* original USGS image and check its exact frame/rights.
- **277:4 — annotated aerial with bold arrows:** exact Medium derivative was displayed; the red and yellow overlaid arrows point to the landslide source and maximum wave run-up, but its ALT omits this important graphical context. Closely related [Commons annotated graphic](https://commons.wikimedia.org/wiki/File:Lituya-Bay-overview-with-arrows.png), **750 × 580**, is **not established as identical binary** to the Medium derivative. Editorial ALT proposal: "Annotated aerial photograph of Lituya Bay after the 1958 tsunami, with red and yellow arrows marking the landslide and maximum run-up area."
- **277:5 — verified original dimensions / provenance:** exact original is NASA Earth Observatory's **July 1, 2020 false-color Landsat 8** illustration credited to **Lauren Dauphin** using USGS data, and independently catalogued at **720 × 480 px / 489 KB**. Commons asserts U.S. federal public-domain authorship; NASA's primary [November 23, 2020 article](https://science.nasa.gov/earth/earth-observatory/lituya-bays-apocalyptic-wave-147557/) identifies its creation and the regrowth/trimline interpretation. **Do not upscale 720 px to 960 px.** Its current ALT "Modern satellite view ... with forest regrown" omits that it is false-color. Prefer: "NASA 2020 false-color Landsat view of Lituya Bay highlighting the landslide site and lingering forest trimline from the 1958 tsunami."

## Exact-source observations versus browser proof

From independent web tool opening of the six literal published URLs:
- **Displayed previews:** 277:0, 277:2, 277:4, 277:5 (**4**).
- **Retriever inaccessible/disabled:** 277:1 (ResearchGate), 277:3 (merchant image renderer) (**2**).
- **ACTUAL origin HTTP status:** unknown for all six.
- **Guest-browser status/decoded width/transfer bytes:** unknown for all six.
- **Asset rights cleared / binary identity verified / downloaded / cached / WordPress upload / post rewrite:** **none**.

The image tool's ability to display an image is not a proof that the live site's lazy-loading, JavaScript, CSP or guest rendering succeeds. Retriever refusal is not a visitor HTTP 403/404. Native runner's direct external HTTP probes failed DNS resolution on November 10; no origin status was inferred.

## Evidence and engineering

- [Six literal original URLs, live ALTs, rights/retriever/960px candidate audit](../qa/media-recovery/lituya_277_six_usgs_nasa_composite_rights_20261110.json) — Git blob **`66f893e5171ee8a958c2e48f6871a8607249953e`**.
- [Frozen independent six-source WordPress readback fixture](../qa/media-recovery/fixture_lituya_277_live_source_20261110.json) — Git blob **`8d73780c32d4aa6ef10d665503bb5109e64dc1ad`**.
- [Full updated 288-slot recovery ledger](../qa/media-recovery/coverage_252_exact_pr1703_20261110.json) — Git blob **`24e0d408c1e8d3c696a613cf7d9ec5e9b78b677e`**.
- [Offline fail-closed validator](../qa/media-recovery/validate_lituya_277_six_20261110.cjs) — Git blob **`77b57009d9b9b7b087c293d307d495c8d571dae2`**.
- [46 regression checks](../qa/media-recovery/test_lituya_277_six_20261110.cjs) — Git blob **`9de18156d57595a2595a99db41625716c04efb41`**.

**46/46 tests passed** under isolated V8 execution with Node-compatible `fs`, `assert` and test runner shims against the five actual GitHub-committed file bodies. Native Node CI and actual logged-out Chromium remain **unrun**.

The 288-slot cumulative ledger now records **252 uniquely source-researched / 36 unresearched = 87.5% coverage**, **257 source-evidence records** due to older overlaps; only **six** slots 277:0–277:5 changed relative to the 246-slot predecessor, and all **282 unrelated objects** remain JSON-identical. These are **research records**, not six fixed images. Next 6-slot groups pending: 279 and 290.

## Safe WordPress Media Library / caching decision, not executed

1. Let Site QA collect real **logged-out** full-scroll mobile and desktop `src`, `currentSrc`, `complete`, `naturalWidth`, request statuses, redirects, CORS/referrer/CSP errors and Chrome CDP `encodedDataLength` (including service-worker and cache flags). Original P0 order remains `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. Add Lituya 277:1 and 277:3 as **P1** after P0 because text retriever access failed, not because the visitor image is proven broken.
2. **Only after** independent item-level rights clearance and exact scene/frame/crop identification, prepare a candidate image in isolated staging with authoritative source URI, credits, license/link, native pixels, checksums, `min(960, native width)` derivative and proportional height. **NASA 277:5 is capped at 720 × 480**, and any composite diagram must remain legible (offer higher-resolution source if rights allow). Verify replacement visual parity side-by-side; annotate if figure is a reconstruction rather than an original photograph.
3. Plan but **do not perform** WordPress Media Library upload, source-ID/attachment mapping, preview and mobile validation, a reviewed **single-block targeted** change and rollback to original literal URL/ALT. Never rewrite entire Gutenberg post or bulk mirror third-party images.
4. For the **76% reduction claim**, compare real uncached **cold browser network encoded transferred bytes** per image request before/after under identical visibility, DPR, viewport, lazy-load scroll and content version. Calculate `100 × (before_wire_bytes - after_wire_bytes) / before_wire_bytes` for actual network image responses, de-duplicate repeated original `currentSrc` requests, and report decoded dimensions and LCP/CLS separately. Source-file sizes and previews are **not** actual transfer bytes. This **76% reduction remains unmeasured**.
5. Historical worklist baseline: **15** WordPress stored originals exceeding **1,500,000 decimal bytes**, totaling **47,096,779 storage bytes**; eleven referenced inline across eight posts. This is not an actual browser-transfer measurement. `docs/IMAGE-WEIGHT-WORKLIST.md` was **404 on both default branch and the media recovery PR branch** at this run, so its detailed table could not be reread. Do not invent file values or transfer savings.

The older "42 broken original external-source images" are **not confirmed as browser failures**. The **36 unresearched slots** are a distinct research-progress count, not a broken-image count.

**Release outcome:** 0 production fixes, 0 WordPress writes, 0 binaries acquired or cached, 0 homepage edits, 0 merges/deployments, **$0 additional spend**. Continue draft-only archival verification and Site QA coordination.
