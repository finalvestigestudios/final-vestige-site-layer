# Final Vestige Library — The Property Without a File
**Prepared:** 2026-11-10 (Pacific) · **Publication:** HOLD (local release candidate, not a public page)

## Reader problem and original asset
A National Register of Historic Places designation may be findable even when its nomination file is not downloadable from the first database searched. This original source-led field guide follows the NPS listing/reference number to NARA records through 2012, NPGallery for files missing from NARA including some later nominations, state SHPO archives, and the NPS reference-request path.

Completed local conversation artifacts (not committed or uploaded to WP): 24.2 KB standalone accessible HTML guide with original SVG research-route diagram, local-only request-text builder and JSON export; three-page illustrated and printable PDF (6 clickable official links); 6-row institutional provenance/rights CSV; local Playwright QA JSON; SHA manifest and ZIP release candidate. **ZIP SHA-256:** `d60efcb4e29801e7182afa84d8368833a354b629a11f5982df4267f40631a934`. These artifacts were supplied in the associated FV Library Studio conversation; there are no public media URLs.

## Primary source and rights trail — checked 2026-11-10
1. [NPS National Register database / records / requests](https://www.nps.gov/subjects/nationalregister/database-research.htm) — first-party text retrieved. Page updated 2026-06-04. NARA holds records through 2012; some later records and missing files are in NPGallery; some unposted files may be requested; restricted files not posted.
2. [NARA Catalog](https://catalog.archives.gov/) — official application entry retrieved, but a dynamic record-level search was **not** verified; do not claim a record exists or is absent from a blank landing page.
3. [NPGallery National Register search](https://npgallery.nps.gov/nrhp) — first-party form retrieved; search fields include name, state, county, reference number and record category.
4. [NPS SHPO inventories](https://www.nps.gov/subjects/nationalregister/shpo-inventories.htm) — official state-directory text retrieved; each state's holdings differ; page last updated 2023-08-17; individual state destination not rechecked.
5. [NPS digitization partnership](https://www.nps.gov/articles/nr_digitization.htm) — official historical explainer retrieved, updated 2019-06-03; roughly 88,000 digitized records **as reported then**, not a current 2026 total; older map has an earlier coverage cutoff.
6. [NPS Content and Copyright](https://www.nps.gov/subjects/nationalregister/national-register-content-and-copyright.htm) — official mixed-rights policy retrieved; government works and third-party supplied photographs/media do not share blanket rights. Last updated 2024-01-05. No third-party archival scans, photographs or maps were reproduced.

**Original media:** FV research-flow SVG, November 2026. Explicitly labeled illustrative and not a source document; original text, worksheet, and graphic. Alt text and visible text alternative provided. No external images copied or embedded.

## Local testing and HOLD
Playwright Chromium `set_content` (standalone, not the WP theme) at **320 / 390 / 768 / 1440px**: all four passed with 0px document-wide overflow, no JS exceptions, all five research doors and six sources present; form generation and JSON export worked. PDF was rasterized and visually inspected: three pages, six embedded click targets. ZIP CRC passed.

**Still missing:** actual WordPress-theme authenticated visual QA at four widths, anonymous visitor/source and media checks, and verified no-email/no-social first-publication pathway. Only publish after those checks; no Library navigation card should advertise a resource not yet live. Shared Site QA #1589 owns the screenshot dependency. No paid service, email blast or Grok social-account action.

## Separate directory repair in the same session
In existing unpublished WordPress Research Sources **staging #2354 only**, added three source-specific updates: #52 NRC Three Mile Island modern official overview URL / DVD vs official records distinction; #77 NPS National Register retrieval boundaries and rights; #84 USCG Ice Patrol annual PDF vs earlier decade ZIP packaging. WordPress authenticated readback: **90 unique source titles and primary URLs**, category distribution **12/24/21/25/8**, status `draft`/noindex, parent Library #77. Existing published directory #1338 and Library landing #77 were **not modified**. Since prior 42 source refinements were preserved, count is now **45**.

Existing persistent [90-source provenance register](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/main/docs/editorial/library/research-sources-90-provenance-ledger-2026-11-10.csv) was updated, commit `05c7a04ae19a520e32dbec9815f254ec28cd8212`. **25 fresh source-entry checks** across the five categories: 20 with readable institutional content, 4 whose direct automated opens produced HTTP 403, and 1 JavaScript app shell without readable result content. The register now has 90 cards with **34 checked at least once on 2026-11-10 (including previous run's 10), 56 not yet checked**. A 403 does *not* prove a visitor-facing URL is broken. Do not infer reuse rights from working links.

**Grok lane concept, hold until release:** “The property is listed. Why can’t you find its nomination?”
