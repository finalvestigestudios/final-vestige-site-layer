# The Page That Moved in the Viewer — Research / QA / Publication Ledger

**FV Library Resource Studio | November 10, 2026 (Pacific) | LOCAL RELEASE CANDIDATE / PUBLICATION HOLD**

**Purpose.** A research problem not covered by existing published *Archive Trail*, *Paper Witness* or *The Page That Changed*, nor by current draft *Frame Before the Frame*: mapping the **printed page/folio mark**, a **digital institutional viewer image or IIIF Canvas**, and the **downloaded PDF page index** in a single precise citation. A failed page match must never be “repaired” by guessing a constant offset. Existing formats and paths preserved.

**Completed standalone package (ChatGPT conversation artifact, NOT website-hosted):**
- Self-contained original 28 KB HTML field guide, responsive original 3-lane SVG diagram with text alternatives, original factual LOC book metadata comparison, seven-pass method, 13-field Page Witness Desk, local-only JSON export/import, TSV export, reset, printable one-page card.
- Three-page original PDF *Page Witness Field Card* (method, blank worksheet and eight-source link/rights directory), 8 clickable source references; both 3-page PDF and 1-page browser-generated card rendered.
- Eight-entry dated first-party source/rights CSV+JSON, reproducible local browser QA and screenshots at 320/390/768/1440, SHA256 manifest and ZIP.
- No archival scans, copied page images, seals, other copyrighted third-party visuals, remote requests, private data processing, subscriptions or paid services.

## Ground-truth teaching examples
- LOC **Ralph Waldo Emerson, Nature**, Duffield, New York (1909), item **09027012**: LOC index describes **53 pages and 66 viewer images**. https://www.loc.gov/item/09027012/
- LOC **Scattered Leaves** (1839), item **27017030**: LOC index describes **100 pages and 110 viewer images**. https://www.loc.gov/item/27017030/
- **Critical qualification:** Direct automated open of both specific LOC item URLs returned HTTP 403. Values were verified from LOC-owned indexed item descriptions; **no page-by-page image-to-printed-page mapping was visually inspected**. Different total counts do NOT prove the position of a particular page nor an invariant offset. These item records require ordinary-browser manual recheck before publication.

## Institutional source and access ledger — checked Nov 10, 2026
| ID | Original first-party source | Why it matters / limitation |
|---|---|---|
| S01 | [LOC Nature 1909](https://www.loc.gov/item/09027012/) | 53 printed pages vs 66 viewer images; indexed metadata, direct viewer blocked. |
| S02 | [LOC Scattered Leaves 1839](https://www.loc.gov/item/27017030/) | 100 pages vs 110 viewer images; indexed metadata, direct viewer blocked. |
| S03 | [LOC Citing Primary Sources](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/citing/) | Stable source identity, creator and context; not automatic image-level locators. |
| S04 | [LOC Copyright and Primary Sources](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/copyright/) | Online viewing does not authorize third-party reproduction. |
| S05 | [NARA Using the Catalog](https://www.archives.gov/research/catalog/help/using) | Metadata/catalog descriptions vs digitized files, access limitations. |
| S06 | [NARA Online Research Tools](https://www.archives.gov/research/start/online-tools) | Archives discovery requires multiple tools; not all descriptions link to scans. |
| S07 | [LOC Finding Primary Sources](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/finding/) | Collection online coverage and staff assistance. |
| S08 | [LOC Chicago citation examples](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/citing/chicago/) | Citation conventions vary, page witness must be item-specific. |

**Rights.** Original diagram, text, software and worksheet: Final Vestige Studios (2026), intended as free Library educational material. No historical source images or excerpts copied. Each external item retains its institution's item-level rights; the LOC metadata's public-domain note for *Nature* does not automatically clear a different item's content.

## QA and release condition
- **PASS — standalone only:** Chromium in-memory actual HTML render at 320/390/768/1440 with JS on and off (8/8, no page overflow or JS exceptions); 8 source rows and 13 labeled form fields at all sizes. Real functional browser tests confirmed Blob payload construction for JSON and TSV, JSON reimport, clear/reset, inert HTML-shaped user content, invalid-source URL rejection, print action, browser-generated single-page print card. OS-native save/download operation not tested; Blob anchor click intercepted to inspect saved bytes.
- **PASS — PDF/local archive:** 3-page PDF rendered and visually inspected; corrected worksheet footer spacing. 8 clickable official source links. ZIP integrity test passed. ZIP SHA256: `a2404d3e3b769d0b9181c916019e1d159866f6626f941029e5730090005d2b6c`.
- **NOT PASSED:** Real WordPress Assembler theme at 320/390/768/1440, keyboard/screen-reader/theme contrast, anonymous retrieval of LOC examples and all outbound links, public PDF download integrity, first-publish email/social suppression. WordPress page-create/update connector for pages does not expose `_jetpack_dont_email_post_to_subs=true` or `jetpack_publicize_feature_enabled=false`, though **post** tools do; this does not authorize publishing a static Library guide as a newsletter post.
- **Decision: HOLD.** No new WordPress page, existing page overwrite, Library index card, subscriber mail, social share or spending. Issue #1589 coordinates real-theme visual access; Library Research Sources issue #1788 is a separate higher-priority release and remains untouched.

**Proposed internal crosslinks after release:** https://finalvestige.com/the-archive-trail/ , https://finalvestige.com/the-paper-witness/ and https://finalvestige.com/free-resources/the-page-that-changed/ .

**Potential Grok short (no distribution now):** “This 53-page book has 66 images. So where is page 24?” Show only explicitly labeled FV schematic, LOC metadata on-screen only if rights/context checked, and ask for the observed page before asserting a number. 

**Next:** Recheck the two LOC book objects in a normal browser, provide exact item-level image witness or keep the catalog-only example, obtain authenticated theme screenshots, verify item-level notification controls, stage one scoped WordPress child page, verify anonymous page and media, add one Library card. Do not publish without all gates.