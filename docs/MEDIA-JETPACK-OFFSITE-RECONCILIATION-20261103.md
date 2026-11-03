# Media origin census — Jetpack proxies of *other* domains (2026-11-03)

**Scope: isolated media-recovery PR #183 only. Zero WordPress production writes, site design edits, asset copies or paid services.** This memo reconciles the *source URL* denominators from Site QA #154 and Media Recovery #183. It is not evidence of visitor HTTP failures, image weight savings or published repairs.

## 61-post independent cross-branch reconciliation

- The **Site QA #154** branch `qa/media-source-dependency-20261029-2347` contains `qa/media/cms_image_census_20261030.csv`, Git **blob `76aa63ffaa299a6e6878edc1b66e637fa6f058ab`**, reporting **61 posts / 355 stored image slots / 286 offsite-origin slots**.
- Media Recovery #183's eight frozen source files `qa/media-recovery/parts/01.json`–`08.json`, fetched from the actual PR branch, account for **61 posts / 355 slots / 288 offsite-origin slots**.
- Reconciliation compared all 61 post IDs and all 355 slots with the actual QA CSV rather than assuming the two snapshots were identical. **59 posts have identical offsite counts; exactly 2 post-level counts differ:**
  - **291, *One Bulldozer Never Came Back*:** QA **5** versus media **6**. Slot **291:0** is `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1`.
  - **285, *The Light Said Closed*:** QA **5** versus media **6**. Slot **285:1** is `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1`.
- Both current URLs use the **i0.wp.com delivery host** but proxy **third-party upstream sites**. Classify an `i0.wp.com/finalvestige.com/...` reference as first party, but **not** `i0.wp.com/text-message.blogs.archives.gov/...` or `i0.wp.com/www.squawkpoint.com/...`. The source-level third-party-origin count is therefore **288 in the later media snapshot**. This does not mean all 288 requests bypass a CDN at runtime.
- **Causation remains OPEN.** Site QA's own classifier already distinguishes first-party Jetpack paths. Because the October 30 QA CSV does not retain the earlier raw `src` values and both relevant live posts were modified on November 2, these two differences may reflect edits between snapshots; attributing them to a Site QA software defect would be unsupported.

## Live source corroboration / archival identity / rights

Authenticated **read-only** WordPress post reads on **November 3** show:
- 291 published and last modified **2026-11-02T21:36:09**: 6 inline images, original slot 291:0 URL and ALT still present.
- 285 published and last modified **2026-11-02T21:39:59**: 6 inline images, original slot 285:1 URL and ALT still present.

Both **exact i0.wp.com URLs displayed in an independent web image renderer** on Nov 3. **No numeric origin status, logged-out guest-browser `currentSrc`, decode result or CDP encoded image bytes** were obtained. Do not promote a successful renderer display to evidence of visitor-browser success, and do not add these to the reported, unverified 42-image failure count.

**291:0:** The [National Archives’ May 31, 2016 Teton Dam photo history](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/) identifies **NAID 28894685** as a photograph of the enlarging breach reaching the crest. Its archive account credits **Jerry Dursteller**, a *contractor employee*, for the failure photo series. Catalog hosting is not blanket federal-author-photo copyright clearance. Verify exact file/crop, author and item-level rights before proposing an archive-hosted derivative. The 291:0 published image appears to depict the same event, but binary or crop identity is unproven.

**285:1:** The [U.S. NRC's TMI-2 Control Room in 1979](https://www.flickr.com/photos/nrcgov/7447591188) is a primary-source **subject candidate only**; it is not established as the same photograph as Squawkpoint's proxied image. Do not silently switch to another angle, label the file public domain without checking item terms, or erase existing photo credits.

Both sources have **unknown verified intrinsic pixel dimensions**: proposed WordPress derivative width = `min(960, verified intrinsic width)`, derive height from original aspect ratio, **never upscale**. Until dimensions and rights are established, width is a conditional cap rather than a generated asset; source replacements, cached copies and WordPress uploads/edits are **HOLD**. Preservation plan: (1) capture full source/target HTTP evidence; (2) verify historical frame, source licensing and attribution; (3) if specifically approved, make an optimized versioned candidate in **staging**; (4) compare full and mobile before/after visuals, ALT and crop; (5) preserve exact existing URL and rollback mapping; (6) require explicit release authorization.

## Auditable files and negative controls

- [Two-slot exact URL/renderer/browser-null/rights audit](../qa/media-recovery/proxy_origin_census_delta_20261103.json).
- [Fail-closed cross-branch reconciliation](../qa/media-recovery/reconcile_proxy_census_20261103.cjs) compares **all 61 post IDs, 355 exact slot records, the actual Site QA 61-row CSV**, and item-specific custody gates.
- [13 adversarial test cases](../qa/media-recovery/test_proxy_census_20261103.cjs) verify the baseline and reject forged visitor 404, malformed Jetpack paths, edited source URLs, third-post drift, duplicate CSV rows, changed rights/republication flags and upscaling.

**Verification:** 13/13 tests replayed using exact GitHub-committed source and test Git blobs in an isolated V8 Node-compatibility shim. **Additionally, the real Site QA CSV blob** `76aa63ffaa299a6e6878edc1b66e637fa6f058ab` was passed through the committed reconciling code with all eight current media frozen parts: PASS, **59 matching + two identified post-level deltas**. Native Node CI and logged-out Chrome/CDP not run.

### Handoff to Site QA #154
Site QA keeps ownership of guest-browser checks and its existing scripts. Prioritize **285:5** and **287:5** before the two **displayed** proxy images 285:1/291:0. When those two are reached, capture `currentSrc`, actual image GET URL/redirect/status/MIME, decoded pixel dimensions, CDP encoded bytes and screenshot. A CDN proxy path is not automatically first-party source custody; a renderer's result is not an actual browser result.

**Unchanged release baseline:** 61 posts / 355 stored slots / 288 offsite in the later source snapshot / 13 WordPress originals >1.5 MiB (stored bytes only). Reported 42 broken remains guest-unverified, claimed 76% transfer reduction still unmeasured, production repairs = **0**.
