# The Envelope Was a Route — Postal Mark Witness (2026-11-11)

**Owner:** Final Vestige Studios Library editorial lane. **State:** unpublished release candidate; no WordPress changes made.

## Reader problem
A historical letter may include a handwritten composition date, dispatch or cancellation mark, an intermediate transit mark, a forwarding instruction, and a later receiving/backstamp. These are independent evidence types. The guide prevents researchers from treating one postmark as an assertion of authorship, first postal acceptance, complete itinerary or delivery to the named addressee.

## Original assets
- Standalone responsive HTML article: `The_Envelope_Was_a_Route.html` (~35 KB), including accessible original fictional front-and-back cover SVG and local-only Postal Mark Witness form with repeatable mark records, provisional date ordering, safe text rendering, JSON export and print action.
- Four-page designed printable PDF: `Postal_Mark_Witness_Field_Cards.pdf`, with original diagram, seven-pass method, 2-mark blank witness card and source URLs.
- 12-source institutional and internal provenance CSV, plus an original-media rights/alt-text CSV (two entries), with access and last-checked qualifications.
- Runnable local browser QA (`qa.py`), build scripts, README, SHA-256 manifest and self-contained release ZIP.
- Art does not reproduce third-party scans or stamps. Diagram labels all place names and dates as fictional.

The files were generated in the Library Studio conversation as a downloadable release candidate; they are **not** claimed to be hosted in this GitHub repository.

## Primary evidence and source links
1. Smithsonian/NPM, marking devices: https://postalmuseum.si.edu/exhibition/about-postal-operations-mail-processing/marking-devices
2. Smithsonian/NPM, covers and letters: https://postalmuseum.si.edu/exhibition/about-philately/covers-and-letters
3. Smithsonian accessioned stampless cover c.1849, object NPM 2007.2004.19 (PA→KY forwarding, rate annotations): https://www.si.edu/es/object/stampless-cover%3Anpm_2007.2004.19
4. Smithsonian accessioned stampless cover 1849, object NPM 1984.0531.702 (SAN FRANCISCO postmark, manuscript rate 80): https://www.si.edu/object/stampless-cover%3Anpm_1984.0531.702
5. Smithsonian object NPM 2005.2005.111 (1872 transatlantic routing/rate evidence): https://postalmuseum.si.edu/object/npm_2005.2005.111
6. Smithsonian NPM receiving handstamp NPM 1987.0905.20: https://postalmuseum.si.edu/object/npm_1987.0905.20
7. NPM image reuse policy (individual CC0 vs restricted media): https://postalmuseum.si.edu/rights-and-reproductions
8. Official USPS 2026 DMM clarification (modern—not applied retroactively to nineteenth-century covers): https://about.usps.com/postal-bulletin/2026/pb22694/html/updt_002.htm
9. NPM collections discovery: https://postalmuseum.si.edu/collections-search-center
10. NPM registered handstamp NPM 1992.2002.830: https://postalmuseum.si.edu/object/npm_1992.2002.830

Related FV reading: [Paper Witness](https://finalvestige.com/the-paper-witness/), [Box Behind the Citation](https://finalvestige.com/free-resources/the-box-behind-the-citation/), [Archive Trail](https://finalvestige.com/the-archive-trail/). [Editorial Standards](https://finalvestige.com/editorial-standards/) govern the publication.

**Last research check:** 2026-11-11. Institutional indexed descriptions and item-specific CC0 metadata were reviewed, but **some Smithsonian direct page opens were rejected by automated fetchers**; these are neither counted as verified anonymous-browser access nor classified as broken. No third-party museum images were reproduced.

## Quality evidence
- Standalone Chromium at **320, 390, 768, 1440 px** with JavaScript on and off: **8/8 layout passes**, no page overflow or script exceptions.
- Interactive tests: repeatable mark entry, provisional date sequence, inert display of HTML-like user input, JSON export, URL scheme validation, reset, internal anchors: passed. **32/32 total checks**.
- Print PDF: 4 pages, rendered and visually inspected; **12 embedded institutional/internal PDF hyperlinks**. ZIP CRC passed. Archive SHA-256: `26d9c534f2c7db83c84720e3912ca6220006079dedaf1c44853f822d01a4caaf`.
- The browser was fed the exact standalone HTML via `set_content()` because direct file navigation was administratively blocked. This is **not** production WordPress-theme inspection.

## Publication gate — HOLD
1. Ordinary-browser verification of Smithsonian object links and item-level image rights.
2. Verified hosting of PDF and diagram; update the relative companion link.
3. Actual WordPress draft/theme screenshot + keyboard QA at 320 / 390 / 768 / 1440 and anonymous public visitor check.
4. Enforce `_jetpack_dont_email_post_to_subs=true` and automatic social sharing disabled **in the first publication request**; available WordPress connector cannot guarantee those fields.
5. Only then publish a new resource under the existing Library hierarchy and insert a **single** scoped Library card/cross-links, preserving all existing paths. Research Sources #1338's 90-source count correction in #1788 is still the higher live-site release priority.

**No public WP modifications, promotions, new expenditures or subscriber emails.** Optional Grok hook after publishing: *A letter's date is not the date of its journey.*

## Final media-rights clarification
Original schematic: © 2026 Final Vestige Studios, all rights reserved; no public reuse license granted; original local file `Original_Cover_Diagram.svg`, not yet publicly hosted. Descriptive SVG title/alt and a fictional-sample caption are embedded. Printable PDF also remains an original FV editorial layout. Release ZIP rebuilt with the media ledger (11 archive entries), SHA-256 `26d9c534f2c7db83c84720e3912ca6220006079dedaf1c44853f822d01a4caaf`.
