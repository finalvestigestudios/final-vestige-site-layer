# Library release gate: Research Sources, 90-card reconciliation

**Owner:** Final Vestige Studios — LIBRARY only  
**Checked:** 2026-11-16 Pacific  
**Status:** REVIEW / RELEASE HOLD — no live WordPress write, no email, no spending  
**Reference issue:** [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788)

## Why this is worth fixing

The published [Research Sources](https://finalvestige.com/free-resources/research-sources/) directory promises **60** records in its static introduction, filter labels and initial announcement; the authenticated WordPress page contains **90 individual source cards**. The supplemental JavaScript upgrades some text to 90, but its two category counts are wrong. Visitors with scripts disabled and some crawlers continue to read the outdated static claim. The main [Library](https://finalvestige.com/free-resources/) landing page also promises sixty and calls five categories "eight research families."

This is a trust and information-architecture fault, not an invitation to add 30 duplicate entries.

## Source-of-truth readback — before changes

- Published WordPress source page: **#1338**, child of Library #77, slug \`research-sources\`; last modified \`2026-11-03T22:12:43\` (site-local).
- Main Library parent **#77**; last modified \`2026-11-07T19:39:01\` (site-local).
- First HTML block: **60** cards. Supplemental HTML block: **30** more. Total **90**, with **90 unique titles** and **90 unique destination URLs**. No cards removed or added in this planned repair.
- Correct categories:
  - Declassified & decisions: **12**
  - Accountability & public records: **24**
  - Engineering, disaster & safety: **21**
  - Archives, maps & research: **25**
  - Navigation & preservation: **8**
- Exact appendix: [90-card JSON source inventory](research-sources-90-inventory-2026-11-16.json). The URLs are copied from authenticated WordPress markup, not new third-party results.

## New durable assets in this review

1. A machine-readable, dated **90-record inventory** containing categories, existing institutional/reuse cues, original outbound URLs, unique-entry checks and honest per-link check status. Copyright status is **not** inferred from hosting.
2. A **fail-closed staging patch**, [reconcile-research-sources-90.mjs](../../../scripts/editorial/reconcile-research-sources-90.mjs), which refuses unexpected IDs, revisions, counts, duplicate destinations or nonunique text anchors. It outputs staged markup; it has **no network calls** and **no publishing action**.
3. [Regression tests](../../../tests/editorial/research-sources-90.test.mjs) covering 90-card preservation, categories, all 15 exact text substitutions, edit conflicts, duplicates, missing cards and reruns.

**Dry-run result against authenticated 2026-11-16 raw Gutenberg content:** all **15 text anchors found exactly once**, 90 unique title and URL pairs maintained, five category totals correct, Gutenberg marker counts unchanged (page #1338: three \`wp:html\` sections plus two groups; Library #77 untouched structurally). All original source URLs, titles, categories and rights cues are preserved; the dated NARA Explorer description is the one intentionally rewritten card description. Layouts and Gutenberg block structure remain unchanged. This was performed as an in-memory structural rehearsal; the new Node regression suite has not been independently executed in CI. Do not claim production browser testing.

## Source-freshness correction — 2026-11-16 follow-up

NARA's [official Record Group Explorer](https://www.archives.gov/findingaid/record-group-explorer) now reports **503,600,456 online textual scans / 12,473,570,637 estimated pages = 4.04%** for **October 2026**, compared with the directory card's outdated **June 2026 475,127,595 scans / ~3.87%**. The retained percentage is a **scan-to-estimated-page ratio**, not the percentage of physical records surviving, publicly accessible, or fully catalogued. The adjacent donated-collection visualization is a **different population** (October 2026: 1,175,630 scans / 25,447,250 estimated pages, 4.62%); figures must not be merged. Source pages last rechecked 2026-11-16. These institutional figures may change monthly.

Instead of replacing one number with another that will soon age, the guarded patch now revises the existing **Record Group Explorer description** to evergreen language and keeps its source URL, title, category and reuse cue intact. This increases the planned correction from 14 to **15 exact anchors**. The 90-entry JSON file is a dated **pre-repair inventory**, not a claim that its underlying WordPress copy has already been repaired.

### Independently executed local Node QA (follow-up)

Reconstructed the PR's staged JavaScript and Node test suite in an isolated local environment and ran `node --test` on the PR-original script/tests: **7/7 passed, 0 failed**. Added one source-freshness guard regression and a stale-metric assertion to the existing test fixture; the revised suite passed **8/8, 0 failed** locally. Original test suite and follow-up execution are **synthetic fixture QA**, not production WordPress-theme browser, accessibility or source-file delivery QA. Authenticated readback immediately before this update again found #1338 (2026-11-03 22:12:43) and #77 (2026-11-07 19:39:01) unchanged, with 90 unique titles/URLs, 12/24/21/25/8 category counts and 14 prior anchors each present exactly once. The new NARA stale phrase is also present exactly once. No WordPress write occurred.

## Targeted editorial corrections

On published #1338, correct the headline quantity, introductory statistic, search label, all-filter quantity, five category numbers, initial live-region message, original script's total, and supplemental script's **23 → 24** and **26 → 25** entries; also replace the outdated June 2026 Record Group Explorer description with source-qualified evergreen text. Preserve all **90** source entries and links.

On published parent #77, change only **"Sixty free" → "Ninety free"** and **"60 curated sources · 8 research families" → "90 curated sources · 5 research paths."** The second correction is grounded in five \`data-cat\` families visible in the source directory.

### Preservation and release policy

No modifications to site navigation templates, other published pages, homepage, Preparedness, Investigations, Grok accounts, subscribers or unregistered WordPress metadata. This is an **existing published-page correction**, not a new article. Ensure any site automations do not email or autopost on an update, and do not assume the per-page Jetpack first-publication field is available on the public-page connector. No new source images or reused third-party assets.

### Primary-link spot check on 2026-11-16

| Source card | Check | Evidence and qualification |
|---|---|---|
| VENONA, NSA (#4) | Institutional landing page opened | https://www.nsa.gov/serve-from-netstorage/news-features/declassified-documents/venona/index.html |
| Nixon Collection, CIA (#7) | Institutional article opened | https://www.cia.gov/stories/story/the-nixon-collection/ |
| Chronicling America, LOC (#48) | Automated request returned HTTP 403 | https://www.loc.gov/collections/chronicling-america/about-this-collection/ — **not proof the link is broken** |
| Navigation Rules, USCG (#59) | Institutional PDF opened; cover inspected | https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/Handbook/Nav%20Rules%20Handbook_Corrected_08-12-2024.pdf — historical edition, not necessarily current boating guidance |
| Congressional Hearings, GovInfo (#66) | Institutional landing page opened | https://www.govinfo.gov/help/chrg |
| NIST Disaster/Failure Data Archive (#69) | Institutional landing page opened | https://www.nist.gov/disaster-failure-studies/data-archive |
| NARA Record Group Explorer (#89) | Institutional page opened | https://www.archives.gov/findingaid/record-group-explorer — scan percentages are estimates of textual page coverage, not of records surviving |

The other **83 URLs were not independently opened in the initial inventory pass**. The source-freshness follow-up also opened NARA's [October 2026 record-group figures](https://www.archives.gov/findingaid/record-group-explorer) and [donated-collection figures](https://www.archives.gov/findingaid/donated-collection-explorer/1000). A successful institutional landing page check does not prove every linked downloadable record is publicly accessible, complete, or reusable. Existing links are kept intact in this scoped correction.

## QA gate: HOLD before a live WordPress correction

1. **Actual public-theme browser**, 320 / 390 / 768 / 1440, JavaScript on and off: capture readable screenshots; verify group order, no duplicate rendering, no horizontal overflow and visible keyboard focus.
2. **Live filter functionality:** search a title that occurs only among the supplemental 30 (for example, "CyberCemetery"); verify relevant card appears and the announced result count is 1 of 90. Test each of five category filters including the corrected 24/25 totals; confirm no console errors.
3. Check screen-reader/live-region behavior and no-JavaScript fallback. Do not confuse ordinary HTML text extracted by crawlers with real rendered DOM.
4. Re-fetch #1338 and #77 in authenticated edit context, compare \`modified\` and section hashes immediately before any live change. Use WordPress **single-section optimistic-locking** operations where possible; do not blindly overwrite concurrent edits.
5. If real browser/network QA is unavailable, **do not publish the patch**. Keep this branch as a review candidate.
6. After a safe scoped write, independently re-read WordPress raw content and the public URL; inspect count labels, SEO title/description, all 90 live cards, sample rights notices and outgoing links. Record any changed page versions and verify no unwanted subscriber/social delivery.

**Current blocker:** public-theme screenshot link was generated by WordPress, but actual screenshot pixels were not independently inspectable; the container cannot resolve external DNS. The site itself was externally read by web search and authenticated WP connector. That does **not** pass requirement #1. Release remains held.

## Related FV reader journeys

[The Archive Trail](https://finalvestige.com/the-archive-trail/) explains source provenance and rights; [The Box Behind the Citation](https://finalvestige.com/free-resources/the-box-behind-the-citation/) follows a citation to a physical record; [Apollo 1 Evidence Atlas](https://finalvestige.com/apollo-1-evidence-atlas/) shows original records informing an investigation. Keep internal links to published and verified resources rather than promoting unpublished drafts.

**Optional Grok lane handoff (idea only):** "We don't need another history claim—we need the actual document. Here's where ninety official records collections begin." Promotional delivery must wait for corrected public content and remains under Grok's account ownership.
