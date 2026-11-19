# Train on Paper v3 — conflicting-witness acceptance ledger
Run 2026-11-18 Pacific. **HOLD / DRAFT ONLY**.

## Defect and correction
The v2 workbench could show “Two records available; verification still required” when identity and independence checkboxes were affirmed, even if the researcher had not compared what the two records said. Two real sources may disagree. v3 adds an explicit `witnessRelation` dropdown (unassessed / apparently consistent / material conflict / ambiguous) and `conflictNote` text field. The qualified receipt and CSV preserve both; edits invalidate stale exports. An apparently consistent outcome requires a specific comparison rationale; contradictory and ambiguous cases remain visible. No automatic truth or train-operation determination.

## Verified workbench source
[Committed HTML](./the-train-on-paper-evidence-workbench-2026-11-18.html). Local SHA-256 `5653d2ce098d2a0d60e6d24465e47b2388b3c673d9ee4340758512f1106af56c`. Git blob SHA `8c57ea94f28f47ae30c6fbc10278f0e2c61fb15c` matches the locally tested source exactly.

Local checks: JavaScript syntax PASS; 38 unique HTML IDs; 23 of 23 native form controls labelled. Eight pure-JS classifier tests PASS (unassessed, conflicts, ambiguity, no comparison rationale, compared agreement, same URL, missing exact date, passenger-claim limitation). Initial local Chromium screenshot/test at widths 320/390/768/1440 produced zero page-wide horizontal overflow and tested the fictional example, export and reset. 390px crop was visually inspected. **Do not count this as completed browser acceptance:** an expanded regression first had a stale test expectation; subsequent Chromium launches timed out, including a blank page. Full v3 interaction, formal screen reader, print and production WordPress tests remain open.

## Source and rights checks
- B&O *Book of the Royal Blue*, 1897–1911, Library of Congress title record: https://www.loc.gov/item/05032208/ — LOC says book collection is public domain, but the source establishes published schedules, not train operation.
- Digitized vol. 14: https://www.loc.gov/resource/gdcmassbookdig.bookofroyalblue27balt/ — large (~56.7MB) PDF blocked scan-pixel inspection. Exact issue/page headings remain unconfirmed visually.
- LOC railroads research guide: https://guides.loc.gov/railroads/maps-timetables
- LOC image/item rights: https://www.loc.gov/legal/security-copyright-and-privacy/understanding-copyright/
- NARA digitization provenance: https://www.archives.gov/preservation/family-archives/digitizing
- FV policy: https://finalvestige.com/editorial-standards/

No archival images or licensed media copied. Original FV process SVG is explanatory, not documentary; worked sample is explicitly fictional. Original form entries stay local unless reader deliberately exports/copies/prints.

## WordPress and release disposition
Site check: published Library and Editorial Standards visible with expected metadata; Research Sources screenshot capture links returned but pixels unavailable for direct visual QA. Existing WP page #2924 remains draft, parent #77, noindex. The workbench is **not hosted**. Newsletter setting `email_new_posts_by_default=false` is not proof of total first-publish suppression; site can send email. No WordPress, subscribers, Grok, social or paid service mutations in this run.

**Before publishing:** full v3 browser/assistive-tech/print and guest-link QA; verified 1910 source scan or appropriately qualified claims; safe JS hosting; enforceable first-publication email/social suppression; independent post-publish metadata and link check. Preserve all existing Library paths, design and other editorial lanes.