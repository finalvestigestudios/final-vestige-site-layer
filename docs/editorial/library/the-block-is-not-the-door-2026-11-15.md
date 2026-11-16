# The Block Is Not the Door — Library draft #2438 continuation
**Date:** November 15, 2026 · **Owner:** FV Library Resource Studio · **Status:** PUBLIC HOLD

## Non-duplication and purpose
Reviewed the live Library, Editorial Standards, Research Sources, published archive/mapping guides, existing [issue #2185](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/2185) and authenticated draft [#2438](https://finalvestige.com/wp-admin/post.php?post=2438&action=edit). This is a new **source-limited archival case study appended to the existing draft** *The House That Changed Its Number*, not another WordPress page or competing publication.

## Research finding
[Chicago History Museum's Address Conversion Guides](https://libguides.chicagohistory.org/buildings/addressconversion) (page last updated November 10, 2026; directly retrieved November 15) supplies the following **pre-1879** example: historical **1001 Prairie Avenue** lies numerically between **998 at 22nd Street** and **1062 at 23rd Street**; the museum places it in the modern **2200 block of South Prairie**. It **does not** establish an exact modern door, lot, extant building or occupant. The underlying historic street-guide leaf was not independently retrieved: the museum guide is the examined witness for the values.

Additional official provenance:
- [Northwestern University: 1909 Chicago renumbering book](https://homicide.northwestern.edu/renumbering/books/1909/) — outside Loop, source describes public-domain 1909 book; print scan not republished.
- [Northwestern University: 1911 Loop table](https://homicide.northwestern.edu/renumbering/books/1911/) — table made **1934 or later** about a 1911 renumbering, uncertain typist and non-one-to-one entries. Not misdated as an original 1911 print.
- [NARA 1930 Geographic Search Strategies](https://www.archives.gov/research/census/1930/geographic-resources.html) — city directories and ED boundaries for cross-checking; ED maps do not list every street.
- [LOC Sanborn rights guidance](https://www.loc.gov/collections/sanborn-maps/about-this-collection/rights-and-access/) — automated HTTP 403; link-only, no individual reproduction rights claimed.
- Canonical published FV related pages independently confirmed in WordPress: [The Archive Trail](https://finalvestige.com/the-archive-trail/) (#189) and [The Lost Landscape](https://finalvestige.com/the-lost-landscape/) (#193).

## Delivered as Library conversation files
- `the-block-is-not-the-door.html`: original accessible static narrative, labeled schematic SVG, local numerical-boundary desk (NOT an address converter/geocoder), 10 fields, optional JSON receipt/print; no tracking, remote dependencies or file uploads.
- `Block_Not_Door_Field_Receipt.pdf`: two-page original printable evidence worksheet.
- `source_rights_ledger.json` and CSV: six provenance / rights records with November 15 checks; dated rights limits and 403 preserved.
- `QA_results.json`, eight Chromium screenshots, QA script, source generator and release-hold report.

## Test evidence (do not confuse with production QA)
Local Chromium using **page.set_content** at **320/390/768/1440 × JS on/off: 8/8 PASS** for no horizontal overflow, no console exceptions, source visibility. On all four JS-on configurations checked 1001∈(998,1062), outside 997, boundary 998, noninteger 1.5, local JSON export and reset. 10 fields with unique DOM IDs. Two PDF pages rendered and visually inspected, **untagged**. **These are not real WP-theme screenshots**; screenshot service limitation and container DNS remain.

## WordPress write / authenticated independent readback
- Existing WP draft **#2438** under Library **#77**, slug `the-house-that-changed-its-number`, remains **draft/noindex**. No new draft or live card created.
- Appended one static, source-linked, original-SVG Gutenberg `core/html` block with optimistic lock. Final site-local modified **2026-11-15T21:44:06**; overall `content_hash=d251db3b6e46926d92607c896c02aa1a6caa2b1d`.
- Existing original section 0 `block_hash=456f3391cd87805fa3366925f03cef5e1f2fcd08` unchanged; new section block hash `e746d2bfdc03607e31396fc0cfa974dee5382867`; case-study marker occurs **once**.
- Corrected initial unverified FV crosslink variants before finalizing; the actual canonical links resolve to `/the-archive-trail/` and `/the-lost-landscape/`, independently checked via authenticated WP pages. No WordPress content warnings.

## Release HOLD / next work
Do **not** first-publish: production-theme visual/keyboard/ARIA QA at 320, 390, 768, 1440 unavailable; companion downloads have no anonymous public hosting; explicit first-publication Jetpack email suppression `_jetpack_dont_email_post_to_subs=true` and auto-publicize-off **cannot** be enforced through current connected page publishing schema; PDF tagging still open. No archival scans copied or rights assumed. Real publish must verify actual source links, multimedia/asset health, public URL and WP metadata independently after first-publish settings are enforced.

**Boundaries:** no live WordPress page, navigation, subscriber/email/social, Grok account, homepage engineering, Preparedness, Investigations or spending changes. Potential post-release Grok short hook: “Your ancestor's address may lead to the right block and the wrong house.” No promotion requested or executed.
