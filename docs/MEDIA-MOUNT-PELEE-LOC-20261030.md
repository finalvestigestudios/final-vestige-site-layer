# Mount Pelée / Saint-Pierre — four direct Library of Congress image sources

**Audit date: October 30, 2026.** Draft media-recovery PR #183; independent from Site QA #154. No WordPress or homepage changes.

[Post 413, The Cell Was Built to Hold a Man](https://finalvestige.com/2026/08/20/the-cell-was-built-to-hold-a-man-mount-pelee/) contains six stored inline images. **Four** use exact direct `tile.loc.gov` URLs; **two** are already first-party. Source census is `qa/media-recovery/parts/02.json` (source snapshot modified 2026-10-29), not a browser capture.

| Stored slot | Original LOC reproduction | Catalog | Evidence and caution |
|---|---|---|---|
| **413:1** | **LC-DIG-stereo-1s41590** | [98504788](https://www.loc.gov/item/98504788/) | Underwood & Underwood stereograph, published **c1903**, representing a **pre-eruption** Saint-Pierre view. Publication is **not** photographic exposure date. Record notes historic Underwood copyright. |
| **413:3** | **LC-DIG-stereo-1s41518** | **Unmatched** | No verified item-level catalog record located. Existing ALT calls it an early morning 1902 eruption photograph; exact subject and exposure date need independent review. A [similarly titled NYPL stereograph](https://old-digitalcollections.nypl.org/items/5e66b3e9-1062-d471-e040-e00a180654d7) was issued circa 1903, but **is not verified as the same image**. Do not substitute its information. |
| **413:4** | **LC-DIG-stereo-1s41424** | [2006688499](https://www.loc.gov/item/2006688499/) | Post-eruption ruins looking north, source catalog warns historic caption-card text is unverified. Exact LOC JPG visibly decoded using a **web image viewer only**. |
| **413:5** | **LC-DIG-stereo-1s41568** | [2004680426](https://www.loc.gov/item/2004680426/) | Post-eruption city and bay from the Boulevard SW; catalog warns old caption-card data are unverified. |

Full exact URLs, ALT descriptions, source uncertainty, and hold flags: `qa/media-recovery/mount_pelee_loc_20261030.json`. Three LOC item records say **“No known restrictions on publication”**, but the [LOC rights guidance](https://www.loc.gov/research-centers/prints-and-photographs/researcher-resources/prints-and-photographs-online-catalog/) expressly places responsibility for assessing rights and securing necessary permissions on researchers. This is **not blanket authorization** to mirror.

**Performance evidence:** Zero logged-out Chromium HTTP responses, actual decoded natural widths, measured wire bytes, rights-cleared binaries, or visitor-side failures. Web-viewer success for 413:4 does not establish FinalVestige.com browser availability. Failed web-tool opening of the other JPGs likewise does not establish they are broken. Historical library original sizes are not downloaded page sizes; reported 42 failures and 76% savings remain unverified.

**Safe recovery sequence:** Browser capture at 390px and 1440px after scrolling lazy images; record per-slot `currentSrc`, redirect chain, HTTP status, `naturalWidth`, actual transfer bytes, screenshot and content type. Repair only confirmed failures. Match exact underlying historical photograph and item rights; credit creator and LOC, measure source binary and SHA-256; resize to **max 960px**, preserving aspect ratio and **never upscale**. After separate approval stage optimized WordPress media and obtain media ID; preserve permalink, original captions unless source-supported editorial correction is approved, and compare visitor wire sizes and visual output. No scraping, unauthorized caching, or Gutenberg post changes.

**Test:** `node --test qa/media-recovery/test_mount_pelee_loc.cjs`; the validator fails closed on invented archival matches, HTTP statuses, image dimensions, savings, copyright clearances and production writes.
