# Ninety Doors — Source Access Audit & Field Interpretation

*Final Vestige Studios · The Library · 18 November 2026 · HOLD / repository-only*

**The reader's problem:** An official research link that fails in one browser is not necessarily a missing record. A link that opens successfully is not necessarily the requested document. The Library should make both distinctions visible.

This companion to [The Ninety Doors Research Desk](./the-ninety-doors-offline-research-desk-2026-11-18.html) records a new access attempt against **every one** of the published [Research Sources](https://finalvestige.com/free-resources/research-sources/) directory's 90 destinations. It is the **first complete 90-URL retrieval sweep** for this snapshot, not a full reader-browser acceptance test.

[Download the 90-row source-access ledger](./research-sources-90-access-probe-2026-11-18.csv) · [Inspect the original results chart](./research-sources-90-access-probe-2026-11-18.svg).

## What the sweep actually found

| Observation | Rows | What it establishes | What it does not |
|---|---:|---|---|
| Institutional HTML returned with readable text | **63** | Automated retrieval produced useful page text | That the database, original documents or downloads work |
| PDFs returned with extractable text | **2** | A PDF resource was reachable and had parseable content | That image rights are clear or OCR is perfect |
| Sparse or client-rendered page shell | **3** | A gateway responded with little extractable content | That a researcher using JavaScript cannot search it |
| Automated retrieval could not inspect destination | **22** | The probe stopped at a status, policy or size limit | That the archive, link, document or institution is unavailable |
| **Total** | **90** | Each original directory destination received an attempted probe | No claim of 90 real-browser checks |

Of the 22 inconclusive probes, **15 returned 403**, **2 timed out**, and one each returned **502**, **404**, a restricted-URL error, a disabled-URL error or a size-limit error. The 404 for Smithsonian Open Access (directory record **FV-RS-053**) is a particularly useful caution: an independent search result surfaced the same Smithsonian-maintained Open Access page. Its present status requires an ordinary-browser verification, *not* automatic deletion from the index.

The shaded bars in the original SVG are proportions of fetch outcomes, **not source quality, trust, legitimacy, site uptime or source completeness**. Text equivalent: 63 HTML, 2 PDFs, 3 sparse shells, 22 inconclusive.

## Four things a researcher can do now

**1. An HTML page opened.** Keep the actual title, URL, institution and date examined, then open the **individual record**. For example, [NARA's Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer) is a discovery aid. Its scan percentages are calculated from online page scans and **estimated** total textual holdings, not a guarantee that any particular file is digitized.

**2. A PDF opened.** Capture its title, edition and record identifier, and inspect page images when layout, illustrations or attribution matters. The original [U.S. Fire Administration-hosted *America Burning* PDF](https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf), which returned text successfully, itself carries an explicit reuse qualification: the report can be reproduced, **except its photographs, which require permission from their owner**. A governmental host does not erase that distinction.

**3. Only a search shell loaded.** Test the gateway in a regular current browser with scripts enabled, check its documented API or file download route, and record whether a useful result was actually retrieved. This category includes USAspending Search, the NARA Catalog landing application, and NOAA Historical Hurricane Tracks. Do not call them empty archives because a text parser saw little.

**4. An automated probe failed.** Retry in an ordinary browser; consult the agency's published alternate path, status page or help desk; preserve the URL, attempted date and exact error class. If a new official destination is found, record the previous URL and a source for the change before updating the live directory. A 403 often identifies an access boundary of the **retrieval environment**, not a deliberate refusal to publish records.

## Two date-sensitive cautions from official pages

- The [NOAA NCEI Event Footprint Catalog](https://www.ncei.noaa.gov/products/event-footprint-catalog) warned on **November 18, 2026** that cloud migration could delay data access, including portals and interactive maps. Its page returned readable HTML, but end-to-end service availability was not established.
- The [USGS EarthExplorer](https://earthexplorer.usgs.gov/) homepage advertised scheduled EROS portal maintenance for **November 23, 2026, 7:00 a.m. to approximately 2:00 p.m. Central Time**. A later error during that window should not be silently classified as permanent record loss. Recheck the official notice before using this date in a future post.

## A small, printable access-failure receipt

When a link fails, preserve these fields in your working notes. The version of the URL is as important as the error.

| Field | Researcher's entry |
|---|---|
| Directory record and source question | _______________________ |
| Institution, record or accession identifier | _______________________ |
| Attempted URL and local date/time | _______________________ |
| Browser/tool, script and authentication state | _______________________ |
| Exact observed result and any redirect | _______________________ |
| Alternative official search/help location | _______________________ |
| Original document actually inspected? | Yes / No / Unknown |
| Rights statement inspected for target item? | Yes / No / Unknown |
| Remaining uncertainty and next check | _______________________ |

**Evidence rule:** A collection page does not prove the contents of a file. An inaccessible search page does not prove the file never existed. A repeated URL in a second repository does not create a second independent witness.

## Verification method and interpretation notes

The 90 destinations were taken **without modification** from the existing [portable Library source snapshot](./research-sources-90-portable-index-2026-11-18.csv), itself previously reconciled against WordPress published page **#1338**, including its 30 JavaScript-appended records. Each URL was submitted to a `web.run open` institutional-page retrieval on **2026-11-18**. Observations were grouped by returned page content or retrieval error. No automated redirection scraping, bypass of robots, credential use, item downloads, nonpublic queries, purchases or reproduction of archival media took place.

**This is not a real-browser uptime test.** Some sites block crawlers, use JS-heavy apps, stream PDFs or require special access. Web result statuses cannot be generalized to all users or all times. The exact error buckets and URLs are available in the CSV for later confirmation. There is no claim that all 90 working links, downloads or rights were verified; the separate index's prior "not individually rechecked" field must be read as a historical snapshot until a future verified update is explicitly merged.

## Provenance and rights ledger

| Source | Use here | Last checked | Access / rights |
|---|---|---|---|
| [Published FV Research Sources](https://finalvestige.com/free-resources/research-sources/) · WP #1338 | Authoritative 90-card source inventory; existing published page | 2026-11-18 | FV-authored descriptions and outgoing links only |
| [FV Editorial Standards](https://finalvestige.com/editorial-standards/) | Method, uncertainty and media rules | 2026-11-18 | Linked; not republished |
| [NARA Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer) | Official explanatory example for gateway vs item and estimated digitization | 2026-11-18 | Linked; no archival scans copied |
| [NARA Donated Collection Explorer](https://www.archives.gov/findingaid/donated-collection-explorer/1000) | Second official example of estimated counts | 2026-11-18 | Linked; no donated documents copied |
| [USFA *America Burning*](https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf) | Controlling PDF with explicit photographic reuse exception | 2026-11-18 | Original image use **not cleared**; linked only |
| [Smithsonian Open Access](https://www.si.edu/openaccess) | Discrepancy between tool 404 and institution-indexed public Open Access page | 2026-11-18 | No image copied; check individual item reuse terms |
| [NCEI Event Footprint Catalog](https://www.ncei.noaa.gov/products/event-footprint-catalog) | Institution's cloud-migration service warning | 2026-11-18 | Link only |
| [USGS EarthExplorer](https://earthexplorer.usgs.gov/) | Institution's dated maintenance notice | 2026-11-18 | Link only |

**Original media:** The adjacent SVG is an original, accessible Final Vestige Studios data illustration authored November 18, 2026. Caption: *Results of automated text/PDF retrieval attempts for the 90 directory gateways; these are not accessibility, rights or uptime scores.* Alt text is preserved in the SVG's `title` and `desc`, and its numbers appear in the table above. No images, scans, videos or institutional logos are included. Reproduction license for the SVG is **not granted**, pending studio policy.

## Release & coordination status

**Draft/HOLD.** The new CSV, explanatory guide and SVG are repository assets for review. They do **not** change the public directory, its original destinations, search, navigation, subscribers or notification settings. Actual browser QA at 320/390/768/1440, keyboard and screen-reader review, and page-level first-publication notification suppression are still required before publishing an integrated public UI.

The existing directory's **stale 60-source static copy and mistaken 23/26 category counts** remain [tracked separately in Library issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788). This probe does not justify editing those scripts without the proper site-specific release gate.

**Related FV field guides:** [The Archive Trail](https://finalvestige.com/the-archive-trail/) · [The Black Bar](https://finalvestige.com/free-resources/the-black-bar/) · [The Page That Changed](https://finalvestige.com/free-resources/the-page-that-changed/) · [The Library](https://finalvestige.com/free-resources/).

**Potential Grok content lane (idea only):** “A 403 is not a vanished document.” Show a reported 403 beside an official source discovery route, with no invented screen interactions. Coordinate only after publication; do not touch Grok's accounts.