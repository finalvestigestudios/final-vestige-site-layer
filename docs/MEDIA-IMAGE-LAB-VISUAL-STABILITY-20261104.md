# Media Recovery — document-start image performance evidence, Nov 4 2026

**Scope:** Source-only draft PR #183. Independent of homepage visual design and Site QA draft PR #154. **No production WordPress post/media/theme writes, image downloads/rehosting, copyright assumptions or expenditure.** This addendum is an instrumentation change, not evidence of improved live performance.

## Problem and impact

The 61-post / 355-inline-image inventory and prior read-only WordPress inspections exposed many unsized historical images (e.g., TMI post 285: 6/6 absent width/height; AZORIAN post 218: 6/6 absent width/height). Missing intrinsic HTML dimensions create a **potential** layout-shift risk but do not prove any measured layout shift. Previous `browser_probe_chrome.cjs` produced image network transfers and decode status but no actual layout-shift or LCP observation. Thus no credible attribution between optimized media and visual stability was available.

The site-wide starting figures are still **61 published posts, 355 stored inline image slots, 288 externally sourced references, and 13 first-party WordPress originals larger than 1.5 MiB (43,522,829 original storage bytes)**. The historical claim of **42 broken images is not proven in a logged-out guest browser**; the reported **76% image weight reduction is not measured in actual browser transfers**. **Production images repaired: zero.**

## Implemented (isolated)

- `qa/media-recovery/lab_visual_metrics_20261104.cjs`: early, buffered `PerformanceObserver` for `layout-shift` and `largest-contentful-paint`. No image URLs, user text, cookies, auth or binary/image content are collected. Observers keep a capped 20-item shift diagnostic sample and simple changed-element tags only.
- **CLS-style lab session-window diagnostic:** shifts with `hadRecentInput` excluded; 1-second maximum inter-shift gap and 5-second maximum session span; preserve both maximum session score and cumulative raw shifts. These numbers are explicitly **lab** diagnostics and cannot be advertised as actual visitor CWV/75th percentile.
- `qa/media-recovery/browser_probe_chrome.cjs`: uses `Page.addScriptToEvaluateOnNewDocument` before navigation; captures **after initial 1.8-second navigation settle** and **after automatic full-page lazy-image scroll** separately. The former is the initial-navigation sample; the latter includes scripted scrolling and must never be represented as genuine user experience.
- Missing/unavailable observer, CDP injection failure, or unverified page remains `UNVERIFIED`/null rather than a made-up 0. `field_cwv_claim_permitted` is always false. These lab metrics are attached to the existing P0 queued browser probe; no second browser QA workflow or Site QA draft was added.
- `qa/media-recovery/test_lab_visual_metrics_20261104.cjs`: 15 native Node deterministic scenarios covering observer support, input exclusions, max session windows, URL/text privacy, read-only snapshots, document verification gates and LCP image recognition.

**Primary measurement references:** [web.dev CLS session window: 1-second gap, 5-second cap](https://web.dev/blog/evolving-cls); [web.dev layout-shift debugging](https://web.dev/articles/debug-layout-shifts); [web.dev LCP observer guidance](https://web.dev/articles/lcp); [MDN Performance Observer](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceObserver).

## QA evidence and limitations

- Local Node.js v22 test fixture matching the committed observer logic: **15/15 PASS**; exact committed module/runner parsed in isolated V8, with **13/13 positive source-code and observer-behavior assertions PASS**. Native Node CI against the remote PR commit and live logged-out Chromium scan remain pending.
- This execution environment cannot resolve public DNS. Accordingly there were **zero real logged-out FinalVestige browser sessions**, **zero actual HTTP image/status/byte/CLS/LCP captures** and **no grounds for declaring any of the six P0 suspicious originals browser-broken**.
- Potential layout shift from unsized images is not synonymous with actual CLS. Final lab numbers will require real Chromium navigation and scans and must be interpreted as one controlled session, not a traffic distribution.

## Next guest-browser handoff (owned by Site QA #154)

Maintain the existing order: **TMI 285:5 → TMI 285:2 → Skyway 287:5 → Scotch Cap 418:1/418:2 → Hebgen 407:1**. Use media's existing `browser_probe_chrome.cjs` (`--plan`, then default priority mobile and `--desktop`) on a network-capable runner. For each image obtain guest `currentSrc`, final CDP Image status, MIME, natural dimensions, redirects, encoded transferred bytes, viewport, `visual_lab.after_navigation` and `visual_lab.after_automated_scroll`; only real image failures should enter the repair queue.

Then select an exact historically faithful and rights-cleared replacement from the already indexed USCG/USGS/Navy/Florida Memory/NRC/publisher candidates, proportionally resize to **≤960 px without enlargement**, retain item-specific credit, stage in WordPress media after explicit release (not in this lane), confirm no visual degradation, and compare cold same-browser before/after media bytes and lab layout metrics. **Do not automatically copy third-party images, rewrite Gutenberg blocks or modify homepage CSS.**

The original source/rights/960px queue remains [P0 release gates](../qa/media-recovery/p0_attribution_release_gate_20261104.json); media-size inventory remains [oversize originals](../qa/media-recovery/oversize_originals_20261030.json); the risk and evidence ledger is [IMAGE-WEIGHT-WORKLIST](IMAGE-WEIGHT-WORKLIST.md).
