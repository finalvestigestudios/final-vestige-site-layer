# The Archive Did Not Say No — Source-access field guide and Library access-triage record

**FV Library Resource Studio · checked 2026-11-11 UTC · status: local release candidate / PUBLICATION HOLD.**
**Owner:** Library only; no Prepararedness, Investigations, homepage engineering, subscriber, paid service or Grok-account writes.

## Reader problem and distinct scope

A browser response is not a historical-record finding. A source returning a 403/406, a JavaScript app shell, a zero-result query, a finding-aid description without an item scan, a legally restricted item, or an otherwise viewable image with unclear reproduction rights must be recorded as **different evidentiary states**. The new original FV guide **The Archive Did Not Say No** gives a seven-step retrieval and qualification method with an original explanatory diagram, five institution-anchored examples, and an 11-control private Access Witness form with JSON download and print.

This is distinct from published *The Archive Trail* (claims), *The Page That Changed* (web page version history), and *The Box Behind the Citation* (finding-aid/box identity). It also provides a reusable method for the existing 90-source Research Sources directory, without creating a second live directory.

### New package prepared locally (NOT hosted in GitHub or WordPress)

- `The_Archive_Did_Not_Say_No.html`: original standalone illustrated field guide, 27 open source-access checks, offline worksheet.
- `Access_Witness_Field_Card.pdf`: three-page original printable guide and card.
- `Source_Provenance_Rights.csv`: 10 dated records (eight institutional + two FV).
- `Unresolved_Access_Review_Register.csv`: **27** active source-access follow-ups, each with primary URL and evidence limitations.
- `QA_Report.json`, screenshots, builder/tests, README and release ZIP.

**Counting correction:** the November 10 controlling provenance register held 28 nontrivial follow-up labels, but card **#49 America Burning** was already checked via its official PDF and has status `none_for_pdf_access`; the active unresolved review list is **27**. The earlier shorthand `26 inconclusive` is not the number of open nontrivial follow-ups in that fetched register. No claim that any of these 27 original links is broken for an ordinary reader.

## Specific first-party source observations — November 11

| FV card | Source | Actual observation in this run | Next ordinary-browser check |
|---|---|---|---|
| #34 | [GovInfo Congressional Hearings](https://www.govinfo.gov/app/collection/chrg) | Official [GovInfo help](https://www.govinfo.gov/help/chrg) directly readable: select hearing coverage, 104th Congress onward plus some older; publication can lag; document PDF images can differ from text. Collection app itself does not prove an item. | Open actual package/granule, preserve ID, verify PDF/text content separately. |
| #54 | [NTSB CAROL](https://my.ntsb.gov/) | NTSB's official portal is indexed with Basic/Aviation/Custom/Published search pathways. Direct automated open yielded no extractable page text. | Open live search in normal browser; verify an actual investigation/docket record. |
| #64 | [DOE OSTI.GOV](https://www.osti.gov/) | Official [DOE Search Tools directory](https://www.osti.gov/search-tools) indexed with OSTI.GOV, DOE PAGES, Data Explorer and CODE; direct opening of directory returned 502 in this client. | Interactive search; distinguish metadata from accessible full report and rights. |
| #66 | [Smithsonian Open Access](https://www.si.edu/openaccess) | Institutional page indexed but direct web open returned 404. Official [Open Access FAQ](https://www.si.edu/openaccess/faq) confirms CC0 applies only to specifically marked media; third-party rights/trademarks/privacy remain. | Open page in ordinary visitor browser, inspect specific item CC0 icon. |
| #68 | [NARA Catalog](https://catalog.archives.gov/) | Direct automated reader returned a tiny JavaScript shell. First-party [catalog help](https://www.archives.gov/research/catalog/help/using) confirms catalog descriptions vs digitized content and restricted/unprocessed items. | Normal-browser catalog search with stable accession/record identifier. |

**No other source was retested on November 11.** The 22 other unresolved cards retain their dated November 10 observation. This is a preliminary access-triage package, not 27 newly confirmed working/failed links.

### Editorial method / rights

Primary instruction pages:
- [NARA Catalog Help](https://www.archives.gov/research/catalog/help/using)
- [GovInfo CHRG help](https://www.govinfo.gov/help/chrg)
- [NTSB CAROL official portal](https://my.ntsb.gov/)
- [Smithsonian Open Access](https://www.si.edu/openaccess) and [FAQ](https://www.si.edu/openaccess/faq)
- [DOE Search Tools](https://www.osti.gov/search-tools)
- [NARA Digitization](https://www.archives.gov/digitization)
- [LOC copyright guidance](https://www.loc.gov/legal/security-copyright-and-privacy/understanding-copyright/)
- [FV Editorial Standards](https://finalvestige.com/editorial-standards/)

All editorial prose, browser worksheet, diagram, and PDF art original Final Vestige Studios (2026-11-11). Sources are links only; NO institutional photos, scans, logos, copyright-protected figures, seals or video copied. Public accessibility, metadata existence and copyright clearance are **not interchangeable**.

## QA record and blockers

**Standalone local QA:** Chromium in-memory rendering (not a live-site browser) **8/8 pass** across 320/390/768/1440 with JS on/off; zero document overflows and JavaScript exceptions; 27 review rows, 10 source cards, 11 controls. JSON download, HTML-shaped text treated as data, invalid URL protocol rejection, and reset passed; local screenshots at mobile/desktop inspected. Three-page PDF rendered and all pages visually reviewed; 5 clickable institutional links. ZIP CRC/integrity PASS.

**PUBLICATION HOLD:** No authenticated production-theme WordPress preview at the four required widths with inspectable pixels; no complete ordinary-reader access clearance for the 27 outstanding sources; WordPress page API cannot enforce `_jetpack_dont_email_post_to_subs=true` plus Social/Publicize false on first publish. Previous mshots calls return links without image pixels. Local stand-alone QA is NOT production-site acceptance. Do NOT publish a new Library card or guide under this gate.

**Important live directory owner constraint:** public Research Sources **#1338** remains published with its original path and stale initial `60` copy, while the 90-source integrity staging **#2354** remains draft/noindex. Use a guarded, in-place public page update only after current production gate and link checks; do not publish #2354 as a duplicate. Related issues [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) and [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589).

**Post-release Grok idea only:** “The archive returned 403. Did the record disappear—or just the door?” No media/social action before verified public release.
