# Project AZORIAN post 218: six external image sources (2026-11-09)
**DRAFT / DO NOT DEPLOY.** Frozen 2026-10-30 WordPress fixture `qa/media-recovery/parts/06.json` blob `0f3dfe398a76838049cebba7cb773d5c5a0c8c69`, post [218](https://finalvestige.com/2026/08/18/the-rock-had-to-be-real/), six distinct source images. All six literal Wikimedia `Special:Redirect/file?width=1280` image URLs were checked via `web.open`: each produced **tool URL not accessible**. This is **not an origin 403/404 or proof of visitor failure**. Six distinct Commons **catalog HTML** pages were accessible. Browser statuses, cache, currentSrc, dimensions and transfer bytes remain unknown.
 
| Slot | Item identity / chronology | Catalog original | Max 960 proportional (catalog only) |
|---|---|---|---|
| 218:0 | CIA Museum *actual nodule in Lucite*, no evidence of submarine cargo | 800×533, 9,281 B | **800×533; no upscaling** |
| 218:1 | Undated vessel image, no exact mission-year provenance | 1280×833, 563,931 B | **960×625** |
| 218:2 | CIA Museum Glomar Summa patch; underlying design rights review | 800×533, 26,721 B | **800×533; no upscaling** |
| 218:3 | **2022 CIA Museum model photograph**, NOT actual wreck underwater photo | 3598×2400, 5,740,268 B | **960×640** |
| 218:4 | **2022 engineer Sherman Wetmore viewing oil painting**, not 1974 photo | 800×709, 31,376 B | **800×709; no upscaling** |
| 218:5 | **2022 museum coveralls and ashtray exhibit**, not mission-era image | 2400×3598, 5,171,994 B | **960×1439** |
 
Catalog *original* byte sizes DO NOT equal the visitor's `width=1280` rendition, caching or CDP transfers. The two 5+ MB master originals are a future performance research lead, **not measured user download bytes**.

**Authoritative CIA crosswalk:** [Recovered manganese nodule](https://www.cia.gov/legacy/museum/artifact/manganese-nodule-encased-in-lucite/); [Summa crew patch](https://www.cia.gov/legacy/museum/artifact/glomar-explorer-crew-patch/); [project exhibit](https://www.cia.gov/legacy/museum/exhibit/project-azorian/); [Sherman Wetmore 2022 visit](https://www.cia.gov/stories/story/honoring-the-mission-of-project-azorian/). All individual Commons file catalogs and exact original URLs are retained in machine audit.

**Rights HOLD:** Commons claims U.S. public-domain government works, but specific photograph identity/crop must be independently verified. A federal employee's photo of a **possibly independently authored oil painting** does not itself clear underlying artwork rights; same issue may arise for patch logos and manufacturer-created artifacts. No permission to copy, cache or upload is inferred.

**Restoration plan:** Site QA #154 retains its own cold full-scroll guest Chrome collector. Priority remains **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. Only after confirmed guest image failure, item-specific original/crop licensing and source bytes/rights verification, stage <=960 wide *with no upscaling* and visual text/artwork legibility QA. Preserve source URL, ALT, caption and Gutenberg block for rollback. Obtain separate explicit WP production-write approval.

**Performance:** Historical **61 posts/355 positions/288 external** and expanded **66/361** are different cohorts. The reported **42 broken images** remain guest-unconfirmed. The **76% reduction** is unmeasured, requiring matched same-slot cold CDP image wire bytes (not Commons original/catalog bytes or WP stored size), explicit no-cache, three runs per mobile and desktop, matching history/crops and p50/p95. **15 WP originals >1.5 decimal MB = 47,096,779 stored bytes**, not image payloads to visitors.

**Verification:** companion fail-closed validator and 51 positive/adversarial cases executed in isolated JavaScript V8 against identical validator semantics before committing. Native Node CI and real browser remain outstanding. No binaries, downloads, caching, WP writes, post rewrites, homepage edits, subscriptions, or spend.
