# Media Recovery — St. Francis Dam post 166 — November 3, 2026

**Status:** isolated source/rights audit only. **Production image fixes: zero.** Branch PR [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183), independent of [Site QA #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) and homepage visual design.

## Source integrity (fresh WordPress read)
Read-only authenticated WordPress post ID **166**, *They Checked the Dam That Morning*, is **published**, modified `2026-11-02T21:39:29`. All **7/7 exact `<img src>` URLs** match the pinned October 30 `qa/media-recovery/parts/07.json` Git blob **`21095161e633aba093b74c0ead9936c9f6186d00`**. Stored source kinds: **five Wikimedia Commons Special:Redirect/file?width=1280**, **one direct Library of Congress GIF**, **one existing first-party JPEG**.

All seven exact direct URLs were inaccessible through the independent text retriever (`web.open` internal tool errors, **no numeric origin response**). **This says nothing conclusive about logged-out browser rendering.** Current `currentSrc`, final HTTP status, MIME, `naturalWidth`, `decode()`, screenshot and uncached CDP `encodedDataLength` are all **unknown/null**. The CMS content is independently reverified; the public HTML and image network were not retrieved as a guest.

## Item-level catalog and staging table

| Slot | Custodial catalog / rights signal | Catalog master pixels | Conditional ≤960px derivative | Gate |
|---|---|---:|---:|---|
| 166:0 | Existing WP JPEG `IMG_3479.jpeg`; rights/metadata not independently re-verified | unknown | unknown | No change |
| 166:1 | LoC HAER **CA3095** Los Angeles Aqueduct survey parent; **exact 00002a.gif sheet NOT catalog-confirmed**; Gov-item copyright exception possible | unknown | unknown | HOLD source sheet, rights, MIME and bytes |
| 166:2 | [H. T. Stearns, USGS, 17 Mar 1928](https://commons.wikimedia.org/wiki/File:St._Francis_abutment.jpg); Commons public-domain federal-work rationale | 1400×806 | **960×553** | HOLD rights/item and crop check |
| 166:3 | [USGS Flickr-origin *Twisted Tracks*](https://commons.wikimedia.org/wiki/File:Twisted_Tracks.jpg); Commons **CC BY 2.0** | 1400×1017 | **960×697** | HOLD exact attribution, license, crop check |
| 166:4 | [Stearns / USGS post-collapse view](https://commons.wikimedia.org/wiki/File:St._Francis_Dam_after_the_1928_failure.jpg); Commons public-domain federal-work rationale | 1400×1043 | **960×715** | HOLD rights/item and crop check |
| 166:5 | [*Standing section*, L.A. Public Library](https://commons.wikimedia.org/wiki/File:Standing_section.jpg); Commons public-domain **unrenewed** rationale references **1931–1963**, but photo is catalogued **1928**. Primary [LAPL TESSA](https://tessa.lapl.org/cdm/search/searchterm/00009829) redirected/inaccessible to independent retriever. | 1250×936 | **960×719** | **HOLD: rights rationale mismatch; primary item needed** |
| 166:6 | [Los Angeles Daily News / UCLA](https://commons.wikimedia.org/wiki/File:Man_pointing_at_crack_in_Saint_Francis_Dam_after_its_collapse.jpg); Commons **CC BY 4.0** refers to bulk UCLA collection and requires per-item verification at [UCLA record](https://digital.library.ucla.edu/catalog/ark:/21198/zz00253zg8) (retriever access denied) | 4431×5760 | **960×1248** | HOLD item rights, credit, crop, editorial accuracy |

**Visual/chronological integrity:** The St. Francis debris/abutment and damaged tracks are photographs **after** the March 1928 failure; the first-party source is captioned as pre-failure February 1927. Preserve distinctions. Commons' 166:6 description contains an **unverified casualty figure** that must not be imported into Final Vestige metadata. Distinct photograph, crop, context, and caption identity are prerequisites for replacement.

**Library of Congress nuance:** [The LoC HAER collection rights advice](https://www.loc.gov/rr/print/res/114_habs.html) explicitly warns government-survey compilations can contain copyrighted material copied from elsewhere. Matching `ca3095` URL structure to the LA Aqueduct parent record is not a verified match of sheet `00002a`; no per-item copyright declaration is inferred from catalog custody. Its `.gif` extension must not be treated as a measured download burden.

## No-risk WordPress recovery protocol (NOT executed)
1. Site QA #154 captures logged-out desktop **and mobile**: view every image after scroll/lazy-load, collect literal `src`, live `currentSrc`, request/redirect chain and final HTTP/MIME, `naturalWidth/Height`, `decode()` and before screenshot. Cold-cache CDP `encodedDataLength` should be mapped per source. Apply existing Site QA P0 queue first.
2. For any actually broken slot, preserve original WP source/ALT/caption/post revision. Verify exact archive item, reproduction rights (including item-specific grants and CC attribution), intrinsic dimensions, and visual similarity; do **not** replace an engineering plan with a disaster photograph or vice versa.
3. If cleared **later**, make a standalone derivative at **at most 960px width** preserving aspect ratio, no enlargement. Encode WebP/AVIF as supported with JPEG fallback where warranted, record hash, attribution, credits, alt and provenance; use a staging WordPress Media Library asset and validate sizes with a cache-cold browser. Preserve immutable original/candidate mapping and reversible post edit instructions.
4. Publication/rehosting remains **HOLD**; user explicitly prohibited WordPress production writes. Production changes require an independently authorized release workflow.

## Measurement safeguards
Previous inventory: **61 published posts, 355 stored inline image refs (288 offsite sources under PR #183 classification, vs QA #154's 286), and 13 WP original assets >1.5 MiB**. Those are source or storage counts, **not wire load**. A claim of **76% image-weight reduction** requires matched 61-page, 355-slot, cold-session before/after captures, three complete paired runs per article, same environment and successful decoding; then sum per-image `encodedDataLength` rather than comparing WordPress originals or master dimensions. The reported **42 broken** remains **guest-browser unverified**. **Real production fixes: zero**.

## Machine evidence and verification
- [Seven-slot JSON with exact published URLs and null guest HTTP evidence](../qa/media-recovery/st_francis_166_catalog_20261103.json)
- [Fail-closed source/rights validator](../qa/media-recovery/validate_st_francis_166_20261103.cjs)
- [25 mutation regression checks](../qa/media-recovery/test_st_francis_166_20261103.cjs)
- **25/25 PASS** against the **exact committed GitHub file contents** in isolated V8 with assert shim. Native Node CI / real Chrome browser remain pending. No binaries downloaded, copied, cached or republished; no WP writes, design edits or subscription charges.
