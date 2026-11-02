# Historical-image attribution and rights register (2026-11-02)

This register records what was **verified in this sprint** and what was **not**. It is evidence for a human sign-off, not a legal opinion. No image was replaced and none was fabricated. Credits are in the three "Inspect the source & limits" drawers of the flagship.

| | Apollo 1 crew photograph | Victory Point note (Franklin) | Brooklyn Rapid Transit map (Malbone) |
|---|---|---|---|
| Identifier | NASA **S67-19766** | Wikimedia Commons **File:Franklinexpeditionnote.jpg** | NYPL Digital Collections, image ID **5003296**, item UUID `a51f7de0-379e-013b-80a1-0242ac110003` (the catalogue link in the page, `c745e730-...`, redirects to it) |
| Original verified | NASA image page `nasa.gov/image-detail/apollo-1-crew-honored/`; file `.../2023/03/s67-19766.jpg`, 1041 x 810, 163,367 B, sha256 `73b1d25f...34d9b4` | Commons file, 1576 x 2506, 902,181 B (Commons SHA-1 `584cf387d7dcf3e259058ec14db2f4c7d04bac00`; sha256 `c416ddf4...5b1eac`) | `images.nypl.org/index.php?id=5003296`, 759 x 513 derivative, sha256 `af807e6c...a77202` |
| Site file | `s67-19766.webp` (WordPress media 473), served by the Jetpack CDN at 1024 px: 76,876 B | `Franklinexpeditionnote.jpg` (media 474), CDN 960 px: 301,260 B | `edit-017-v02-nypl-5003296-original.jpg` (media 1258, 5667 x 3831 original), CDN 1024-1536 px: 129,395-282,367 B |
| Identity check | Normalised cross-correlation of 48x48 luminance vs original **0.9999** | **0.9998** | **0.9982** |
| Source's own statement | NASA media/brand guidance generally allows educational and informational use and prohibits implying NASA endorsement. (Not re-read this sprint; see `qa/release-candidate/ARCHIVAL_PROVENANCE_ADMISSION_20261031.md`.) | Commons metadata read today via its public API: license **"Public domain"** (`pd`), `Copyrighted: False`, attribution not required. It is a scan of an **1869 printed reproduction**, not a photograph supplied by the museum. | NYPL item page read today: NYPL believes the item is in the public domain under United States law and made **no** determination for other countries; it asks, but does not require, the credit "From The New York Public Library" with a link back. |
| Credit now in the page | "Credit: NASA. Shown for editorial and educational context; NASA does not endorse Final Vestige or any product or service." | "Rights: The displayed scan is the Wikimedia Commons file marked public domain, not a photograph supplied by the museum." Museum object (RMG HSR/C/9/1) and Canadian Museum of History transcription are linked separately. | "Credit: From The New York Public Library. NYPL believes this item is in the public domain under United States law." Item link retained. |
| What the image must not be used to say | Not evidence of the hatch mechanism or ignition source (stated on page). Not to be used beside commerce. | The document's later margin entry is evidence of what the writers reported, not of every crew member's fate (stated on page). Do not claim an RMG image licence. | The 1903 network map is **not** a plan of the 1918 temporary curve (stated on page). |
| Commerce adjacency | The flagship carries no earning link. Keep it that way: no affiliate or Inspire3 link may sit beside this photograph. | same | same |
| Status | Editorial-use basis documented; **item-specific NASA reproduction conditions need a named editorial sign-off** | Basis documented (Commons PD) | Basis documented (NYPL US-PD statement; credit added) |

## Other images on the homepage

- Observer Lab specimens: original CSS-built illustrations, labelled "illustrative specimens, not archival records".
- Hero Franklin "note": original editorial typesetting, labelled "not a facsimile".
- Focus Fieldbook cover and the preserved "latest/recently filed" thumbnails: existing production media, unchanged.

## Open items before publication

1. A named editor confirms the NASA item-specific conditions (founder approves the editorial concept and use of cleared images; this does not replace that check).
2. Confirm that the WordPress media records 473, 474, 1258 carry the same credit text as the page (WordPress media metadata was read on 2026-10-31 and showed empty caption/description for 473 and 474).
3. Re-check the NYPL statement at release time (statements can be revised).
