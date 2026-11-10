# Research Sources — controlled release difference register

**Prepared:** 2026-11-10 | **Source readback:** 2026-11-10 13:34 Pacific run (live authenticated API readback) | **Status:** editorial QA; **NOT authorization to publish**
**WordPress sources:** [public #1338](https://finalvestige.com/free-resources/research-sources/) (modified `2026-11-03T22:12:43`); draft #2354 (modified `2026-11-10T12:36:48`).

## Why this record exists
Release decisions need to be based on the exact differences, not the number of previous editorial sessions. This document compares the *current WordPress editable source* of the published 90-source directory with the unpublished 90-source repair. It records every changed card, separates primary destination changes from supporting citations embedded inside descriptions, and states the checks that were not performed.

## Structural invariants

| Test | Published #1338 | Draft #2354 |
|:--|--:|--:|
| Source cards | 90 | 90 |
| Unique titles | 90 | 90 |
| Unique **primary** destinations (final CTA anchor per card) | 90 | 90 |
| Total group headings | 6 | 5 |
| Group card distribution | 9 / 19 / 16 / 11 / 5 / 30 | 12 / 24 / 21 / 25 / 8 |
| HTML/script blocks | 3 | 1 |
| Inline `<script>` elements | 2 | 1 |
| Duplicate HTML IDs | 0 | 0 |
| Unsafe new-tab outbound anchors missing `noopener` | 0 | 0 |

**Crucial qualification:** the public source contains 60 cards in its original five categories **plus 30 in a separate supplemental fallback section**; the 30 are not absent from HTML. They are reorganized with JavaScript. The draft consolidates all 90 cards into the five primary categories in static HTML, removing the dependency on that categorization script. Do not describe the public page as having only 60 raw cards or as definitively hiding 30 from all no-JavaScript readers.

**Correct draft category counts:** declassified 12; accountability 24; engineering 21; archives 25; navigation 8.
**Changed cards:** 47 of 90; **unchanged cards:** 43; **primary destination changes:** 5.

## Changed primary destinations (exact target of each card's final action anchor)

| Card | Public URL | Draft URL |
|:--|:--|:--|
| ADAMS Public Documents | https://www.nrc.gov/reading-rm/adams | https://www.nrc.gov/documents-reports/adams-public-documents |
| Congressional Hearings Collection | https://www.govinfo.gov/help/chrg | https://www.govinfo.gov/app/collection/chrg |
| Three Mile Island Knowledge Management Digest | https://www.nrc.gov/reading-rm/doc-collections/nuregs/knowledge/km0001/r1/index | https://www.nrc.gov/regulations-legislation/nureg-series-publications/publications-prepared-by-nrc-staff-for-knowledge-management/three-mile-island-accident-of-1979-knowledge-management-digest-nuregkm-0001/r1 |
| NTSB CAROL — Case Analysis and Reporting Online | https://www.ntsb.gov/Pages/carol.aspx | https://my.ntsb.gov/ |
| National Archives Donated Collection Explorer | https://www.archives.gov/findingaid/donated-collection-explorer/1000 | https://www.archives.gov/findingaid/donated-collection-explorer |

These are navigational changes only: the existence of a URL is not a full record-access or rights audit. Supporting citations inside descriptions are not the card's primary destination and are not counted as a duplicate.

## Exact change log — all modified cards

### 1. JFK Assassination Records — 2025 Documents Release · card 1/90 · declassified

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Archives · Declassified records · Link-only

The newest JFK release batches, indexed by release date and record identification number, with direct access to the underlying files.

PRIMARY: https://www.archives.gov/research/jfk/release-2025
```
**Staging**
```text
National Archives · Declassified records · Link-only

The National Archives’ 2025 JFK release files are organized by release date and record number. NARA warns that some released files contain personal identifying information about living individuals; do not republish those details.

PRIMARY: https://www.archives.gov/research/jfk/release-2025
```

</details>

### 2. VENONA Documents · card 4/90 · declassified

**Changed fields:** link label / inline markup.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Security Agency · Signals intelligence · Link-only

Declassified Soviet diplomatic and espionage traffic together with the U.S. cryptanalytic record that made portions readable.

PRIMARY: https://www.nsa.gov/serve-from-netstorage/news-features/declassified-documents/venona/index.html
```
**Staging**
```text
National Security Agency · Signals intelligence · Link-only

Declassified Soviet diplomatic and espionage traffic together with the U.S. cryptanalytic record that made portions readable.

PRIMARY: https://www.nsa.gov/serve-from-netstorage/news-features/declassified-documents/venona/index.html
```

</details>

### 3. The Nixon Collection · card 7/90 · declassified

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Central Intelligence Agency · Presidential briefing files · Link-only

Eight intelligence briefing documents prepared for Nixon’s 1972 China trip, including city guides, leadership profiles, and an 82-page atlas.

PRIMARY: https://www.cia.gov/stories/story/the-nixon-collection/
```
**Staging**
```text
Central Intelligence Agency · Presidential briefing files · Link-only

CIA's 2022 overview introduces eight China-trip briefing documents—three city guides, an atlas and four profiles. Follow the collection link on the agency page to reach the underlying records; this destination is the overview, not the files.

PRIMARY: https://www.cia.gov/stories/story/the-nixon-collection/
```

</details>

### 4. President’s Daily Brief — Kennedy and Johnson · card 8/90 · declassified

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Central Intelligence Agency · Presidential intelligence · Link-only

Roughly 2,500 formerly classified presidential intelligence briefs covering 1961–1969, including Cuba, Vietnam, and the Six-Day War.

PRIMARY: https://www.cia.gov/resources/publications/presidents-daily-brief-delivering-intelligence-to-kennedy-and-johnson/
```
**Staging**
```text
Central Intelligence Agency · Presidential intelligence · Link-only

The CIA publication page describes its 40-page explanatory booklet and links to the FOIA reading room for the roughly 2,500 declassified 1961–1969 presidential briefing documents. The booklet is not the source-file collection. Find the underlying records separately in the <a href="https://www.cia.gov/readingroom/" target="_blank" rel="noopener noreferrer">CIA FOIA Reading Room</a>.

PRIMARY: https://www.cia.gov/resources/publications/presidents-daily-brief-delivering-intelligence-to-kennedy-and-johnson/
```

</details>

### 5. GAO High-Risk Series 2025 · card 15/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
GAO · Federal oversight · U.S. government work

GAO’s current map of federal programs and operations vulnerable to waste, fraud, abuse, mismanagement, or major transformation needs.

PRIMARY: https://www.gao.gov/products/gao-25-107743
```
**Staging**
```text
GAO · Federal oversight · U.S. government work

The February 25, 2025 GAO High-Risk Series identifies 38 federal risk areas, including a newly added disaster-assistance area. Its ratings reflect analysis through the 118th Congress; use this as a dated assessment, not a live verdict on actions taken afterward. The GAO High Risk List tracks updates between editions.

PRIMARY: https://www.gao.gov/products/gao-25-107743
```

</details>

### 6. USAspending Advanced Search · card 18/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Treasury · Federal spending · Public data

Prime awards and subawards searchable by recipient, agency, geography, award type, industry code, competition, and fiscal year.

PRIMARY: https://www.usaspending.gov/search
```
**Staging**
```text
U.S. Treasury · Federal spending · Public data

Search federal prime awards and subawards by recipient, agency, place, fiscal year and award type. The Treasury's data disclosures warn of historical duplicate or late subaward reporting, unlinked awards with missing fields and a 90-day delay for some Defense procurement data; apparent gaps are not proof no award exists.

PRIMARY: https://www.usaspending.gov/search
```

</details>

### 7. FOIA.gov — Annual and Quarterly Reports · card 19/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Department of Justice · FOIA performance · Public data

Agency FOIA performance data covering requests received, processed, backlogs, dispositions, and the oldest pending requests.

PRIMARY: https://www.foia.gov/reports.html
```
**Staging**
```text
U.S. Department of Justice · FOIA performance · Public data

Compare agency-level FOIA annual reports with quarterly counts of received, processed and backlogged requests and the status of the ten oldest pending requests. These are summary statistics, not a searchable index of every individual FOIA request. Annual and quarterly measures have different scopes and reporting periods.

PRIMARY: https://www.foia.gov/reports.html
```

</details>

### 8. Fatality Inspection Data · card 21/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
OSHA · Workplace safety · Public data

Federal and State Plan workplace fatality inspections with establishment, victim, inspection, and exportable record fields.

PRIMARY: https://www.osha.gov/fatalities
```
**Staging**
```text
OSHA · Workplace safety · Public data

Federal and State Plan workplace fatality inspections with establishment, victim and exportable data. OSHA updates the display daily but excludes inspections whose opening conferences occurred within the last six months; absence from the table does not prove no incident occurred.

PRIMARY: https://www.osha.gov/fatalities
```

</details>

### 9. ADAMS Public Documents · card 24/90 · accountability

**Changed fields:** annotation, primary destination.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Nuclear Regulatory Commission · Licensing and inspection records · Link-only

The NRC’s public record system for licensing, inspections, enforcement, technical records, and adjudicatory documents.

PRIMARY: https://www.nrc.gov/reading-rm/adams
```
**Staging**
```text
Nuclear Regulatory Commission · Licensing and inspection records · Link-only

Search NRC licensing, inspection, enforcement and technical documents using the agency’s newer <a href="https://www.nrc.gov/documents-reports/adams-public-documents" target="_blank" rel="noopener noreferrer">ADAMS Public Search guidance</a>. The full-text public library principally covers documents released since <strong>November 1, 1999</strong>; older records may be indexed in the legacy library, held on microfiche, or require help from the <a href="https://www.nrc.gov/reading-rm/pdr" target="_blank" rel="noopener noreferrer">Public Document Room</a>. A search gap does not establish that no NRC record exists.

PRIMARY: https://www.nrc.gov/documents-reports/adams-public-documents
```

</details>

### 10. EDGAR — SEC Search Filings · card 27/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Securities and Exchange Commission · Corporate filings · Link-only

Millions of first-party securities filings, ownership forms, issuer correspondence, full-text search, and APIs.

PRIMARY: https://www.sec.gov/search-filings
```
**Staging**
```text
Securities and Exchange Commission · Corporate filings · Link-only

Search first-party securities filings, ownership forms and issuer correspondence. SEC EDGAR indexes begin in 1994/95, refresh on a schedule, and can be corrected or rebuilt after acceptance. Some older or paper filings are not in ordinary EDGAR search; distinguish filing date from the reporting period.

PRIMARY: https://www.sec.gov/search-filings
```

</details>

### 11. Open Payments Data · card 29/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Centers for Medicare &amp; Medicaid Services · Financial disclosures · Public data

Searchable and downloadable manufacturer and purchasing-organization payments to covered healthcare recipients, with methodology and dispute context.

PRIMARY: https://www.cms.gov/priorities/key-initiatives/open-payments/data
```
**Staging**
```text
Centers for Medicare &amp; Medicaid Services · Financial disclosures · Public data

Search manufacturer and purchasing-organization payments to covered healthcare recipients. CMS publishes reporting-entity submissions annually after a review/dispute period; a disclosed payment is not, by itself, a finding of misconduct or an improper relationship.

PRIMARY: https://www.cms.gov/priorities/key-initiatives/open-payments/data
```

</details>

### 12. FederalRegister.gov · card 31/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Office of the Federal Register / GPO · Rules and notices · Link-only

More than a million searchable rules, proposed rules, notices, and presidential documents, each tied to the official GovInfo edition.

PRIMARY: https://www.federalregister.gov/
```
**Staging**
```text
Office of the Federal Register / GPO · Rules and notices · Link-only

Searchable rules, proposed rules, notices and presidential documents. FederalRegister.gov's HTML/XML view is informational, not the official legal edition; for legal reliance, check the linked official PDF on <a href="https://www.govinfo.gov/app/collection/fr" target="_blank" rel="noopener noreferrer">GovInfo</a>. The Office of the Federal Register explains that distinction.

PRIMARY: https://www.federalregister.gov/
```

</details>

### 13. Office of Legal Counsel Opinions · card 32/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Department of Justice · Executive legal opinions · U.S. government work

Published OLC opinions preserving the executive branch’s legal reasoning on presidential authority, appointments, privilege, agency powers, and related questions.

PRIMARY: https://www.justice.gov/olc/opinions
```
**Staging**
```text
U.S. Department of Justice · Executive legal opinions · U.S. government work

The public OLC opinions page is a selected publication record, not a complete register of every opinion the Office has given. Distinguish an opinion’s signature/issuance date from its later addition to the website; official bound volumes, individually posted opinions and the electronic reading room have different publication status.

PRIMARY: https://www.justice.gov/olc/opinions
```

</details>

### 14. Congressional Hearings Collection · card 34/90 · accountability

**Changed fields:** annotation, primary destination.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
GovInfo · Congressional oversight · Link-only collection

Published hearing volumes preserving witness testimony, committee questions, exhibits, appendices, and supporting material where Congress has made a hearing available.

PRIMARY: https://www.govinfo.gov/help/chrg
```
**Staging**
```text
GovInfo · Congressional oversight · Link-only collection

Browse published hearing volumes, testimony and exhibits when made available to GovInfo; not every hearing is included, and some appear long after the session. GovInfo's official coverage and search guide explains the gaps.

PRIMARY: https://www.govinfo.gov/app/collection/chrg
```

</details>

### 15. Federal Audit Clearinghouse · card 35/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
General Services Administration · Single Audits · Public data

Search Single Audit submissions, federal awards, findings, questioned costs, corrective-action information, and underlying audit-report packages.

PRIMARY: https://www.fac.gov/
```
**Staging**
```text
General Services Administration · Single Audits · Public data

Search submitted Single Audit packages, federal award findings and questioned costs, with CSV/API access. Coverage follows audit eligibility: generally at least $750,000 of federal awards expended for fiscal years beginning before October 1, 2024, and $1 million for fiscal years beginning on/after that date; it is not a census of every grant recipient.

PRIMARY: https://www.fac.gov/
```

</details>

### 16. RECAP Archive / CourtListener · card 36/90 · accountability

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Free Law Project · Federal court records · Link-only

A free legal-research route into federal dockets and PACER documents contributed to the RECAP archive, with coverage determined by what has entered the collection.

PRIMARY: https://www.courtlistener.com/recap/
```
**Staging**
```text
Free Law Project · Federal court records · Link-only

Search federal court dockets and PACER documents available in the Free Law Project's RECAP Archive. Much of the collection comes from PACER purchases contributed by users; a missing filing in RECAP does not establish that the court never filed or maintained it. Verify a consequential absence against the court's own docket.

PRIMARY: https://www.courtlistener.com/recap/
```

</details>

### 17. Event Footprint Catalog · card 45/90 · engineering

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NOAA NCEI · Severe-weather evidence · Public data

High-resolution tornado and hail footprints with event narratives, metadata, and downloadable geospatial data.

PRIMARY: https://www.ncei.noaa.gov/products/event-footprint-catalog
```
**Staging**
```text
NOAA NCEI · Severe-weather evidence · Public data

High-resolution tornado and hail footprints with event narratives and geospatial downloads, not an inventory of every hazard. NOAA lists tornado coverage from January 2010 and hail from October 2020; cloud migration may delay downloads, and prior dataset versions are not retained. Research outputs are not certified records.

PRIMARY: https://www.ncei.noaa.gov/products/event-footprint-catalog
```

</details>

### 18. NIOSH FACE Reports · card 47/90 · engineering

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NIOSH / State FACE Programs · Occupational fatalities · Link-only collection

Worksite-level investigations of fatal occupational incidents with prevention recommendations and concrete failure chains.

PRIMARY: https://www.cdc.gov/niosh/face/topics/index.html
```
**Staging**
```text
NIOSH / State FACE Programs · Occupational fatalities · Link-only collection

Worksite-level fatality investigations with prevention recommendations. NIOSH routes reports through 2015 to CDC Stacks; State FACE reports from 2016 onward appear on this page. Search both eras before concluding a report is missing.

PRIMARY: https://www.cdc.gov/niosh/face/topics/index.html
```

</details>

### 19. America Burning · card 49/90 · engineering

**Changed fields:** source/rights label, annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
USFA · National fire policy · U.S. government work

The 1973 national fire-policy report that treated fire loss as a systems problem and helped drive creation of the U.S. Fire Administration.

PRIMARY: https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf
```
**Staging**
```text
USFA · National fire policy · Text reusable; photographs require permission

The 1973 national fire-policy report traces fire loss, building design, prevention and public policy. The scanned edition also contains a <strong>September 1989 U.S. Fire Administration information update</strong> revising several original loss estimates. Cite the two periods separately: those figures are not interchangeable or current fire statistics. Its explicit reuse notice permits republication of the report but <strong>excludes photographs without their owners’ permission</strong>.

PRIMARY: https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf
```

</details>

### 20. FEMA 549 — Hurricane Katrina Building Performance · card 50/90 · engineering

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
FEMA / GovInfo · Building performance · U.S. government work

A field investigation of Gulf Coast building performance under wind, flood, and surge, with observations, recommendations, and technical mitigation guidance.

PRIMARY: https://www.govinfo.gov/app/details/GOVPUB-HS5_100-PURL-LPS81562
```
**Staging**
```text
FEMA / GovInfo · Building performance · U.S. government work

FEMA's post-Katrina building-performance investigation covers wind, flood and surge damage and mitigation recommendations. The GovInfo PDF is approximately 254.8 MB; use the detail page to assess file size before downloading on mobile.

PRIMARY: https://www.govinfo.gov/app/details/GOVPUB-HS5_100-PURL-LPS81562
```

</details>

### 21. Three Mile Island Knowledge Management Digest · card 52/90 · engineering

**Changed fields:** annotation, primary destination.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Nuclear Regulatory Commission · Nuclear accident archive · U.S. government work

A curated gateway to the technical, regulatory, cleanup, training, human-factors, and emergency-planning record generated by Three Mile Island.

PRIMARY: https://www.nrc.gov/reading-rm/doc-collections/nuregs/knowledge/km0001/r1/index
```
**Staging**
```text
Nuclear Regulatory Commission · Nuclear accident archive · U.S. government work

Start with the NRC’s June 2016 Revision 1 overview of the 1979 accident, then follow its linked cleanup supplements. The supporting documents and multimedia database was also distributed by DVD; the NRC says historical material in that DVD collection is reference material rather than official NRC records. Not every cited record is necessarily downloadable here.

PRIMARY: https://www.nrc.gov/regulations-legislation/nureg-series-publications/publications-prepared-by-nrc-staff-for-knowledge-management/three-mile-island-accident-of-1979-knowledge-management-digest-nuregkm-0001/r1
```

</details>

### 22. NIST Disaster and Failure Studies Data Archive · card 53/90 · engineering

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NIST · Disaster and failure evidence · Link-only

Photographs, video, simulations, reports, and other evidence behind major NIST disaster and failure studies, with item-level rights varying across contributed material.

PRIMARY: https://www.nist.gov/disaster-failure-studies/data-archive
```
**Staging**
```text
NIST · Disaster and failure evidence · Link-only

NIST preserves WTC investigation photographs, simulations and reports, among other disaster records; some contributed items retain third-party copyright. As checked November 10, 2026, NIST explicitly marks its 2010 Chile earthquake dataset site unavailable for maintenance.

PRIMARY: https://www.nist.gov/disaster-failure-studies/data-archive
```

</details>

### 23. NTSB CAROL — Case Analysis and Reporting Online · card 54/90 · engineering

**Changed fields:** annotation, primary destination.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Transportation Safety Board · Investigation search · U.S. government work

Cross-mode search for transportation investigations, reports, recommendations, and available dockets, including aviation records reaching back to 1962.

PRIMARY: https://www.ntsb.gov/Pages/carol.aspx
```
**Staging**
```text
National Transportation Safety Board · Investigation search · U.S. government work

Search NTSB investigation and safety-recommendation records through CAROL. The agency’s <a href="https://www.ntsb.gov/Pages/carol.aspx" target="_blank" rel="noopener noreferrer">coverage guide</a> states that aviation investigations extend back to 1962, while other transport modes generally begin in 2010. Those are CAROL search-system ranges, <strong>not</strong> the dates of every surviving investigation. For underlying supporting exhibits, also consult the <a href="https://data.ntsb.gov/Docket/Forms/searchdocket" target="_blank" rel="noopener noreferrer">separate docket search</a>.

PRIMARY: https://my.ntsb.gov/
```

</details>

### 24. National Hurricane Center Data Archive · card 56/90 · engineering

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NOAA National Hurricane Center · Storm records and data · U.S. government work

Operational advisories, Tropical Cyclone Reports, HURDAT2 best tracks, GIS files, reconnaissance data, storm wallets, and forecast-verification records.

PRIMARY: https://www.nhc.noaa.gov/data/
```
**Staging**
```text
NOAA National Hurricane Center · Storm records and data · U.S. government work

NHC provides operational advisories and later best-track datasets, including HURDAT2. Best tracks are retrospective and can change after reanalysis: the Atlantic HURDAT2 archive notes a September 23, 2026 update revising 1971–1975 seasons; the Pacific archive notes a September 29, 2026 change to 1971 Olivia. Preserve the dataset version before comparing with forecasts issued during a storm.

PRIMARY: https://www.nhc.noaa.gov/data/
```

</details>

### 25. HABS / HAER / HALS · card 59/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Library of Congress / National Park Service · Built environment · Link-only collection

More than half a million measured drawings, large-format photographs, and written histories of American buildings, engineering works, and landscapes.

PRIMARY: https://www.loc.gov/pictures/collection/hh/
```
**Staging**
```text
Library of Congress / National Park Service · Built environment · Link-only collection

More than 581,000 drawings, photographs and written histories document over 43,000 historic structures and sites. Examine the individual item record and its Rights Advisory before reuse: federal survey images often carry no known restrictions, but copies of photographs or drawings from other sources can remain restricted.

PRIMARY: https://www.loc.gov/pictures/collection/hh/
```

</details>

### 26. topoView — Historical Topographic Map Collection · card 60/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Geological Survey · Historical maps · U.S. government work

Historical USGS map editions for comparing roads, rail lines, settlements, reservoirs, mines, coastlines, and place names across time.

PRIMARY: https://www.usgs.gov/tools/topoview
```
**Staging**
```text
U.S. Geological Survey · Historical maps · U.S. government work

topoView includes the scanned Historical Topographic Map Collection (printed editions 1884–2006) alongside newer US Topo products. Record the specific map sheet, scale, publication or revision year and download format; do not treat a modern US Topo layer as the exact map a historical observer carried.

PRIMARY: https://www.usgs.gov/tools/topoview
```

</details>

### 27. Chronicling America · card 61/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Library of Congress / NEH · Historic newspapers · Mixed rights by item

Millions of searchable historic newspaper pages for recovering local reporting, public notices, disasters, court proceedings, and community response.

PRIMARY: https://www.loc.gov/collections/chronicling-america/about-this-collection/
```
**Staging**
```text
Library of Congress / NEH · Historic newspapers · Mixed rights by item

Search historic newspapers, local notices and contemporary accounts. The Library of Congress believes these pages are public domain or carry no known restrictions, but warns that pages from the last 95 years may contain protected third-party content. Check the <a href="https://www.loc.gov/collections/chronicling-america/about-this-collection/rights-and-access/" target="_blank" rel="noopener noreferrer">collection rights note</a> before reproducing material.

PRIMARY: https://www.loc.gov/collections/chronicling-america/about-this-collection/
```

</details>

### 28. Apollo Lunar Surface Journal &amp;amp; Apollo Flight Journal · card 63/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NASA History / volunteer editors · Annotated Apollo archive · Link-only

Corrected Apollo transcripts layered with astronaut commentary, photographs, maps, documents, audio, and video.

PRIMARY: https://www.nasa.gov/history/alsj-and-afj/
```
**Staging**
```text
NASA History / volunteer editors · Annotated Apollo archive · Link-only

Read the <strong>Apollo Lunar Surface Journal</strong> and <strong>Apollo Flight Journal</strong> as edited research editions: transcripts are aligned with later astronaut commentary, photos, maps, audio and video. Their explanatory annotations and corrections are not themselves contemporaneous mission transmissions. When a disputed quotation matters, identify the mission, time, editorial layer and underlying recording or original transcript.

PRIMARY: https://www.nasa.gov/history/alsj-and-afj/
```

</details>

### 29. OSTI.GOV · card 64/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Department of Energy · Technical research · Link-only repository

More than 75 years of technical reports, datasets, software, patents, conference papers, books, theses, and other DOE research records.

PRIMARY: https://www.osti.gov/
```
**Staging**
```text
U.S. Department of Energy · Technical research · Link-only repository

Search DOE-funded scientific and technical records across reports, datasets, software, patents, papers and other research outputs. If the search interface is unavailable, use DOE OSTI’s <a href="https://www.osti.gov/search-tools" target="_blank" rel="noopener noreferrer">official search-tools directory</a> to identify specialized collections such as DOE PAGES. A catalog hit establishes a record, not that full text or reuse rights are available for every item.

PRIMARY: https://www.osti.gov/
```

</details>

### 30. Smithsonian Open Access · card 66/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Smithsonian Institution · Museum open access · CC0 where marked

Millions of museum, archive, scientific, 2D, and 3D assets, with explicit CC0 reuse on designated items.

PRIMARY: https://www.si.edu/openaccess
```
**Staging**
```text
Smithsonian Institution · Museum open access · CC0 where marked

Museum collections, scientific records and 2D/3D media. Only individual assets marked <strong>CC0</strong> are cleared under Smithsonian Open Access; other material can be restricted by copyright, donor agreements, ownership or cultural sensitivity. Verify the item mark and <a href="https://www.si.edu/openaccess/faq" target="_blank" rel="noopener noreferrer">program FAQ</a> before reuse.

PRIMARY: https://www.si.edu/openaccess
```

</details>

### 31. Sanborn Maps Collection · card 67/90 · archives

**Changed fields:** source/rights label, annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Library of Congress · Historical maps · Public domain collection

Fire-insurance maps encoding building footprints, construction, uses, streets, industrial properties, and fire-protection infrastructure block by block.

PRIMARY: https://www.loc.gov/collections/sanborn-maps/about-this-collection/
```
**Staging**
```text
Library of Congress · Historical maps · Online collection public domain

Fire-insurance sheets document building footprint and use, but one physical atlas may contain a printed edition plus decades of paste-on corrections. LOC explains that the correction record and latest pasted material may have different dates, and individual pasted changes often cannot be dated. Treat a printed year as the map edition, not a construction date for every depicted building.

PRIMARY: https://www.loc.gov/collections/sanborn-maps/about-this-collection/
```

</details>

### 32. National Archives Catalog · card 68/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Archives · Federal records · Link-only catalog

The broadest first-party gateway into NARA holdings, combining archival hierarchy, descriptions, digitized records, and searchable OCR.

PRIMARY: https://catalog.archives.gov/
```
**Staging**
```text
National Archives · Federal records · Link-only catalog

The first-party gateway into NARA holdings, including collection/series descriptions, digital objects and OCR. Over 95% of holdings are described at series level; most descriptions do not name every individual, and many records are not online. A failed name or online-only search cannot rule out an existing record.

PRIMARY: https://catalog.archives.gov/
```

</details>

### 33. USGS EarthExplorer · card 71/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Geological Survey · Remote sensing · Link-only portal

Search satellite imagery, historical aerial photography, elevation products, and declassified remote-sensing collections by place and date; downloads can require a free account.

PRIMARY: https://earthexplorer.usgs.gov/
```
**Staging**
```text
U.S. Geological Survey · Remote sensing · Link-only portal

Find satellite imagery, historical aerial photographs, elevation products and declassified remote sensing by place and date. Some downloads or bulk-export functions require a free USGS login; the map baselayers are reference layers, not necessarily downloadable imagery. Follow each dataset's metadata and access terms.

PRIMARY: https://earthexplorer.usgs.gov/
```

</details>

### 34. NOAA Historical Hurricane Tracks · card 73/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NOAA Office for Coastal Management · Storm geography · Link-only portal

A map-first viewer for more than 13,000 historical tropical-cyclone tracks, useful for finding storms by place before moving into deeper advisory and report records.

PRIMARY: https://coast.noaa.gov/hurricanes/
```
**Staging**
```text
NOAA Office for Coastal Management · Storm geography · Link-only portal

Map and search more than 13,000 historical storm tracks using NHC HURDAT2 and IBTrACS. A search that returns no nearby storm may reflect the tool’s search-radius setting, not absence of regional impacts: NOAA notes Hurricane Harvey missed a 60-mile Houston query despite its catastrophic flooding. A track line is not an impact footprint.

PRIMARY: https://coast.noaa.gov/hurricanes/
```

</details>

### 35. Railroad Maps, 1828–1900 · card 74/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Library of Congress · Railroad cartography · Link-only collection

A digitized collection of 623 railroad maps including government surveys, land-grant maps, rights-of-way, progress maps, and route depictions.

PRIMARY: https://www.loc.gov/collections/railroad-maps-1828-to-1900/about-this-collection/
```
**Staging**
```text
Library of Congress · Railroad cartography · Link-only collection

The Library of Congress presents <strong>623 selected maps</strong>, not a complete inventory of its thousands of railroad-related maps. Survey and right-of-way maps can document proposals and projected routes; commercial/promotional maps sometimes depicted lines <strong>never built</strong>. Corroborate a purported working railroad with target-date timetables, reports and independent local records.

PRIMARY: https://www.loc.gov/collections/railroad-maps-1828-to-1900/about-this-collection/
```

</details>

### 36. Digital Public Library of America · card 75/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Digital Public Library of America · Cross-institution discovery · Link-only

A national discovery layer across libraries, archives, museums, and cultural institutions, leading back to source institutions for item metadata and rights.

PRIMARY: https://dp.la/
```
**Staging**
```text
Digital Public Library of America · Cross-institution discovery · Link-only

Search across libraries, museums and archives, then follow each result to its contributing institution and item record. A DPLA search result is not permission to reproduce: review its <a href="https://dp.la/about/rights-categories" target="_blank" rel="noopener noreferrer">rights category</a> and the item's actual license, including attribution, noncommercial or no-derivatives terms.

PRIMARY: https://dp.la/
```

</details>

### 37. David Rumsey Map Collection · card 76/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
David Rumsey Map Collection · Historical maps · Link-only

About 150,000 historical map images with high-resolution viewing, geographic search, comparison, and georeferencing tools.

PRIMARY: https://www.davidrumsey.com/
```
**Staging**
```text
David Rumsey Map Collection · Historical maps · Link-only

Historic maps with high-resolution viewing, search and georeferencing tools. The collection permits many kinds of publication reuse, but later maps may still have third-party copyright; items without a download button are display-only absent further permission. Credit the collection and inspect its <a href="https://www.davidrumsey.com/about/copyright-and-permissions" target="_blank" rel="noopener noreferrer">copyright and permissions guidance</a>.

PRIMARY: https://www.davidrumsey.com/
```

</details>

### 38. National Register of Historic Places — Database and Research · card 77/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Park Service · Historic places · Link-only collection

Research routes into nomination files, photographs, maps, downloadable data, and GIS for more than 95,000 listed properties and districts.

PRIMARY: https://www.nps.gov/subjects/nationalregister/database-research.htm
```
**Staging**
```text
National Park Service · Historic places · Link-only collection

Search the NPS listing spreadsheet, GIS data and nomination files for more than 95,000 listed properties. NARA holds National Register records through 2012; some files listed since 2013 are in NPS NPGallery. Not every file is online: NPS accepts document requests and withholds restricted files. A missing downloadable nomination is not proof a property was never listed; rights in photographs and contributed material require item-level review.

PRIMARY: https://www.nps.gov/subjects/nationalregister/database-research.htm
```

</details>

### 39. Veterans History Project Collection · card 78/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Library of Congress · Oral history and personal records · Link-only

First-person military-service accounts with interviews, letters, diaries, photographs, and memoirs; recollection remains distinct from independently corroborated fact.

PRIMARY: https://www.loc.gov/collections/veterans-history-project-collection/
```
**Staging**
```text
Library of Congress · Oral history and personal records · Link-only

First-person veteran interviews, diaries, letters and photographs. A catalog description does not mean the item has been digitized; some collections require an onsite appointment. Contributors retain rights and publication or exhibition use generally requires permission: see the <a href="https://www.loc.gov/collections/veterans-history-project-collection/about-this-collection/rights-and-access/" target="_blank" rel="noopener noreferrer">Library's rights guidance</a>. Treat recollection as testimony, not independent corroboration.

PRIMARY: https://www.loc.gov/collections/veterans-history-project-collection/
```

</details>

### 40. CyberCemetery · card 79/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
UNT Libraries / GovInfo · Government web preservation · Link-only

Archived websites from defunct federal agencies, commissions, and temporary government bodies, preserving reports and source material that can disappear from the current web.

PRIMARY: https://govinfo.library.unt.edu/
```
**Staging**
```text
UNT Libraries / GovInfo · Government web preservation · Link-only

UNT Libraries' CyberCemetery preserves websites of defunct U.S. agencies, commissions and temporary bodies. A captured site is evidence of an archived presentation, not proof that every dynamic database entry, external link or submission form survives. UNT warns that archived <strong>forms, search boxes and external links may not function</strong>; document the capture date and check extracted publications or the originating institution when possible.

PRIMARY: https://govinfo.library.unt.edu/
```

</details>

### 41. National Archives Record Group Explorer · card 81/90 · archives

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Archives · Federal record groups · Link-only

A record-group discovery tool that makes digitization gaps visible: NARA’s June 2026 baseline reports 475,127,595 scans, about 3.87% of estimated textual holdings represented there.

PRIMARY: https://www.archives.gov/findingaid/record-group-explorer
```
**Staging**
```text
National Archives · Federal record groups · Link-only

A federal record-group discovery tool, not a complete count of all archival material: NARA estimated 503,600,456 scans online, representing 4.04% of its estimated textual pages as of October 2026. The estimate uses textual record volume and is updated monthly.

PRIMARY: https://www.archives.gov/findingaid/record-group-explorer
```

</details>

### 42. National Archives Donated Collection Explorer · card 82/90 · archives

**Changed fields:** annotation, primary destination.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
National Archives · Donated collections · Link-only

A companion discovery layer for donated papers and non-record-group holdings, with scan coverage that helps distinguish “not digitized” from “not held.”

PRIMARY: https://www.archives.gov/findingaid/donated-collection-explorer/1000
```
**Staging**
```text
National Archives · Donated collections · Link-only

Browse donated collections separately from federal record groups. NARA's October 2026 snapshot lists <strong>1,175,630 online scans</strong>, about <strong>4.62%</strong> of an estimated 25,447,250 donated-collection textual pages. This is an estimated <em>textual-page</em> coverage measure, not a complete inventory or proof that an unlisted record is not held.

PRIMARY: https://www.archives.gov/findingaid/donated-collection-explorer
```

</details>

### 43. International Ice Patrol Annual Reports · card 84/90 · navigation

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Coast Guard · North Atlantic ice · U.S. government work

More than a century of annual North Atlantic iceberg-condition and Ice Patrol operational reports, reaching back to 1913.

PRIMARY: https://www.navcen.uscg.gov/international-ice-patrol-annual-reports
```
**Staging**
```text
U.S. Coast Guard · North Atlantic ice · U.S. government work

North Atlantic iceberg conditions and Ice Patrol operations documented in annual reports back to 1913. The Coast Guard lists reports for 2000 onward as individual PDFs; many earlier years are packaged in decade ZIP archives. Record the individual report year and inspect its contents before treating a decade bundle as complete.

PRIMARY: https://www.navcen.uscg.gov/international-ice-patrol-annual-reports
```

</details>

### 44. United States Coast Pilot · card 85/90 · navigation

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
NOAA Office of Coast Survey · Nautical reference · U.S. government work

Ten free volumes covering channels, anchorages, bridge clearances, currents, tides, weather, ice, wharves, hazards, routes, and navigation regulations.

PRIMARY: https://nauticalcharts.noaa.gov/publications/coast-pilot/
```
**Staging**
```text
NOAA Office of Coast Survey · Nautical reference · U.S. government work

Ten volumes of coastal and Great Lakes sailing directions covering channels, bridge clearances, currents, hazards, facilities and navigation regulations. NOAA updates these volumes <strong>weekly</strong>; preserve the exact downloaded edition and update date before treating a paragraph as a historical witness. For operational use, consult the newest official volume and applicable notices rather than an old saved PDF.

PRIMARY: https://nauticalcharts.noaa.gov/publications/coast-pilot/
```

</details>

### 45. Navigation Rules and Regulations Handbook · card 86/90 · navigation

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Coast Guard · Rules of the Road · U.S. government work

The official International and Inland Rules of the Road, annexes, radio rules, and vessel-traffic regulations in one free handbook.

PRIMARY: https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/Handbook/Nav%20Rules%20Handbook_Corrected_08-12-2024.pdf
```
**Staging**
```text
U.S. Coast Guard · Rules of the Road · U.S. government work

The USCG's <strong>August 2024 corrected edition</strong> of the International and Inland Navigation Rules, annexes and associated regulations. Valuable as a dated legal/technical reference, but the linked PDF is not proof of what rules applied on a different historical date—or what amendments govern today. For current text, consult the <a href="https://www.navcen.uscg.gov/navigation-rules-amalgamated" target="_blank" rel="noopener noreferrer">Coast Guard's rules portal</a> and controlling regulations.

PRIMARY: https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/Handbook/Nav%20Rules%20Handbook_Corrected_08-12-2024.pdf
```

</details>

### 46. U.S. Coast Guard Light List · card 89/90 · navigation

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
U.S. Coast Guard · Aids to navigation · U.S. government work

Annual regional lists of lights, sound signals, buoys, daybeacons, and other aids to navigation, with current weekly correction files.

PRIMARY: https://www.navcen.uscg.gov/light-list-annual-publication
```
**Staging**
```text
U.S. Coast Guard · Aids to navigation · U.S. government work

Annual regional descriptions of lights, sound signals, buoys, daybeacons and other aids to navigation. The annual volumes are a snapshot, <strong>not</strong> a complete present-day operating picture: the Coast Guard issues weekly corrections and directs readers to <a href="https://navcen.uscg.gov/weekly-light-lists" target="_blank" rel="noopener noreferrer">weekly Light Lists</a> and the <a href="https://navcen.uscg.gov/msi" target="_blank" rel="noopener noreferrer">MSI Products service</a>. For history, record the volume, edition and correction week.

PRIMARY: https://www.navcen.uscg.gov/light-list-annual-publication
```

</details>

### 47. Aeronautical Information Manual · card 90/90 · navigation

**Changed fields:** annotation.

<details><summary>Previous card text and new card text</summary>

**Before**
```text
Federal Aviation Administration · Aviation operations · U.S. government work

The FAA’s operating reference for the national airspace system, navigation, air-traffic procedures, airport operations, communications, emergencies, and safety information.

PRIMARY: https://www.faa.gov/air_traffic/publications/atpubs/aim_html/
```
**Staging**
```text
Federal Aviation Administration · Aviation operations · U.S. government work

The FAA's handbook of basic U.S. flight information and air-traffic procedures, published as dated basic editions and changes. The version checked on <strong>November 10, 2026</strong> is <strong>Change 3, effective July 9, 2026</strong>; read its effective-date and change notices before citing. It is not a complete substitute for time-specific charts, supplements, notices or regulations.

PRIMARY: https://www.faa.gov/air_traffic/publications/atpubs/aim_html/
```

</details>

## Source provenance, rights, and honest limits
- This is a *structural editorial-difference audit* of the authenticated WordPress page source, not a reproduction-license grant. No third-party imagery or source scans were copied into this report. The original cards contain link-out references; owning institutions govern object-level rights.
- Full 90-source provenance and the last-checked state of each destination are recorded in [`research-sources-90-provenance-ledger-2026-11-10.csv`](./research-sources-90-provenance-ledger-2026-11-10.csv). That ledger describes **63 directly readable, one cached, and 26 inconclusive** institutional destinations on Nov 10. Inconclusive bot/app access is not proof of a broken visitor link.
- A primary card link can be an institutional publication, guidance page, downloadable PDF or search portal. Even direct retrieval does not establish every search result is public, current, full-text or licensed for republication.
- The CIA Kennedy/Johnson card's principal destination remains the CIA **2015 publication/booklet** page; the embedded FOIA Reading Room link is a **separate supporting route**, not an accidental second primary destination. The booklet is **not** the nearly 2,500-document collection. See [CIA publication](https://www.cia.gov/resources/publications/presidents-daily-brief-delivering-intelligence-to-kennedy-and-johnson/).

## Release gate — currently HOLD
1. Confirm exactly the same public and draft modified times/hashes immediately before any promotion or guarded block write; rerun the 90-title, 90-primary-URL, correct category and no-lost-link comparisons after any edit.
2. Independently inspect actual site-theme rendering with **image pixels**, not just mshots URLs, at **320, 390, 768, 1440px**; record screenshots, keyboard focus, zoom, no-JavaScript navigation, active search/filter, counts and horizontal overflow.
3. Use an ordinary browser to resolve the 26 access-inconclusive destinations or explicitly retain the reviewed exceptions with warnings; verify priority links, internal crosslinks, canonical, metadata and downloads anonymously.
4. Verify page-specific notification and Publicize suppression. WordPress newsletter configuration was observed **email_new_posts_by_default=false** on Nov 10, but this is not a substitute for explicit first-publish controls; no first publication is part of this release (existing #1338 is already live).
5. Publish **only** by applying scoped changes to existing page **#1338**, retaining URL, layout, related-reading blocks and assets; **never publish #2354 as a duplicate directory**. Make the Library landing-page 60→90 factual count correction in a separate scoped edit after the directory release.
6. Read back the updated original page and independently check its public URL and browser rendering. Open the GitHub QA ticket with actual PASS/FAIL evidence. No emails, social publishing or spending.

## Coordination
- [Research Sources issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788)
- [Shared visual QA blocker #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589)
- [Editorial standards](https://finalvestige.com/editorial-standards/)
- [Library](https://finalvestige.com/free-resources/)

**Original work:** Final Vestige Studios editorial change register and verification method; no institutional images or scans copied.