# Media Recovery: 66-post live metadata and 12-post/77-image P0 crosswalk (2026-11-17)

**Status: review-only. No production changes, downloads, cached copies, rehosting, Gutenberg rewrites, merge, deploy or spend.** Separate from homepage visual design and Site QA draft #154. This is an incremental batch on draft Media Recovery #2747.

## What was actually inspected

The authenticated WordPress **published-post listing** returned **66 published posts in one complete page**. Fresh WordPress **VIEW** reads, checked against the list's modification timestamps, were completed for 12 selected posts: **285, 287, 407, 418, 268, 432, 299, 291, 213, 434, 292, 1926**. These contain **77 inline `img` tags**. This is **NOT** a 66-post live image audit; the other 54 post bodies were not fetched this sprint.

Of 77 selected images, **57** had a Jetpack proxy wrapping a third-party origin, **11** were direct third-party URLs, and **9** were first-party origins wrapped by Jetpack. There were **35** distinct embedded/direct source hosts. **61/77** did not have both explicit `width` and `height` attributes in WP VIEW markup. These are markup-only findings; theme/runtime output can differ. The 61-post/355-image historical inventory and 66 current posts are **different denominators**, not a before/after weight test.

[Current-published URL and per-slot machine census](../qa/media-recovery/live_twelve_post_view_crosswalk_20261117_1026pt.json) freezes exact 66 metadata rows, all 77 current VIEW `src` URLs, the six established P0 source slots, geometry flags, null guest HTTP/decode/bytes and max 960px/reuse holds. Its Jetpack embedded-host/path field is an *inference*, not a recovered exact authored source URL. The [six-slot primary-source/rights matrix](../qa/media-recovery/p0_six_official_rights_crosswalk_20261117_1026pt.json) separately records catalog-level leads.

## Six priority source dependencies, freshly read from WP

| Slot | Published Jetpack-embedded host | Primary-source next action |
|---|---|---|
| 285:5 | `images.saymedia-content.com` | No approved same-frame movie-still substitute; hold rights |
| 285:2 | `blog.ucsusa.org` | Preserve UCS Figure 4/NRC test-tag semantics; NRC backgrounder is context **only** |
| 287:5 | `stpetecatalyst.com` | Publisher relocation previously identified; copyright/University Press of Florida credit unresolved. Florida Memory **RC09237 is a different frame**, not an automatic substitute |
| 418:1 | `media.defense.gov` | USCG official accession **VIRIN 210330-G-DE713-0002** is a strong catalog match. [USCG item](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) marks it public domain and cleared for release, with credit/DoD-use constraints. Verify exact pixels/crop |
| 418:2 | `www.history.uscg.mil` | [National Coast Guard Museum 1946 Scotch Cap article](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) contains relevant credited debris images. Exact frame/master still unverified; 600×463 prior preview must never be upscaled |
| 407:1 | `d9-wret.s3.us-west-2.amazonaws.com` | [Official USGS 1959 fault-scarp catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) credits J. R. Stacy and marks image public domain. Compare exact file/frame to old S3 route before staging |

An [official Florida Memory RC09237 record](https://www.floridamemory.com/items/show/32083) depicts a car near the May 9, 1980 bridge failure, unlike the present slot 287:5 color bridge-and-ship photograph. Custody, identity, rights and image purpose must not be conflated. No catalog lead establishes a successful *visitor* image load. Previously recorded independent source-retriever 403/404/redirect observations are not equivalent to cold guest Chromium failures, especially through Jetpack.

## Release and replacement protocol

1. **Prove the breakage in Site QA's existing collector, do not clone it.** Request cold logged-out mobile and desktop `currentSrc`, actual GET status/MIME, redirect chain, nonzero `naturalWidth/naturalHeight`, successful decode, screenshot, and CDP network received bytes for six P0 slots. Record direct-origin response separately from the Jetpack URL actually displayed to the visitor. Preserve source/caption exactness and failures.
2. **Rights and scene fidelity first.** Confirm item-level attribution/reuse permission or a clearly supported public-domain notice, photograph author/credit, exact subject/time, original master URL and SHA-256, crop/framing, native dimensions, and any rights restrictions. RC09237 and NRC context are **not** authorized same-photo replacements. Where rights are unclear, do not copy the binary.
3. **No-upscale derivatives only after approval.** Use `target_width=min(native_width,960)` pixels; `target_height=round(native_height*target_width/native_width)`; never convert text-heavy scans/maps to destructive formats without a readability review. Known 600px source stays at 600px maximum, not 960px. No numerical width/height is claimed for unknown original masters.
4. **Reversible WordPress staging plan, not permission to execute it.** For explicitly cleared exact images, create a staging-only WordPress Media attachment with documented credit, SHA-256, item license and source URL; verify `srcset/sizes`, MIME, original-caption parity, lazy loading, mobile crop and accessibility. Map old source slot to new Media ID in a manifest; keep original rendered markup and a rollback path. Do **not** bulk-search/replace Gutenberg post content or mirror third-party source galleries.
5. **Re-measure performance honestly.** Compare paired cache-disabled, service-worker-bypassed logged-out mobile samples at identical viewport/DPR/post revisions and full lazy-load coverage. Count distinct actual image network GETs once, while preserving each DOM slot. Compute `100*(before_actual_image_wire_bytes-after_actual_image_wire_bytes)/before_actual_image_wire_bytes`, using real image bytes—not original library file sizes. Require both historical 61/355 slot parity and visual evidence before declaring a 76% *historical-cohort* result; separately audit current 66 posts before calling anything site-wide.
6. **Oversized originals are not page weight.** Historical WordPress inventory had **20 originals >1.5 million bytes / 64,385,752 stored bytes**; only selected originals were actually referenced inline. Vasa post 299 is an appropriate next cold-transfer candidate, but actual delivered variant and byte savings are still unknown.

## Tests and evidence boundary

[Offline validator](../qa/media-recovery/validate_live_twelve_post_view_20261117.cjs) and [17-case regression suite](../qa/media-recovery/test_live_twelve_post_view_20261117.cjs) enforce post/revision/slot identity, derived Jetpack host fidelity, strict 66/12/77 and 57/11/9 counts, historical-savings HOLD, no fake visitor HTTP, no granted copying rights, and no >960px derivative. **17/17 cases passed in isolated V8** against the exact authored validation function and current GitHub JSON. Native Node and repository CI were not run; no guest browser screenshots or real transfer bytes were obtained.

All files live only on the unmerged Media Recovery draft branch. Hand off this current-source index to Site QA #154 without modifying that team's existing collectors, snapshots or drafts.
