# Final Vestige media: authenticated published-cohort image benchmark gate — 2026-11-06

**Status: isolated draft-only QA/engineering evidence, no WordPress writes, browser collector, image downloads, cache, homepage modifications, subscription spend, or production repairs.**

## Independently re-read all published WordPress articles (read-only)

WordPress `posts.list` returned exactly **66** posts with `status=publish` and their exact canonical article URLs. Then, using authenticated read-only `posts.get context=edit` for **each of all 66 posts**, counted stored Gutenberg `<img>` tags and external-origin `src` references. The frozen and current image counts agree across all 66 posts (zero drift).

| Cohort | Published posts | Stored inline image slots | Direct external-host references (excluding first-party/Jetpack) |
|---|---:|---:|---:|
| Prior 2026-10-30 sample | 61 | 355 | 286 |
| Re-read published articles 2026-11-06 | 66 | **361** | **294** |

The five newer posts contribute **six** inline images. The Change Blindness post (ID 1922) has **zero** stored inline `<img>` tags; the zero must be explicitly attested, never silently omitted from a full cohort. The fresh census measures editor HTML, **not** whether remote image HTTP loads work or what a visitor actually downloads. The per-post direct external counts and exact published canonical URLs, plus both old and new counts, are in `qa/media-recovery/published_cohort_manifest_20261106.json`. The source-level 61-post census is `qa/media/cms_image_census_20261030.csv` on draft Site QA PR #154.

## Defect in the earlier 76% evidence comparator, and isolation of the fix

The pre-existing `measure_cold_wire_pairs_20261106.cjs` correctly rejects cache hits, HTTP failures, failed decoding, incomplete before/after captures, and mismatched device settings **within** a page. However, its `expected_page_urls` and `published_cohort_size` were entirely **self-declared**. Its test suite even demonstrated that 66 invented `/article-N/` routes could produce `sitewide_claim_allowed: true`. It did not validate which site article a `post_id:image_index` slot belonged to, whether all editor-image slots were included, or whether different pages were measured under identical environments and byte sources.

This batch adds a separate **offline, read-only** wrapper: `qa/media-recovery/verify_published_image_cohort_20261106.cjs`. It must be used before *any* 76%-transfer-weight or site-wide claim. The wrapper:

1. Validates an explicit, freshly recensused 66-post published WordPress manifest, including unique real canonical post URLs, post IDs, 361 inline slots, 294 direct external references and 355 slots in the original 61.
2. Rejects fabricated or out-of-cohort URLs, duplicate/missing pages, DOM slots belonging to the wrong post, missing `post_id:index` images, orphan article-network requests and unverified zero-image claims.
3. Requires a consistent browser/device/viewport/network profile and **one byte source** across every before/after page in the measured cohort. Retains all prior strict cold-network, decode and timestamp checks from the existing comparator.
4. Distinguishes a sample, the historical 61-post cohort, and the **66-post published corpus** as captured November 6. The old 61-post set is no longer the entire current site. A complete 61-post comparison must NOT authorize a current site-wide assertion.
5. Returns `manifest_scope` and explicitly states that any 66-post 'sitewide' conclusion is scoped to the **frozen snapshot**. Refresh the WordPress published-post list and image-slot census before making a later-date claim.

### Safe read-only commands

```bash
node --check qa/media-recovery/verify_published_image_cohort_20261106.cjs
node --test qa/media-recovery/test_verify_published_image_cohort_20261106.cjs
node qa/media-recovery/verify_published_image_cohort_20261106.cjs /path/to/curated-guest-browser-before-after.json
```

The curated input schema is the existing `fv-cold-image-wire-pairs-v1`; this tool **does not collect** HAR or Chrome evidence. It uses Site QA's already assigned browser collection lane (#154). Any network failure must first enter a separate image-defect report rather than being excluded to inflate performance savings. A positive measurement cannot justify replacement rights.

## Tests and limits

The new regression suite has **25 tests**, all executed successfully in an isolated V8 Node-compatible harness using the **GitHub-readback committed wrapper and manifest**. Included are fabricated article URLs; cross-post/out-of-range slots; incomplete image coverage; a non-article image request; mixed wire sources; viewport drift; HTTP 404; warm cache; failed decoding; false zero-image assertions; tampered manifest counts; caller-side manifest injection; and sample/61/66 cohort distinctions. **Native Node execution, GitHub CI and visitor Chrome evidence remain pending.** Tests use **synthetic** example bytes (100,000 before and 24,000 after, i.e. 76%) to check the gate. Those bytes are NOT measurements of Final Vestige traffic or image assets.

## Site QA handoff: visitor-visible broken images remain first priority

The previously reported **42 broken remote image URLs** are *not* a guest-browser-verified defect count. The read-only 294 external `src` links do not establish image failure. Site QA (#154) owns Chrome guest-browser image response, `currentSrc`, `complete`, `naturalWidth`, mobile/desktop layout, and the image network waterfall for priority slots: 285:5, 285:2, 287:5, 418:1, 418:2, and 407:1, followed by Florida Memory 432:0–432:6. Their exact stored URLs remain in `qa/media-recovery/wire_gate_targets_20261106.json` (audit; no browser status asserted).

The 13 WordPress originals over 1.5 MiB in the prior fresh media snapshot total **43,522,829 stored bytes**; these are not measured network-transfer bytes. Five large 1672×941 PNGs on posts 34–38 offer conditional **960×540** no-upscale derivatives. The two Malbone originals have existing WP 768px derivatives and demand historically faithful/map-zoom retention. Vasa photos are already Jetpack-resized and must be measured before reprocessing. All remain preview-only proposals subject to rights checks.

For *confirmed* broken images, restore only a verified same-image original from authoritative agency/archive item records (Navy, Coast Guard, Florida Memory, USGS, NASA, LOC), with item-level copyright/credits, accurate subject/date/crop, actual native size, and a **maximum 960px without enlargement**. If redistributable, request isolated WordPress **staging** media upload and preserve original alt text, caption, permalink and full-resolution archival zoom where necessary; verify mobile/desktop visual fidelity and cold wire size before asking for separate approval to publish. **No automatic rehosting, unlicensed scraping, risky block rewrites, or WordPress production writes.**

**Engineering lane:** existing media-recovery PR #1228. **Independent browser-QA lane:** existing PR #154. `docs/IMAGE-WEIGHT-WORKLIST.md` returned 404 on main and does not gate safe draft evidence work.
