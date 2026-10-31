# Experience 2.0 — archival media delivery and native WordPress staging hold

**Scope:** Existing **seven-chapter** flagship homepage at source head inherited from draft PR #254 (Franklin editorial folio), plus read-only WordPress media discovery on 2026-10-30 PT. This patch is isolated and stacked, not deployed. PR #49 remains frozen. No new chapters, image sources, webfonts, subscriptions, merchant links or rights claims.

## Before / after — actual source properties, NOT measured network timing

| Image | Before | This branch | Original WordPress upload metadata |
|---|---|---|---|
| Apollo 1, WP media #473 | `loading=eager`, `fetchpriority=high`, 1041-pixel single-source image | `loading=lazy`, no high priority; 300/768/1024-pixel verified WordPress CDN variants | 1041×810, 78,346 bytes |
| Victory Point Note, WP media #474 | `loading=lazy`, single 960×1526 JPEG source | `loading=lazy`, 189/644/768/960-pixel verified WordPress CDN variants | 960×1526, 466,043 bytes |
| 1903 NYPL map, WP media #1258 | Already `loading=lazy`, 768/1024/1536-pixel WP CDN variants | Unchanged, exact source and art unchanged | Original 5667×3831, 5,553,669 bytes |

**Why:** After PR #254 replaces abstract hero decoration with CSS-only source-derived folio, the first historical-image card is farther down the page. Eager/high-priority Apollo image competes with first-screen resources without being the page's central visual. Responsive derivatives preserve the published source URL in `src` and its exact source-manifest mapping while giving modern browsers size-appropriate image choices. WordPress media IDs and derivative dimensions above come from *connected WordPress media.get* on 2026-10-30; they prove metadata, **not HTTP delivery or compressed transfer bytes**.

The URLs under `i0.wp.com/finalvestige.com/wp-content/uploads/...` use existing Jetpack CDN delivery already used by the NYPL card. No new external dependency or JavaScript. The canonical original `src` of all three images, their alt text, inherent dimensions, and their source/limitations ledger remain intact. No product links added.

## Must measure before shipping

1. After authorized native WordPress.com staging clone, check *staging* site ID, hostname, access mode, and `WP_ENVIRONMENT_TYPE=staging`. Current connected site enumeration returned **only production site ID 256784396**, with **no accessible staging entry**.
2. On an explicitly authorized private staging host, serve the *exact* unpublished HTML from the approved sealed renderer. Use its source-hash admission from PR #250; verify file/commit SHAs. **Do not use the public-asset preview builder in PR #212.**
3. Run committed offline exact-head Chromium CSP/interaction gate from #252, then actual staging browser admission. Capture 320/390/768/1440/1920px, 200% zoom, keyboard/no-JS, responsive image `currentSrc`, `naturalWidth`, HTTP 200, content-type, transferred bytes, timing and failed requests. Browser image selection after interaction must work for Apollo, Franklin and NYPL.
4. Run axe (fail-closed if unavailable), manual WCAG 2.2 AA screen-reader/keyboard/touch and Safari checks, Lighthouse **on real staging**, and report laboratory LCP/CLS separately from p75 real-user CWV. Preserve screenshots and before/after network HARs.
5. Independently review archival source-use rights: RMG record HSR/C/9/1 supports the two Franklin entries but is **not** itself a license for reproducing photographs; Wikimedia Commons Franklin file provenance must be checked. NASA Apollo publication guidelines restrict implied endorsement. NYPL individual-item license remains unresolved. No rights approval has been granted by this change.
6. Hosted CI and independent QD must pass at final exact SHA; founder must explicitly approve staging install/activation and later separately approve production release.

## One required platform action (not performed by this engineering lane)

The founder can create WordPress.com's **native clone** from Hosting Dashboard → select site → Production environment dropdown → **+ Add staging site**, where supported by the plan. Do not substitute a new unrelated website or create a staging environment via production plugin installation. Staging shares storage allowance; clone/synchronization can change content and subscriber databases. **Never sync staging database into production.** Site discovery should be repeated after the founder's action; no production CMS writes are authorized.

**State: RELEASE HOLD.** Responsive markup is not a measured performance win until actual staged image-network and Lighthouse evidence exists. All seven chapters, three art directions, 52-page Focus Fieldbook, Jetpack signup and live 72 Margins remain unchanged. 
