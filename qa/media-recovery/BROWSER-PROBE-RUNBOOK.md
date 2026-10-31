# Browser proof & authoritative-asset addendum — media recovery
**Status:** draft, non-deployed. Complements media recovery PR #183 and Site QA PR #154; does not alter Gutenberg content, images or the homepage.

## What this batch adds
The site-wide 61-post/355-reference audit has only **source URL** data, not a visitor browser waterfall. The new pure functions and tests explicitly distinguish `currentSrc` from stored `src`, unravel `i0.wp.com/THIRD_PARTY_HOST` without misclassifying its origin, preserve redirect-chain attribution, and require an actual failed browser request AND `naturalWidth === 0` to label a broken image. Unmapped, lazy, ambiguous-alt, web viewer 403 and inaccessible audit runner are NOT evidence of visitor breakage. Tests use Node's built-in runner (no packages or spend).

The six newly reviewed official media records in `primary_source_addenda_20261030.json` cover Coast Guard Scotch Cap (418:1), two Navy USS Tang assets (274:4 and 274:5) and three USGS Hebgen Lake / Madison Slide photographs (407:2, 407:3, 407:7). Five are new image keys; 418:1 supplements an existing catalog record with explicit release/caption details. Every row includes the **actual stored source URL**, record citation, catalog ID, meaningful level of identity confidence, attribution, rights-not-fully-cleared gate and the maximum 960px / no-upscale requirement. No image was downloaded, optimized, uploaded or substituted.

## Source-specific editorial precautions
- Official [USCG image record](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) says the photo 210330-G-DE713-0002.JPG is public domain and cleared for release, but requires appropriate credit and DoD guidance. The gallery uses **Pettit** while [a Coast Guard museum article](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) also lists **Petit** in a memorial roster. This is an unresolved textual discrepancy—not grounds for an automatic change.
- [NHHC 80-G-344565](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/wwii/wwii-pacific/japanese-surrender/allied-prisoners-of-war/80-g-344565.html) and [NHHC 80-G-227991](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227991.html) corroborate specific original catalog IDs.
- [USGS Madison Slide 1959](https://www.usgs.gov/media/images/view-madison-slide-august-21-1959-rapidly-filling-earthquake-lake), [USGS dragline 1959](https://www.usgs.gov/media/images/dragline-working-lower-outlet-channel-earthquake-lake-october-18-1959), and [USGS Earthquake Lake 2023](https://www.usgs.gov/media/images/earthquake-lake-and-madison-slide) each state Public Domain and supply photographer credit; all still require exact image match and audit of derivative rendition.

## Verification gates, in priority order
1. **Logged-out browser** loads P0 posts 268, 432, 418, 407, 434 and 621 at mobile 390px and desktop 1440px, scrolls lazy images into view, and captures a HAR or CDP waterfall, actual response/redirect/content type, `currentSrc`, `naturalWidth`, and before screenshots. Tool failure in this runner MUST appear as `environment_blocked`, not 42 broken images.
2. Cross-match every failure to exact `image_key`. Verify license and exact same historical photo, editorial dates/subjects, attribution and institutional caveats. Get human release approval before media upload or block edit.
3. When cleared, resize without upscaling to **max 960px** width, retain aspect ratio, produce responsive variants/alt/credit, retain original SHA-256 and media item ID, test logged-out mobile/desktop and no-JS. NEVER hotlink through a new proxy to evade access controls.
4. Compare identical page/viewport/cache mode **actual browser image transfer bytes** (prefer Chrome Network encoded wire bytes) and LCP/CLS before vs after. A claimed 76% reduction needs `100*(baseline_image_bytes - new_image_bytes)/baseline_image_bytes`; Media Library originals (13 over 1.5MiB) cannot serve as transfer baselines.

## Offline checks
`node --test qa/media-recovery/test_browser_probe_core.cjs`. Separate original tests: `node --test qa/media-recovery/test_validate_inventory.cjs`.

**Restrictions:** no production WordPress writes, no unlicensed scraping, no subscriptions, no speculative posts or CSS edits. Only PR review and evidence collection.


## v3 decoded-image source proof / reproducible weight gate

The probe output is now `probe_version: 3`. Run from the repository root on a **network-enabled**, logged-out Chromium system with **no WordPress production writes**:

```sh
node --test qa/media-recovery/test_browser_probe_core.cjs qa/media-recovery/test_browser_probe_commons.cjs qa/media-recovery/test_browser_probe_active_src.cjs qa/media-recovery/test_compare_wire.cjs
node qa/media-recovery/browser_probe_chrome.cjs --plan
node qa/media-recovery/browser_probe_chrome.cjs
node qa/media-recovery/browser_probe_chrome.cjs --desktop
```

Use `--all` only after bounded P0 verification. Collect unmodified JSON results and screenshots; browser status, decoded `currentSrc`, natural dimensions, response MIME/redirect, encoded bytes, viewport, and cache settings are required evidence. For each stored slot, a matching `src` or `data-src` is **not sufficient** if `currentSrc` differs. `current_src_identity_unverified` means editorial/source identity needs review, **not broken**. The browser request must match `currentSrc` and its network record.

The paired-run comparator now refuses v2 evidence and requires every loaded slot's claimed response size to match an actual Image-network row (including known redirect aliases). Do not claim the 76% reduction or 42 browser failures from the source census, CDN viewer, WordPress original bytes, synthetic tests, or network-only failures. A meaningful before/after still needs matching scope, browser version, viewport, screenshots and visual/rights signoff; a comparator passing alone is not a deployment approval.

## Full-height scroll acceptance requirement (October 31, 2026)

The old probe could stop at 36 × 720px = 25,920px, leaving unvisited lazy images on sufficiently tall pages. The revised browser runner reevaluates scrollHeight, scrollY and innerHeight on every step and uses instant 720px scrolling, capped at 120 steps and 80,000px of document height. This does not claim that any particular published post exceeds the old budget.

A page without demonstrated bottom coverage is labelled inspected_browser_partial_scroll. Raw evidence includes scroll_coverage.complete, state and reason. Partial-page confirmed_broken_count and image_wire_bytes_total remain null, and site-wide counts remain null if any page is incomplete. The paired image-wire comparator now refuses missing or incomplete coverage. Test the new controls with: node --test qa/media-recovery/test_scroll_coverage.cjs qa/media-recovery/test_compare_wire.cjs . Neither source-only checks nor synthetic tests prove the original 42-broken or 76%-reduced claims.

## Exact DOM-slot screenshot evidence — October 31, 2026

Older screenshot generation identified an image with `findIndex` by its network/source URL. Teton post 291 has two slots referencing the same image URL but different historic ALT descriptions, so the earlier logic would screenshot the **first** occurrence for both. Now every classified image retains `rendered_index` and `rendered_alt`. `selectScreenshotTarget` requires the exact indexed element, `src`, decoded `currentSrc`, ALT, completed state and zero natural width to remain identical **after** scroll-to-element; otherwise the screenshot records `skipped` with a specific reason. This avoids false visual evidence if the DOM reorders or the image recovers. The bounded per-post screenshot limit is 24, with explicit attempted/captured/omitted counts. No unrelated homepage work, image mirroring, or CMS write is performed.

Run offline regression: `node --test qa/media-recovery/test_screenshot_targets.cjs qa/media-recovery/test_teton_visual_guard.cjs qa/media-recovery/test_browser_probe_core.cjs`. Reproduce logged-out screenshots only in a network-enabled Chromium environment. A captured screenshot supports **that exact image slot only**; it never establishes an image license or 76% measured weight reduction.

## Final CDP redirect URL is distinct from browser `currentSrc` — October 31, 2026

A decoded image is not necessarily the intended photograph: HTTP redirects can deliver a different image while the DOM keeps the originally requested `currentSrc`. The v3 browser probe now emits `network_final_identity_verified` and `redirected_image_identity_unverified` for each matched image. Triage every `redirected_image_identity_unverified` against the final CDP URL, redirect aliases, exact catalog ID, photograph/caption and rights evidence; **do not** count the original photo as loaded, broken or replaced merely because the final response was HTTP 200. Commons canonical redirect to the same hashed file and NHHC same-`image=` rendition changes can be identity-equivalent; a different Navy `image=` ID is not. The independent image-census layer also checks stored URL → decoded URL → final request URL before definitive loaded totals, while confirmed visual 404/HTML decode failures retain their separate evidence paths. Run regression via `node --test qa/media-recovery/test_network_redirect_identity.cjs qa/media-recovery/test_image_census_coverage.cjs qa/media-recovery/test_browser_probe_core.cjs qa/media-recovery/test_compare_wire.cjs`. **No network/browser observation was produced by these tests.** See `docs/MEDIA-REDIRECT-IDENTITY-20261031.md`.
