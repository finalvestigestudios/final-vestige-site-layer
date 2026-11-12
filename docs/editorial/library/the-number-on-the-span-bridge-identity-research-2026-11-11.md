# The Number on the Span — Bridge Identity Witness

**Final Vestige Studios / The Library · Research and release record · November 11, 2026 (Pacific)**

**WordPress editorial draft:** [#2426](https://finalvestige.com/wp-admin/post.php?post=2426&action=edit), `draft`, parent Library #77, `jetpack_seo_noindex=true`. **Not published**. Full standalone guide, interactive private witness, and three-page printable source worksheet are available as conversation release attachments, not hosted on WordPress or in this GitHub repository.

## Distinct reader need

Readers researching a historic bridge often conflate a local road/bridge designation, a National Bridge Inventory (NBI) structure identifier, a Historic American Engineering Record (HAER) survey number, and a Library of Congress item/call number. Worse, a replacement bridge can occupy the same crossing. The guide therefore asks **which physical structure stood at the crossing on the specified date**, not simply whether two catalog records share a place name.

Checked existing live Library /free-resources/, published guides, drafts (including The Scan Witness, The Frame Before the Frame, The Old Line, The Lost Landscape and The Failure Chain), and GitHub coordination issue #1788. This is a distinct bridge-specific ID-crosswalk guide; it does not duplicate scan comparison, microfilm frames, boundary surveys or accident-investigation methods. Scope explicitly excludes Preparedness, Investigations, homepage and shared templates.

## Verified real source example: Waterloo Bridge

[Library of Congress catalog item VA1750](https://www.loc.gov/pictures/item/va1750/):
- main title: Waterloo Bridge, State Route 613 crossing the Rappahannock River, Fauquier/Culpeper, Virginia
- **Other Title**: Bridge No. 6906
- **HAER survey**: VA-112
- **LOC call number**: HAER VA,24-WATLO,1-
- historic record: 1919 initial construction, with 18 survey photographs, 18 data pages and two caption pages; iron/steel Pratt truss and beam-deck spans described

**Not established:** that Bridge No. 6906 is the NBI `STRUCTURE_NUMBER_008`, that a later replacement retains the original survey number, or that the recorded bridge survives unchanged today. The catalog item is a specific archival example, not a current condition or route-clearance report. Indexed official LOC metadata was inspected; automated direct page access returned HTTP 403, which is **not** a confirmed public link failure. Ordinary-browser verification remains a publication gate.

## Primary sources and last-check ledger

Checked **November 11, 2026** unless stated. Links are institutional references, not republished images.

| Institution | Original record | Findings, access limits and reuse |
|---|---|---|
| FHWA | [NBI data and warnings](https://www.fhwa.dot.gov/bridge/nbi/nbi_data.cfm) | Official page updated **October 21, 2026**. Annual files may be corrected, considered final for year June 15; **not for route clearance**; 2026–2027 SNBI transition may contain temporary codes/nulls. Official HTML retrieved. U.S. government source, no imagery copied. |
| FHWA | [2026 state bridge data](https://www.fhwa.dot.gov/bridge/nbi/nbi_data_2026.cfm) | Official state Excel, JSON and GeoJSON downloads listed; every specific downloaded file's content **not** individually inspected. |
| US DOT | [NBI public data schema](https://data.transportation.gov/Roadways-and-Bridges/National-Bridge-Inventory/pced-83j4) | Official indexed portal: `STRUCTURE_NUMBER_008` text, `FACILITY_CARRIED_007` and `FEATURES_DESC_006A`; public-domain federal dataset. Do not silently transfer legacy field definitions across SNBI transition. |
| FHWA | [National Bridge Inspection Standards](https://www.fhwa.dot.gov/bridge/nbis.cfm) | Official HTML, updated **May 27, 2026**; federal inspection framework, not an assessment of a particular bridge. |
| NPS | [Historic American Engineering Record](https://www.nps.gov/subjects/heritagedocumentation/haer.htm) | Official page updated **August 12, 2026**, HAER founded in 1969 to document engineering heritage. |
| NPS | [HABS/HAER/HALS collection](https://www.nps.gov/subjects/heritagedocumentation/collection.htm) | Official page updated **August 12, 2026**. Drawings, photography, historic reports; some field notes require reading room appointment; material created for programs is public domain. |
| LOC | [Waterloo Bridge VA1750](https://www.loc.gov/pictures/item/va1750/) | Indexed official item metadata verified. Direct automated opening returned 403. No third-party images embedded; catalog's rights advisory notes contributed materials may differ. |
| LOC | [HABS/HAER/HALS rights](https://www.loc.gov/rr/print/res/114_habs.html) | Original federally created photographs and drawings generally public domain; third-party contributions may be restricted. No item-specific clearance inferred. |

Related live Final Vestige content: [The Lost Landscape](https://finalvestige.com/the-lost-landscape/), [The Failure Chain](https://finalvestige.com/the-failure-chain/), [Research Sources](https://finalvestige.com/free-resources/research-sources/), and [Editorial Standards](https://finalvestige.com/editorial-standards/).

## Original asset / media / rights

- **The Number on the Span**: responsive HTML editorial guide, nine research sections, source-based real LOC case, original fully described SVG four-lane ID diagram, searchable source trail, browser-local Bridge Identity Witness with JSON export, reset and print.
- **Bridge Identity Witness Field Cards**: original 3-page PDF with evidence crosswalk, record worksheet, clickable official source links and rights statements.
- **Provenance and rights CSV**: 13 records, containing creator, title, primary URL, source/access status, qualified rights and record use.
- No archive photos, drawings, institutional seals, data rows or other third-party graphics copied. Artwork and text original to Final Vestige Studios. Illustrative graphic is explicitly *not a historical documentary record*.
- No paid resources, third-party scripts, tracking, telemetry, uploads, lead-magnet gate, email sends or Grok account modifications.

## Local QA, not a production visual pass

- Chromium / Playwright with HTML injected from the standalone release: **8/8** viewport states passed at **320, 390, 768, 1440 px**, both JavaScript on/off. No document-wide horizontal overflow, no uncaught JavaScript errors; nine sections, eight institutional source links and accessible SVG remain present.
- At 390px, JSON export retains a structure number with leading zeros, serializes HTML-shaped text inertly, rejects HTTP (requires HTTPS for LOC permalink), records source URL and clears notes on reset; all passed.
- Three printable PDF pages rendered and visually inspected. One original illustration only; no archive imagery.
- The local browser refuses file/localhost navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`); tests use `page.set_content`, not networked WordPress. **Do not claim these screenshots show the production WP theme**.
- Authenticated WP readback independently confirmed #2426 remains `draft`, parent #77, original illustrative diagram, source links, safety warning, **no script elements**, `jetpack_seo_noindex=true`; no warnings returned.

## Release status: HOLD

The existing published Research Sources page #1338 still has stale 60-source static labels, despite 90 actual cards (12 declassified, 24 accountability, 21 engineering, 25 archives, 8 navigation). Coordination #1788 stays P1 and must not be confused with this new guide.

Do **not** publish #2426 or add a Library navigation card until all apply:
1. Test **actual production WordPress-theme** preview at 320, 390, 768 and 1440 px for no overflow, readable tables/SVG, visible focus, working links, print and no-JS; inspect real pixels, not an mshots URL alone.
2. Open the LOC item in an ordinary browser and verify catalog metadata; check independent visitor access to all 8 official links.
3. If offering downloadable HTML/PDF, upload and independently verify hosted media URL, MIME, alt/caption and rights before adding a download link.
4. Confirm first-publication subscriber email and auto-social suppression. A page is not typically treated like a newsletter post, but custom hooks remain unverified; never imply `_jetpack_dont_email_post_to_subs` was set when the exposed WordPress meta interface does not accept that key.
5. Publish only #2426 with noindex removed after approval gates; minimally add one Library card to #77; independently inspect anonymous public URL, canonical, metadata, links/media and issue closure.

**Grok promotion candidate (not sent)**: “The bridge number and the history number are both real. Why don't they match?” Show only original illustration and verify every historical comparison before producing a video. Do not touch Grok's accounts.

**Publication outcome:** editorial draft only, no live page/navigation changes, no subscriber emails, no new spending.
