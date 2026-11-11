# Library release candidate — The Old Material That Was Reworked
**Last researched:** 2026-11-11 (America/Los_Angeles)  
**Status:** HOLD; no WordPress publication, no social or subscriber distribution  
**Owner:** Library Studio only; does not amend the Crystal Skulls investigation

## Reader problem and intended page
A historic material may be carved, reworked, assembled, or sold at a much later time. The guide distinguishes (1) material age, (2) manufacturing date, (3) later alteration, and (4) earliest documentary appearance. Core public asset: original illustrated field guide with a 12-field client-side Artifact Witness worksheet, local JSON export, reset, print CSS, and a three-page printable witness pack. Planned Library subpage slug: `the-old-material-that-was-reworked`; **not yet created**.

## First-party and scholarly evidence, with qualifications
1. Sax, Walsh, Freestone, Rankin & Meeks, *Journal of Archaeological Science* 35 (2008) 2751–2760, DOI **10.1016/j.jas.2008.05.007**. Authenticated [Kingston university research record](https://researchinnovation.kingston.ac.uk/en/publications/the-origins-of-two-purportedly-pre-columbian-mexican-crystal-skul-2/): the study addresses technical microscopy, mineral evidence and provenance of British Museum/Smithsonian skulls. Copyrighted article/figures not copied.
2. Smithsonian [NMNH object record](https://www.si.edu/object/nmnhanthropology_8552155), accession 409954, and [2008 museum exhibition](https://www.si.edu/exhibitions/science-news-truth-about-crystal-skulls-event-exhib-4471): first-party search-index records support modern toolmark account; direct automated object retrieval returned **404** (not independently confirmed in normal browser). The object metadata bears CC0 but third-party image reuse was not established. No photograph reproduced.
3. Perucchetti & Dowler, [*The bad side of recycling*](https://onlinelibrary.wiley.com/doi/10.1111/arcm.12738), *Archaeometry*, first published 2021-12-08. Publisher abstract directly examined: authors **hypothesize**, do not conclusively prove, that suspected modern Ithacan coin forgeries used remelted old metal. Do not present as universal diagnostic.
4. British Museum [salt-cellar WB.143](https://wb.britishmuseum.org/MCN3105), indexed institutional description that a dealer assembled an object with old and new parts. Direct check **timeout**; must verify ordinary-browser page before publication.
5. British Museum [ewer WB.75](https://wb.britishmuseum.org/MCN9427), catalog index indicates reattribution from sixteenth to nineteenth century and no firm maker. Direct check **502**; must verify ordinary-browser page before publication.
6. Smithsonian [National Museum of Asian Art provenance method](https://asia-archive.si.edu/collections/provenance-research/): direct institutional page inspected 2026-11-11; documents importance of chain of ownership and its gaps.
7. Smithsonian [Museum Conservation Institute IR/UV imaging](https://mci.si.edu/infrared-and-ultraviolet-imaging): direct institutional page inspected 2026-11-11; techniques reveal alterations and underdrawings, not the whole biography.
8. Smithsonian [Digital Radiography](https://mci.si.edu/digital-radiography): first-party search-index page supports characterization of internal construction; direct check pending.
9. Existing FV [Crystal Skulls investigation](https://finalvestige.com/2026/11/02/crystal-skulls/) directly read, cross-linked as complementary evidence-led case study, not rewritten.

## Media and rights
All original prose, 4-clock CSS infographic, card design and PDF vector layout created for FV on 2026-11-11. The timeline is **explicitly illustrative**, not documentary evidence. No third-party images, scans, museum seals, scholarly figures or embedded media copied. Linked third-party sources retain item-specific copyright/reproduction rights. Diagram alt/accessible label, credits, caption provided.

## QA evidence
- Standalone Chromium via `page.set_content`: 320, 390, 768, 1440 pixel viewports, JavaScript enabled and disabled; 8/8 structural responsive checks passed. No horizontal overflow, 10 references and 12 worksheet inputs present; no uncaught JS errors. 390px test passed invalid javascript: URL rejection, safe JSON roundtrip of markup-shaped user text, and form reset.
- Three-page PDF rendered and visually inspected; page count and textual content verified. Release ZIP generated.
- **Important distinction:** Standalone browser checks do NOT validate the production WordPress theme. WP mshots screenshot *links* for the existing Research Sources page returned ready at four sizes, but actual images still could not be visually inspected by this agent.
- Source access holds: Smithsonian object/press records (404 in automated browser), British Museum object records (timeout/502), and radiography direct recheck; verify by normal browser or replace claims before release.

## Release gate and coordination
Do **not** publish new page or upload media yet. First clear the specific source/rights ambiguities, review actual WordPress-theme screenshots and keyboard/print output, create only a **page** (not a post/newsletter), and confirm first-publish suppresses all email and automatic social sharing. For any post publication, request explicitly `_jetpack_dont_email_post_to_subs=true` and disable publicize as applicable; page tool lacks those keys. Independently read back authenticated page, public URL, document metadata, media links and related Library navigation. Preserve live resources #77 and #1338; the [90-source correction #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) remains a higher production priority. No homepage, Preparedness, or Investigations edits.
