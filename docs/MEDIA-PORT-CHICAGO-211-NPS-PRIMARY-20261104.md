# Media Recovery — Port Chicago post 211: six NPS primary sources (2026-11-04)

**Scope:** provenance, visual integrity and recovery candidate geometry for one single-host 6/6 external image article; isolated from homepage design and Site QA PR #154. This memo approves **no** image mirroring, third-party downloads, file modification, caching, WordPress updates, or publication.

## Fresh verified state

- Authenticated, **read-only** WordPress `posts_get(context=edit, id=211)` on Nov 4 returned published post **The Men Who Wouldn’t Turn Left** (last modified **2026-11-02T21:39:32** UTC). Its six image URLs and six ALT descriptions are exact matches to October 30 pinned `qa/media-recovery/parts/06.json` blob `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`.
- **Five of six** `img` elements declare width/height. **211:4** (the mutiny trial courtroom) declares **neither**. This is a *possible* layout-shift risk, **not** measured visitor CLS. Width+height for the other five are HTML declarations, not intrinsic dimensions.
- All six use `www.nps.gov` original source paths. Exact original URLs and ALTs are in the [machine-readable ledger](../qa/media-recovery/port_chicago_211_nps_primary_20261104.json).

## Primary-source identity and conditional 960px staging geometry

| Slot | NPS archival reference | Official source | Conditional derivative from HTML aspect ratio only | Independent image viewer |
| --- | --- | --- | ---: | --- |
| 211:0 | POCH 2.078, sailors loading ship | [NPS original vs colorized](https://www.nps.gov/poch/learn/photosmultimedia/colorized-photographs.htm) | 960 × 749 | NPS page's WebP-parameter image link error |
| 211:1 | POCH 2.115, sailors loading rail car | same NPS page | 960 × 765 | NPS page's WebP-parameter image link error |
| 211:2 | POCH 2-113, wreckage and cars | same NPS page | 960 × 809 | NPS WebP-parameter variant displayed |
| 211:3 | POCH 2-056, destroyed rail tracks | same NPS page | 960 × 776 | NPS WebP-parameter variant displayed |
| 211:4 | Navy / National Archives, 1944 courtroom | [NPS mutiny trial](https://www.nps.gov/poch/learn/historyculture/the-mutiny-trial.htm) | **unknown** | NPS bare JPEG URL displayed |
| 211:5 | POCH 2-055, destroyed pier | NPS original vs colorized | 960 × 767 | NPS WebP-parameter variant displayed |

**Important measurement separation:** the NPS comparison page requests `format=webp` for five variants, whereas the published Final Vestige source URL does not. A retriever's success/error on that **different query** is neither an origin HTTP response for the published URL nor a logged-out visitor's `currentSrc`. No numeric HTTP statuses, decoded intrinsic sizes, browser transfer bytes or user-visible failures were obtained. There is **no evidence here of six browser-broken images** or of a percentage improvement. Viewer failures do **not** establish 403/404/500.

**Visual custody caveat:** the NPS comparisons include **colorized derivatives** separately from original black-and-white photographs. Never substitute the colorized derivative for the historic original by URL similarity. Slot 211:3's black-and-white original visibly contains a contemporaneous Mare Island marking about release for publication and a later declassification notation. This historic label must be interpreted with the image's present-day rights record; it neither proves current restriction nor grants reuse permission.

## Rights and caching decision: HOLD

Official [NPS photo gallery](https://www.nps.gov/poch/learn/photosmultimedia/photogallery.htm) says the collection mixes public-domain and rights-limited photographs; source origin on an NPS domain is **not** an individual-item license. [NPS Archives copyright guidance](https://www.nps.gov/articles/000/copyright-restrictions.htm) cautions that possession of an archive reproduction is not permission to republish. Slot 211:4 is expressly credited **U.S. Navy / National Archives** by NPS; confirm the underlying work's photographer, status and attribution. All six remain `item_public_domain_proven=false`, `wp_upload_authorized=false`, `cache_authorized=false`, and `post_rewrite_authorized=false`.

Staging plan **only after Site QA proves an exact visitor failure**:
1. Capture screenshot + browser `src/currentSrc`, all redirect hops and final GET status/MIME, `decode()`/`naturalWidth,naturalHeight`, CDP cold-wire `encodedDataLength`, and CLS on both suspected asset and a valid control image. **Site QA #154** owns this; do not fork its scanner.
2. Confirm photo subject, crop, grayscale vs colorized treatment, NPS item number, rights/credit; prefer same photo over plausible different scene. Obtain written license if not demonstrably public domain.
3. Decode intrinsic master pixel dimensions and aspect ratio, then derive at width **min(960, intrinsic width)** with proportional height; never upscale; consider modern formats only if encoding supports visual fidelity; report encoded bytes by browser URL, not Media Library storage. Do not equate NPS `format=webp` variant with final visitor response.
4. In **non-public staging only**, create a cached derivative in approved WordPress media with catalog credit/attribution, inspect desktop+mobile 211:0–5 before/after, preserve Gutenberg blocks and ALT, and prepare exact rollback URL. A separate explicit production authorization is required for any publication. No staged binary was created this run.

## Other standing work, not overridden

P0 remains 285:5/285:2, 287:5, 418:1–2 and 407:1. The post 211 six-image same-host dependency is P1 *after* browser-proof first. The frozen sitewide census remains **61 posts / 355 stored image refs / 288 external origins / 13 WP originals >1.5 MiB**. The old **42 broken** count is unverified as visitor-facing, and claimed **76% savings** unmeasured by actual cold browser wire. The five 1672×941 first-party PNGs on posts 34–38 remain a separate size-target batch (not a measured visitor-transfer reduction).

## Executable checks

[Validator](../qa/media-recovery/validate_port_chicago_211_20261104.cjs) checks every exact `src`/ALT against the pinned frozen part, 6 image identities, authoritative NPS catalog mapping, HTML-derived dimensions, unverified HTTP fields, rights, and release holds. [Regression tests](../qa/media-recovery/test_port_chicago_211_20261104.cjs) reject 34 adversarial changes, including invented 200/404, fabricated bytes and WordPress authorization. **39/39 assertions passed in isolated V8 against exact committed GitHub blobs**, including 34/34 mutation rejections. Native Node CI and logged-out Chromium **not run**. No external image files downloaded or CMS writes made.
