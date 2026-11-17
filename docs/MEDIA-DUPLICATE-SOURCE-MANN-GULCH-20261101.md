# Media recovery: exact-source duplicates and Mann Gulch primary-source custody — November 1, 2026

## Scope and verified method

This is an **isolated, read-only media-integrity batch** on draft PR #183. It is not the Site QA PR #154 classifier, a guest browser audit, or a homepage design change.

The immutable source census consists of eight JSON parts, **61 published posts and 355 stored image-reference slots**. Parsing each complete *exact source URL* (including case, path and query) yields **353 distinct URLs**. The split is **288 offsite reference slots corresponding to 286 unique exact URLs**, plus **67 first-party and Jetpack slots corresponding to 67 unique URLs**. Only two same-post source URLs repeat: **213:2 = 213:6** and **291:2 = 291:5**. Four visible slots rely on two distinct source files.

This is not evidence that only 286 offsite images are present or that any are broken. The older Site QA 286-offsite-source number is numerically equal to our distinct URL count, but prior post-291/post-285 proxy classification and snapshot differences are independently documented; **do not infer the prior classifier counted unique URLs**. A broken source may create two broken visual *slots*, while a browser may fetch the underlying URL once or more depending on cache and redirect behavior.

WordPress read-only post checks on November 1 confirmed both repeated URLs remain in the published Gutenberg source: post **213** modified **2026-10-29 20:59:21**, with **7/7 exact stored URLs and full ALT strings** unchanged; post **291** modified **2026-08-28 15:14:59**, with both duplicated URL/ALT pairs unchanged. This is authenticated CMS editor-content inspection, not a logged-out visitor page load.

## P0: substantive visual-integrity concern, Teton Dam (291:2 and 291:5)

The exact same Deseret News CloudFront photograph is used once under **“Growing breach in Teton Dam during the final hour before collapse”** (slot 291:2) and once under **“Aftermath of the Teton Dam failure and downstream cleanup in Idaho”** (slot 291:5). Earlier media source work identified the underlying photo as post-collapse cleanup, so the first claim has an **editorial identity mismatch requiring a corrective source/photo review**. Its historical effect is material: it depicts a different phase of the disaster than the text promises.

The prior Teton memo records a [National Archives NAID 28894684](https://catalog.archives.gov/id/28894684) **candidate alternative**. It is NOT established as the same original photograph, and it cannot be silently inserted under the current text. Required: read-only comparison of the exact picture/crop with the authoritative archival catalog, individually verify the candidate's rights and credit, author an editorially correct ALT/caption, and secure release approval. **No Gutenberg change, new media item or image download occurred.**

## P2: identical map used twice intentionally or redundantly, Mann Gulch (213:2 and 213:6)

The two original source URLs (including the S3 VersionId query) are byte-for-byte identical. Both are NWCG staff-ride maps derived from the historical Rothermel account. The first accompanies the crew's last movements; the second accompanies a discussion of Dodge's escape fire. Their different ALT descriptions are **potentially complementary**, not necessarily conflicting, and should not be automatically merged or treated as two distinct downloaded images. Check the visitor experience and historical context; preserving both placements may be intentional. [NWCG staff ride](https://www.nwcg.gov/page/staff-ride-to-the-mann-gulch-fire); [USFS Mann Gulch history](https://research.fs.usda.gov/firelab/projects/manngulch).

### Seven-slot source/rights/960px custody

Every original URL, exact ALT text, source host, status held/unknown, 960px proposal and prohibited CMS actions is recorded in [mann_gulch_213_primary_20261101.json](../qa/media-recovery/mann_gulch_213_primary_20261101.json). Source page links below **do not establish a matching original-file SHA-256**.

| Slot | Source/archival evidence | Safe width target | Rights and identity gate |
| --- | --- | --- | --- |
| 213:0 | Official USDA Forest Service annotated north-face image; [USFS photo context](https://research.fs.usda.gov/firelab/products/multimedia/photos/mann-gulch-fire-tragedy-photo-series) | Stored 1024×622 → **960×583**, conditional | Item-specific photographer/source and master identity HOLD |
| 213:1 | NWCG 2023 staff-ride S3 *fire-progression-map* image | Unknown until source decoded; **≤960px**, no upscale | Government host does not by itself prove all rights |
| 213:2 | NWCG staff-ride *historical-map-race-pg5* image, same exact URL as 213:6 | Unknown until source decoded; **≤960px** | Richard C. Rothermel/USFS historical diagram attribution needs individual review |
| 213:3 | [Exact Commons file page](https://commons.wikimedia.org/wiki/File:Mann_Gulch_Fire,_1949._US_Forest_Service,_retrieval_of_victim%27s_bodies.jpg), USDA Forest Service photographer **Dick Wilson**, **August 6, 1949** | Catalog original 1457×972 → **960×640**, conditional | Commons asserts public domain; verify catalog crop, original bytes and credit before mirroring |
| 213:4 | USDA Fire Lab hosted historical combustion-chamber image | Unknown until source decoded; **≤960px** | Individual attribution/photo release HOLD |
| 213:5 | USDA-hosted wind tunnel image has filename **firelabwindtunnel-courtesy-newyorktimes.jpg** | Unknown until source decoded; **≤960px** | **High-risk third-party-rights hold**: a New York Times courtesy credit cannot be treated as federal public domain |
| 213:6 | Exact repeated NWCG staff-ride historical-map-race-pg5 file from 213:2 | Same original dimensions, currently unknown | Same image, same rights and credit status; no second asset needed |

USFS supports the historical context of the research laboratory and why it followed the 1949 Mann Gulch fire. Its location does **not** convert an externally credited New York Times photograph into a U.S.-government public-domain work. [USFS Fire Lab history](https://research.fs.usda.gov/firelab/about); [NWCG historical photo gallery](https://www.nwcg.gov/wfldp/toolbox/staff-ride/library/mann-gulch-fire/collection-of-historical-photographs-mann-gulch-fire). The 1457×972 Commons metadata documents a crop/rotation history, so any eventual master must be visually matched to the displayed original, not inferred from the title alone.

## Failure evidence and weight methodology — explicit unknowns

**No logged-out visitor HTTP status or transferred image bytes** were recorded this sprint. Direct execution-container DNS resolution fails for both finalvestige.com and unrelated archival control domains, which is an environmental limitation, not proof of visitor 404s. The search image viewer displayed the shared NWCG staff-ride image, but did not record a Final Vestige guest-browser response.

**The reported 42 broken images and claimed 76% image-weight reduction remain unverified.** When Site QA obtains guest browser data, preserve (a) failed visual slots, (b) distinct failed *image assets*, and (c) image **network requests** as separate counters. Match decoded currentSrc, final redirect URL, HTTP status and MIME, natural dimensions and encoded wire bytes to the specific slot; avoid counting the same cached response twice in a per-page transfer sum. For savings compare the same fully loaded page, device, viewport, cache policy and network conditions before and after a separately approved intervention; aggregate actual encoded transfer bytes, not the Media Library's original-storage sizes. The **13 originals >1.5 MiB** remain source/storage measurements only.

## Safe WordPress-caching plan (proposal, not release)

For each actual broken and source-rights-approved photo: verify exact record/source/crop and rights; obtain the original file via a lawful permitted path; record master SHA-256 and publisher credit; locally stage a dimension-preserving derivative **min(960px, original width)** with no cropping/upscale, then visually QA content and ALT; only with separate approval create a WordPress media item, confirm responsive output, and update the single intended figure without altering surrounding historical content or permalink. No bulk scraping, hotlink bypass, blanket government-work license assumption or production update.

## Engineering evidence and execution

- Frozen [site-wide distinct-source ledger](../qa/media-recovery/duplicate_exact_urls_20261101.json) (all exact repeated URLs and source slot/ALT pairs).
- [Mann Gulch seven-photo primary-source ledger](../qa/media-recovery/mann_gulch_213_primary_20261101.json) (7/7 CMS-verified source and ALT).
- [Fail-closed validator](../qa/media-recovery/validate_duplicate_source_20261101.cjs) and [30 native Node tests](../qa/media-recovery/test_duplicate_source_20261101.cjs). Execute from repo root: node --test qa/media-recovery/test_duplicate_source_20261101.cjs; then node qa/media-recovery/validate_duplicate_source_20261101.cjs.
- **30/30 native Node tests passed** on locally tested source, with the committed validator and test file independently matching the locally tested Git blob SHA-1 values. Exact committed-source isolated V8 readback also validated the real **61/355/353/288/286/67** census and both duplicate groups, with a minimal test-only URL shim (not a native browser).
- No WordPress writes, image binaries/downloads, new licensed asset copies, homepage design changes, Site QA PR #154 classifier changes, or subscription spend.

## Focused Site QA handoff

Do **not** create a parallel duplicate-source classifier or rewrite Site QA's independent draft. In its existing logged-out browser evidence collection, capture both placements **291:2 / 291:5** with image identity and captions, then **213:2 / 213:6** with currentSrc, final response, visual screenshots and encoded wire bytes. The P0 missing-image checks for Okeechobee and Hebgen remain independently higher priority. These observations determine whether a visitor-facing failure exists, while the Teton ALT mismatch warrants a separate editorial fix even if the photo loads.
