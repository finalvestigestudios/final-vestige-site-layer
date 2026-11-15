# Texas City Disaster — six frozen external originals, catalog conflict and 960px HOLD (2026-11-09)

**Scope:** Original six Commons redirect image positions in published historical article 216, [The Fire Department Was Already There](https://finalvestige.com/2026/08/18/the-fire-department-was-already-there/). Confirmed exact stored URL/ALT pair against frozen WP export `qa/media-recovery/parts/06.json`, blob `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`, and site-wide external census `92a904c8da1ace1f972b2f00adf1a4847dde2b99`. Live CMS edit content not re-read this sprint.

**Source-only outcome:** Six exact stored redirect endpoints yielded independent external retrieval service `TOOL_URL_NOT_ACCESSIBLE`; actual origin HTTP, guest-browser HTTP/decode, cache and transfer bytes **UNKNOWN/NULL**, not 404/403 claims. None proved broken. Historical reported 42 failures and claimed 76% cold-guest wire-byte reduction both **unverified**. 15 >1.5 million B WP originals total 47,096,779 stored bytes, not wire bytes. Existing Site QA #154 Chrome/CDP owner retains P0 order 285:5, 285:2, 287:5, 418:1, 418:2, 407:1.

## Historical/rights findings
- **216:0 parking lot / 216:2 five-story building:** Current primary University of Houston Digital Collections catalog credits **Charles Tellus Townsend** and states **Copyright Undetermined**, while Wikimedia Commons asserts public domain. A host-level/Commons label cannot overrule current item-level evidence. Flag the contradiction; **no rehosting without documented rights resolution**.
- **216:4 ship photograph:** Commons identifies **SS Wilson B. Keene**; University of Houston collection-level reuse information is unresolved and does not establish individual frame rights. Do not conflate with **SS High Flyer**. Creator of this exact frame not independently confirmed.
- **216:1 firefighters' memorial:** Modern 2008 **Jim Evans** photo **CC BY-SA 4.0**; derivative requires correct credit/license/change indication/share-alike. It is not a federal archival photo.
- **216:3 NARA 68149862:** Official NARA Army Air Forces title `Texas - Texas City`; broad series coverage `1917–1964` does **not prove photo 1947 date** or document the explosion. No silent historical relabel.
- **216:5 anchor monument:** David Provines modern 2006 Commons `PD-self` claim; width only **480 px**, so preserve **480×320** (do not upscale to 960).

## Measured versus conditional
Catalog master dimensions (not decoded from the live original binary), and resulting **conditional** max-960px dimensions:
- 216:0 3111×2421 → 960×747
- 216:1 1917×1544 → 960×773
- 216:2 2765×2112 → 960×733
- 216:3 6923×5485 → 960×761
- 216:4 2768×2120 → 960×735
- 216:5 480×320 → 480×320

These are not actual rendered visitor sizes, downloaded binaries, byte checksums or rehost-approved assets. Maps/pictures must retain important labels/contents and accurate chronology.

## Safe remediation plan (all release flags FALSE)
1. **Site QA**: actual logged-out cold-browser status and intrinsic image decode with P0 ahead of 216. Inspect browser-resolved final `currentSrc`, full-scroll lazy loads and cache flags; do not infer failures from this external retriever.
2. **Media recovery**: for proved failures, verify original exact photo/scan/crop, catalog accession, creator rights/license and attribution; if any conflict persists, HOLD.
3. **Authorized staging only**: download known licensed binary after explicit clearance; record origin URL, acquisition time, SHA-256, exact native dimensions and full-resolution visual comparison. Create 960px maximum width **without enlarging** or trimming information. Preserve full-resolution viewing for detailed scans.
4. **WordPress**: propose media library asset with credit/license metadata and reversal plan; require separate explicit approval for any upload or post-block src replacement; avoid bulk Gutenberg block rewrites.
5. **Performance measurement**: quantify true visitor image `encodedDataLength` per uncached CDP response for the **same historical scene/source identity** with matched baseline/staging, full load/lazy scroll, LCP and CLS. Different photographs are not compression. No fabricated "76%" savings.

**Primary source trails:** University of Houston https://digitalcollections.lib.uh.edu/collections/0p0967712?locale=en&view=gallery ; NARA https://catalog.archives.gov/id/68149862 ; item-specific Commons catalog URLs in JSON. This memo is evidence-only: no download, cache, WP writes, homepage edits or subscription spend.
