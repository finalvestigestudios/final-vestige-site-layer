# Final Vestige Library — Research Sources destination-verification audit

**Date:** November 16, 2026 (Pacific)  
**Owner:** LIBRARY editorial integrity only  
**Targets:** [published Research Sources #1338](https://finalvestige.com/free-resources/research-sources/), [Library landing page](https://finalvestige.com/free-resources/), [Editorial Standards](https://finalvestige.com/editorial-standards/)  
**State:** LINK AUDIT COMPLETE FOR 50/90; WORDPRESS CORRECTION STILL ON RELEASE HOLD

## What this new work establishes

Starting from the original authenticated 90-card, 90-unique-URL WordPress inventory, this audit attempted **45 additional exact institutional destination URLs**. Five were already checked in the earlier QA pass, for **50/90 examined** without altering any source URL, title, category or rights cue. This was a public textual retrieval, **not** an interactive browser session or item-level license determination.

| Classification | Count | Precise meaning |
|---|---:|---|
| Institutional content observed | 36 | Destination returned identifiable original institution content, including 4 from the first pass; no guarantee of downstream documents |
| Application shell only | 2 | USAspending and National Archives Catalog responded, but dynamic UI/search not validated |
| Automated access restricted | 11 | HTTP 403/406 or restricted automated fetch; **do not call broken links** |
| Timeout unresolved | 1 | NASA NTRS citation request did not complete |
| Not yet checked | 40 | Presence in the WordPress source inventory only |

## Selected evidence that changes how a reader should use a source

- **NARA JFK 2025 release (#1):** NARA's own page explicitly warns that some files contain personal identifiers of living people. Do not mirror or quote private identifiers merely because a release is public. [Institutional page](https://www.archives.gov/research/jfk/release-2025).
- **OSHA fatality inspection data (#18):** The page says updates are daily but newly opened inspections are delayed by six months, so it cannot answer an exhaustive recent-fatality question. [Official dataset](https://www.osha.gov/fatalities).
- **FederalRegister.gov (#28):** The site says its prototype HTML is **not the official legal edition**. Consult the controlling edition on GovInfo when the exact legal text matters. [Federal Register](https://www.federalregister.gov/).
- **USFA _America Burning_ (#41):** The PDF's rights note permits broad report use **except photographs**, which need separate owner permission. Link only; no photographic reuse here. [Official PDF](https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf).
- **NTSB CAROL (#70):** NTSB describes aviation data extending to 1962 and other-mode datasets from 2010, with different coverage limits. Do not use one database miss as proof an older accident was never investigated. [CAROL help](https://www.ntsb.gov/Pages/carol.aspx).
- **National Register (#85):** NPS distinguishes NARA files, post-2012 files and not-yet-digitized requests; some files are restricted. Search by exact reference number or custodial route. [NPS research guidance](https://www.nps.gov/subjects/nationalregister/database-research.htm).
- **NARA donated-collection Explorer (#90):** Its estimated scan/page denominator applies to donated collections, not the federal Record Group Explorer. Do not combine the statistics. [NARA](https://www.archives.gov/findingaid/donated-collection-explorer/1000).

## Per-URL result for all 50 investigated destinations

| # | Source | Retrieval result | Notes |
|---:|---|---|---|
| 1 | [JFK Assassination Records — 2025 Documents Release](https://www.archives.gov/research/jfk/release-2025) | Institutional page body observed | NARA release page explicitly warns some 2025 JFK files contain living persons' personal identifiers; do not rehost private data. |
| 2 | [Pentagon Papers](https://www.archives.gov/research/pentagon-papers) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 3 | [COINTELPRO](https://vault.fbi.gov/cointel-pro/cointel-pro) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 4 | [VENONA Documents](https://www.nsa.gov/serve-from-netstorage/news-features/declassified-documents/venona/index.html) | Previously observed institutional content | Landing/entry only; rights assessed per record |
| 5 | [FRUS: Iran, 1951–1954, Second Edition](https://history.state.gov/historicaldocuments/frus1951-54IranEd2) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 6 | [FRUS: Guatemala, 1952–1954](https://history.state.gov/historicaldocuments/frus1952-54Guat) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 7 | [The Nixon Collection](https://www.cia.gov/stories/story/the-nixon-collection/) | Previously observed institutional content | Landing/entry only; rights assessed per record |
| 9 | [FRUS: Cuban Missile Crisis and Aftermath](https://history.state.gov/historicaldocuments/frus1961-63v11) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 10 | [Watergate Road Map](https://www.archives.gov/research/investigations/watergate/roadmap) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 12 | [GAO High-Risk Series 2025](https://www.gao.gov/products/gao-25-107743) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 14 | [Campaign Finance Data](https://www.fec.gov/data/) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 15 | [USAspending Advanced Search](https://www.usaspending.gov/search) | Application shell only | USAspending JavaScript application returned a shell only; search, data delivery and download not independently exercised. |
| 16 | [FOIA.gov — Annual and Quarterly Reports](https://www.foia.gov/reports.html) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 17 | [Lobbying Disclosure Act Reports](https://lda.gov/system/public/) | Automated access restricted | Lobbying Disclosure Act page returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 18 | [Fatality Inspection Data](https://www.osha.gov/fatalities) | Institutional page body observed | OSHA states fatality-inspection data are refreshed daily but only after an approximately six-month opening-conference delay. |
| 19 | [9/11 Commission Records](https://www.archives.gov/research/9-11) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 21 | [ADAMS Public Documents](https://www.nrc.gov/reading-rm/adams) | Automated access restricted | NRC ADAMS page returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 23 | [Oversight.gov](https://www.oversight.gov/) | Automated access restricted | Oversight.gov returned HTTP 406 to automated retrieval; not a broken-link determination. |
| 24 | [EDGAR — SEC Search Filings](https://www.sec.gov/search-filings) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 25 | [Regulations.gov](https://www.regulations.gov/) | Automated access restricted | Regulations.gov returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 28 | [FederalRegister.gov](https://www.federalregister.gov/) | Institutional page body observed | FederalRegister.gov itself says its HTML is not the official legal edition; use official GovInfo edition for controlling text. |
| 29 | [Columbia Accident Investigation Board Report](https://ntrs.nasa.gov/citations/20030093634) | Timeout | NASA NTRS citation request timed out; record existence and landing-page content not independently verified this run. |
| 30 | [Rogers Commission Report — Challenger](https://www.nasa.gov/history/rogersrep/) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 31 | [World Trade Center Disaster Investigation — NCSTAR 1](https://www.nist.gov/publications/federal-building-and-fire-safety-investigation-world-trade-center-disaster-final-report) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 33 | [Sinking of El Faro — DCA16MM001](https://www.ntsb.gov/investigations/Pages/DCA16MM001.aspx) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 34 | [The 1980 Eruptions of Mount St. Helens — Professional Paper 1250](https://pubs.usgs.gov/publication/pp1250) | Automated access restricted | USGS PP1250 landing returned HTTP 403 to automated retrieval; do not label broken. |
| 38 | [BP Texas City Refinery Explosion](https://www.csb.gov/bp-america-texas-city-refinery-explosion/) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 41 | [America Burning](https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf) | Institutional page body observed | Federal PDF opened and a page inspected. PDF explicitly exempts photographs from broad reproduction permission; linked-only, no image reuse. |
| 45 | [Psychology of Intelligence Analysis](https://www.cia.gov/resources/csi/books-monographs/psychology-of-intelligence-analysis-2/) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 46 | [HABS / HAER / HALS](https://www.loc.gov/pictures/collection/hh/) | Automated access restricted | LOC HABS/HAER/HALS catalog returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 47 | [topoView — Historical Topographic Map Collection](https://www.usgs.gov/tools/topoview) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 48 | [Chronicling America](https://www.loc.gov/collections/chronicling-america/about-this-collection/) | Automated access restricted | Landing/entry only; rights assessed per record |
| 55 | [National Archives Catalog](https://catalog.archives.gov/) | Application shell only | National Archives Catalog returned an almost empty JavaScript application shell; records/search not validated through this interface. |
| 56 | [Preservation Briefs](https://www.nps.gov/orgs/1739/preservation-briefs.htm) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 59 | [Navigation Rules and Regulations Handbook](https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/Handbook/Nav%20Rules%20Handbook_Corrected_08-12-2024.pdf) | PDF landing + cover check | Landing/entry only; rights assessed per record |
| 60 | [Secretary of the Interior’s Standards for the Treatment of Historic Properties](https://www.nps.gov/orgs/1739/secretary-standards-treatment-historic-properties.htm) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 62 | [Office of Legal Counsel Opinions](https://www.justice.gov/olc/opinions) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 65 | [Congressional Research Service Products](https://www.congress.gov/crs-products) | Automated access restricted | Congress.gov CRS products path rejected automated retrieval; content not validated. |
| 66 | [Congressional Hearings Collection](https://www.govinfo.gov/help/chrg) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 67 | [Federal Audit Clearinghouse](https://www.fac.gov/) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 68 | [RECAP Archive / CourtListener](https://www.courtlistener.com/recap/) | Automated access restricted | CourtListener RECAP returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 69 | [NIST Disaster and Failure Studies Data Archive](https://www.nist.gov/disaster-failure-studies/data-archive) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 70 | [NTSB CAROL — Case Analysis and Reporting Online](https://www.ntsb.gov/Pages/carol.aspx) | Institutional page body observed | NTSB CAROL help specifies aviation coverage from 1962, other transport modes from 2010; check individual dockets. |
| 72 | [National Weather Service Service Assessments](https://www.weather.gov/publications/assessments) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 73 | [National Hurricane Center Data Archive](https://www.nhc.noaa.gov/data/) | Automated access restricted | NHC data page returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 85 | [National Register of Historic Places — Database and Research](https://www.nps.gov/subjects/nationalregister/database-research.htm) | Institutional page body observed | NPS states some Register files are not online and restricted files are not posted; use reference-number and custodian route. |
| 87 | [CyberCemetery](https://govinfo.library.unt.edu/) | Institutional page body observed | Landing/entry only; rights assessed per record |
| 88 | [Biodiversity Heritage Library](https://www.biodiversitylibrary.org/) | Automated access restricted | Biodiversity Heritage Library returned HTTP 403 to automated retrieval; not a broken-link determination. |
| 89 | [National Archives Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer) | Previously observed institutional content | Landing/entry only; rights assessed per record |
| 90 | [National Archives Donated Collection Explorer](https://www.archives.gov/findingaid/donated-collection-explorer/1000) | Institutional page body observed | Donated Collection Explorer tracks donated collections as a separate population from federal record groups; page ratios are estimates. |

## Rights and QA policy

All linked material remains at the source institution. No photographs, scans, PDFs or other third-party media are embedded or mirrored in this audit. `U.S. government work`, `Link-only`, `Public data` and institutional labels already on FV cards are catalog hints, **not blanket licenses**. Recheck particular document/image authorship, embedded third-party material and source terms before reproducing anything.

The primary research corpus and source titles/URLs remain identical to the published inventory. The audited records now carry `last_checked`, `access_outcome`, `link_verification_scope` and optional `qualification` fields. Other entries remain explicitly unverified.

**Still HOLD:** WordPress #1338 and #77 have unchanged public text/counts. Existing [draft PR #2816](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2816) holds its 15 guarded replacements until independently inspectable **production-theme** 320/390/768/1440 + keyboard/screen-reader QA, live search and category tests, and explicit subscriber/social suppression evidence. An automated retrieval result is not a production screenshot.

**Next pass:** Examine remaining 40 source URLs, prioritizing highest-use collections and URLs currently denied/timeout with a normal browser; require endpoint-level confirmation and any underlying image-specific rights before reproducing. Coordinate potential Grok promotion only after the directory is publicly accurate; no account change performed.

**No WordPress write, page publish, email, social post, paid action, or shared-template change occurred in this audit.**
