# The Flightline — Field Instrument 05: The Frame Is Not the Map
**Editorial, rights and release QA ledger — 2026-11-17 (America/Los_Angeles)**

## Scope and custody
Continues the *existing* Final Vestige Studios Library draft [The Flightline, WordPress #2301](https://finalvestige.com/wp-admin/post.php?post=2301&action=edit), parent #77, slug `the-flightline`. This is a sixth isolated Gutenberg HTML block, not a new competing page. Existing five blocks' hashes remain intact. Public Library and Research Sources are not edited. Coordination: [Library Flightline issue #1724](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1724), shared browser gate [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). Source HTML is committed on this review branch.

## Reader problem / deliverable
USGS aerial images are often treated as maps with exact scale and coordinate geometry, even though ordinary unrectified scans do not confer map-position certainty. A 1,463-word original research supplement explains original film exposure vs preview/scan vs corrected imagery vs modern overlay. Deliverables: six-item primary-source rights/provenance ledger, original clearly fictional explanatory SVG with `title` and `desc`, a nominal 9-inch-frame scale comparison table for USGS NAPP / NHAP BW / NHAP CIR, an eight-field printable witness worksheet, and an explicit refusal to infer coordinate precision from browser pixel width. No third-party photographs or archival scans copied. All FV illustration/text rights owned by Final Vestige Studios; illustrative geometry not documentary evidence.

## Source ledger — links opened / checked 2026-11-17
1. **USGS EROS, National Aerial Photography Program (NAPP)** (July 9, 2018): https://www.usgs.gov/centers/eros/science/usgs-eros-archive-aerial-photography-national-aerial-photography-program-napp . Establishes nominal 1:40,000 scale, nine-inch acquisition format, 1987–2007 program, overlap and the explicit notice that imagery is not geocorrected. Free institutional page, linked only; collection rights do not automatically clear third-party content.
2. **USGS EROS, National High Altitude Photography (NHAP)** (July 9, 2018): https://www.usgs.gov/centers/eros/science/usgs-eros-archive-aerial-photography-national-high-altitude-photography-nhap . Establishes BW 1:80,000 / color-infrared 1:58,000, color-IR interpretation caution and lack of geocorrection. Linked only; no sample media copied.
3. **USGS EROS, Aerial Photo Single Frames Data Dictionary** (June 11, 2021): https://www.usgs.gov/centers/eros/science/aerial-photo-single-frames-data-dictionary . Fields include acquisition date, original film dimensions, roll, frame, image type, focal length, scale, browse status. Linked only.
4. **USGS, How much area does an aerial photograph cover?** https://www.usgs.gov/faqs/how-much-area-does-aerial-photograph-cover . Ratio/scale geometry and camera focal-length principle. Linked only.
5. **National Archives, Publishing National Archives Photos** (last reviewed Nov 22, 2019): https://www.archives.gov/research/still-pictures/publish-photos . Small fraction of photographic records may have restrictions; NARA does not certify item-level copyright. Linked only.
6. **Library of Congress, About the Prints & Photographs Online Catalog** https://www.loc.gov/pictures/about/ . Institutional search result found; direct fetch gave HTTP 403 in this environment, so reader access is **not independently confirmed**. No LOC material copied. For individual rights check, consult each item's record; possession/public access is not a license.

### Numerical boundaries
`film side (inches) × nominal scale denominator ÷ 63,360` produces about 5.68 miles for 9in at 1:40,000, 11.36 miles for 1:80,000, and 8.24 miles for 1:58,000. The first exceeds USGS's rounded ~5.5-mile usable/illustrated example; this is identified as an *illustrative simple conversion*, **not** a corrected image footprint or positional uncertainty. Camera tilt, elevation and lens distortion remain unresolved until source-specific correction evidence is available.

## QA receipts
- Authenticated WordPress scoped `page-sections-insert` then one guarded `page-sections-replace` to correct the Missing Caption internal link to its published canonical URL, https://finalvestige.com/the-missing-caption/.
- WordPress #2301 status `draft`, parent #77, SEO `noindex=true`; modified **2026-11-17T13:35:23** site-local.
- Serialized page content **64,195 characters**, sixth source HTML block **16,613 characters**.
- Final WordPress page `content_hash=66cb03369e8fad465bb565816144d1d52c728250`.
- Five previous block hashes preserved: `670bb52b...`, `d4c1e194...`, `c779bbe...`, `858f947...`, `8f10df...`.
- Independent GitHub `fetch_file` vs authenticated WordPress last block **exact byte parity**, blob SHA `92a2288823fae9534a006aae2f54dd9bf202ae3f`. Full-file, metadata, markup and link checks: **15/15** passed. Unique DOM IDs, source links HTTPS, accessible table region/caption, original SVG title/desc, print/mobile CSS, no external media tags or scripts, no links to the old incorrect URL.
- Existing **public** Library and Research Sources server-side HTML readbacks returned HTTP **200** with their established canonical URLs; both reported 0 missing image-alt attributes, 0 empty links and 0 nowhere links. Research Sources still has stale 60-labels; owned under #1788.
- Individual **external** image objects, scans or film records were not downloaded or licensed. No publication of any third-party images.

## Release decision: HOLD
1. Actual authenticated WordPress production-theme visual and keyboard/screen-reader tests at **320 / 390 / 768 / 1440** are not completed; isolated/source CSS checks cannot replace them. Review footer, original diagram, horizontal table scrolling, overlays and print output.
2. Verify full site-specific first-publish suppression of newsletter/subscriber email and automatic social syndication; the site's default email toggle is insufficient evidence.
3. Before any future first publication, verify final current content hash, source links and rights; only then change draft status, confirm anonymous public URL, canonical/robots/social metadata, and add the Library card through a minimal independent edit.
4. All existing public pages, source paths and cross-lane content remain unchanged; no paid tools, email blasts, Grok accounts, Preparedness, Investigations or homepage engineering were touched.

**Optional Grok concept only:** 30–45-second visual demonstration: “An old aerial photograph can show a road exactly where it was—and still place it incorrectly on a modern map.” Use *only* the labeled FV original conceptual diagram, cite USGS and don't imply the image itself has been georectified. No account changes or uploads.
