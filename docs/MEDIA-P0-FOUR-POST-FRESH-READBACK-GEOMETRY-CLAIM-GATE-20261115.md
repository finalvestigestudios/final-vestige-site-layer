# Media Recovery: fresh P0 WordPress source crosswalk and 960px evidence gate — 2026-11-15 PT

**Scope:** independent Media Recovery draft PR #183 only. Site QA #154 owns existing cold-guest-browser collector; the interim lead owns homepage visuals. Read-only source verification and isolated QA only; **no production WordPress writes, copied third-party binary, derivative, subscription spend, merge or deployment**.

## Verified live WordPress EDIT/VIEW crosswalk

Read `posts_get` in both EDIT and VIEW contexts on published post IDs **285, 287, 407, 418** (eight authenticated read-only requests). All image-slot counts and post modification timestamps matched across both contexts:

| Post | Inline images | Modified | P0 slots |
|---|---:|---|---|
| Three Mile Island 285 | 6 | 2026-11-02T21:39:59 | 285:2, 285:5 |
| Sunshine Skyway 287 | 6 | 2026-11-02T21:40:01 | 287:5 |
| Hebgen 407 | 8 | 2026-10-29T18:30:30 | 407:1 |
| Scotch Cap 418 | 6 | 2026-08-28T03:11:08 | 418:1, 418:2 |

**All six P0 editor-image URLs and six WordPress-view URLs match the prior exact-source audit**, with the view URLs routed through Jetpack. These are **actual published WordPress content values, NOT network response status, cold-browser `currentSrc`, decoded geometry or measured traffic**. Guest status and origin/Jetpack HTTP status remain `null`. No guest-browser break is claimed for the 42 reported suspects; no actual 76% transfer savings is claimed.

[Machine-readable six-image fresh source/rights/status-null readback](../qa/media-recovery/p0_six_fresh_wp_readback_20261115_1131pt.json) carries the **12 exact editor/view URLs**, post timestamps, primary-catalog leads, explicit rights/visual holds, conditional `min(nativeWidth,960)` no-upscale dimensions, and the post 418:5 `?itok=ASMRCahz` editor-to-view query drop. The query discrepancy is an identity risk, **not a verified user-visible failure**.

## Corrected fail-closed validator

The preceding `validate_wp_view_proxy_26_20261115.cjs` checked whether candidate `native_px` and `review_px` were both populated, but did not validate numeric dimensions, preserve aspect ratio, enforce 960px/no-upscale review, or recompute all route/attribute summary counts. A malformed or stretched “review derivative” could have passed. It also did not reject a changed `reported_broken_guest_verified`, `measured_76_percent`, paid-spend, merged or deployed flag.

The updated guard now verifies both dimensions are positive safe integers, width is exactly `min(960,nativeWidth)`, proportional height is rounded, neither URL nor ALT is silently missing, width and height are paired, responsive declarations are not invented, six P0 rights assertions remain false, all 26 source slots still reconcile to the four post manifests, and all source route/dimension/count totals are calculated from rows rather than trusted blindly. It rejects fabricated guest status/76%-savings release claims and any encoded production work.

**Validation evidence:** 20 intentionally unsafe mutations were rejected and the original full 26-row snapshot was accepted using a V8 harness with exact source-function text verified against the committed GitHub blob (all six relevant functions byte-identical). A 20-case regression expansion was added to the native Node test file. Native Node execution, repository CI and logged-out Chrome were **not** performed and are not claimed.

## Priorities and safe reversible plan

1. Site QA #154 runs its existing cold, logged-out browser capture on the **Jetpack view URL**, not just the external editor original. Record actual `currentSrc`, CDP image GET/redirect chain, response, cache flags, `naturalWidth/Height`, screenshot and transferred bytes.
2. Confirm exact-scene identity and archive-item rights/credits before copying a photograph. USCG [Anthony Pettit catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) identifies a public-domain/cleared-release photo but binary identity and reuse review remain separate. Florida Memory RC09236 depicts the **1980 aftermath** and is **not automatically the same** image as the old-and-new bridge view. The candidate for 285:5 is 819×614 while the published original used a 16:9 crop; avoid silent change in visual narrative.
3. Only after confirmed failure and rights approval, make a **staging-only** WordPress Media Library replacement, with `width=min(960,nativeWidth)`, proportional height, no upscale, credited catalog link and rollback identity mapping. Check fine labels and crop on desktop/mobile before any separately authorized publication.
4. Attribute transferred-byte changes only to verified cold-cache matching 61-page baseline/candidate runs using completed Image CDP event chains; a 76% projection is not evidence.

Baseline remains **61 posts / 355 stored inline images / 288 external-origin dependencies**, distinct from the newer live 66-post inventory. Last verified WordPress media inventory: **132 images, 20 stored originals over 1.5 decimal MB totaling 64,385,752 original bytes**; stored originals are not image wire bytes. No full guest-browser confirmation of the 42 reported broken external media yet.
