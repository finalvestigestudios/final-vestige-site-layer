# Media recovery: oversized originals reconciled through first-party Jetpack paths

**Verified:** 2026-10-31. **Scope:** independent PR #183, no homepage design, Site QA PR #154, or production changes.

## Defect found in the previous offline oversized-image worklist

The frozen 2026-10-30 WordPress Media Library inventory contains **13 original image files >1.5 MiB**, totaling **43,522,829 original-storage bytes**. Its first-pass `referenced_inline_positions` field compares an exact media original URL to frozen Gutenberg `<img src>` values. **That exact-URL-only comparison undercounts inline use of first-party images routed through WordPress/Jetpack's `i0.wp.com` resize proxy.**

The earlier `oversize_960_plan_20261030.json` therefore classified six originals as not inline in the 61 published-post snapshot. The corrected conservative, path-and-origin-verified crosswalk identifies three as in use in the published Vasa investigation, post **299, “Thirty Men Were Enough.”** They were *already in the 355-image census* as first-party Jetpack proxy references; the 355-image count, the 288 stored offsite-source count, and PR #154's separate classifier do not change.

| Original media ID | Original bytes | Published source slot | Actual stored editor `src` (read-only CMS verification) | WordPress 1024-px variant |
| --- | ---: | --- | --- | --- |
| **389** | 2,822,969 | **299:0 (featured)** | `https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-01-2020.jpg?fit=1024%2C676&ssl=1` | Registered |
| **388** | 8,176,362 | **299:1** | `https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1` | Registered |
| **382** | 2,318,980 | **299:7** | `https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/vasa-med-gamla-och-nya-stottor_vasa-with-old-and-new-supports.jpg?fit=1024%2C683&ssl=1` | Registered |

**Vasa original-storage subtotal: 13,318,311 bytes.** These 1024px proxy `src` URLs do not prove successful browser GETs or that original-size binaries transfer. In fact, the proxy and existing responsive variants make immediate recompression a *lower* priority until the guest-browser waterfall is inspected.

## Highest-value 5-file source-only PNG batch

Authenticated, read-only WordPress **`media.get` and `posts.get(context=edit)`** independently confirmed the five large images listed below. All are **featured images AND the only inline `<img>` in their published article's stored editor content**. Each Media Library item is an AI-assisted historical reconstruction, with an original **1672 × 941** PNG, **empty `media_details.sizes`**, and a stored editor image explicitly sized **1024 × 576**. The article captions explicitly disclose their reconstructed nature; preserve that disclosure.

| Post ID / image key | Title | Media ID | Original bytes | Proposed conditional maximum (no upscaling) |
| --- | --- | --- | ---: | --- |
| **34 / 34:0** | The Morning San Francisco Lost Its Water | **39** | 2,892,087 | 960 × 540 |
| **35 / 35:0** | The Boat That Refused to Die | **40** | 2,552,136 | 960 × 540 |
| **36 / 36:0** | The City That Went Underground | **41** | 2,498,247 | 960 × 540 |
| **37 / 37:0** | How Petra Made Water Flow Through Stone | **42** | 2,488,823 | 960 × 540 |
| **38 / 38:0** | The Cisterns Beneath San Francisco | **43** | 2,836,245 | 960 × 540 |

**Five-source original-storage subtotal: 13,267,538 bytes (12.65 MiB).** This is a *source storage* subtotal, not an LCP/image-wire baseline or an achievable savings claim. Empty Media Library `sizes` is strong **CMS** evidence that no WordPress thumbnail derivatives are registered for these five items, but does **not** rule out live CDN responsive transformations. Because the five images occupy the first image block and are featured, they are sensible **LCP/visual-integrity testing candidates**. No LCP element, web-vitals timing, HTTP status, or actual transferred bytes were observed.

**WordPress source readback:** all six post IDs **34–38 and 299** are published. Posts 34–38 were last modified on **2026-10-29**, and post 299 on **2026-09-08**. Their `wp-image-{id}`, `src`, `featured_media`, recorded `width`/`height`, and reconstruction captions were checked read-only.

## Corrected 13-item prioritization

The safe source classification is now **10 originals used inline in the 61-post snapshot / three with no inline match**. Of the ten used inline: **five** are first-party PNG featured images with no registered WordPress sub-sizes (P1: verify guest-browser source/transfer first), **two** are Malbone JPEG originals with responsive variants (P2), **three** are Vasa first-party Jetpack-proxied originals with responsive variants (P2). The **three** not matched inline in the 61-post image census are media IDs **482, 405 and 293**, totaling **6,584,916 original bytes**. “Not in 61-post inline census” does **not** mean unused on the website, since products, author profile, featured media and other page types are out of scope.

### Implementation gates and staged WordPress media plan

1. **Guest-browser measurement first:** network-enabled, logged-out Chromium at 390px and 1440px. Record `currentSrc`, decoded natural size, final response URL, MIME, response status, transfer bytes, CDN cache, and LCP/CLS. Verify whether the five image elements actually fetch ~2–3 MiB PNG originals or negotiated Jetpack/WebP/AVIF derivatives; do not infer transfer from `media_details.filesize`.
2. **Prepare files only after clearance:** confirm the five reconstruction assets are owned/authorized to redistribute and derive. Obtain original file bytes through an approved WordPress export (no unlicensed scraping), calculate SHA-256, produce ≤960px-width variants without upscaling, compare visual quality and typography at 390px/1440px, and retain the **AI-assisted reconstruction** disclosure. A 960 × 540 display candidate is conditional, not an approved media rewrite.
3. **Stage first-party media under explicit approval:** upload separately named optimized media items on staging only after authorization; capture MIME, bytes, original hash, image quality, attribution, WP media IDs, generated responsive sizes and rollback mapping. **Do not overwrite originals, rewrite Gutenberg blocks, change `featured_media`, or alter live WordPress** in this lane.
4. **Release with before/after proof:** only consider a minimal reviewed WordPress post/featured-media edit if the guest-browser baseline indicates a real payload problem; separately test first-party proxy aliases in Vasa. Compare the same 390px/1440px pages and cold-cache network image bytes, LCP and CLS. Record a measured percentage only when both samples exist and match.

## Auditable code/data and safety

- `qa/media-recovery/oversize_inline_reconciled_20261031.json`: 13 original URLs and bytes, 10 exactly identified published-image slots, actual stored `src` strings, Jetpack aliases, 960px target dimensions, published featured-post evidence, and NULL actual browser/status/transfer/hash fields with explicit rights and CMS-write denials.
- `qa/media-recovery/validate_oversize_inline_reconciled.cjs`: recomputes every match from **all 355** original frozen image records. An `i0.wp.com` alias counts only if its *embedded original domain is exactly `finalvestige.com`*, path equals the original, `source_kind=jetpack_proxy`, and the query contains only an allowable `fit` resize and `ssl=1`. Rejects arbitrary third-party proxy paths, status fabrication, incorrect photo slots and permission claims.
- `qa/media-recovery/test_oversize_inline_reconciled.cjs`: 25 positive and adversarial regression cases; **25/25** successfully replayed against exact committed GitHub source bytes in isolated V8 using Node API shims. **Native Node CI and live browser QA were not performed.**
- Previous `oversize_960_plan_20261030.json` remains a frozen **direct-URL-only** snapshot for historical audit compatibility, not the final proxy-aware prioritization.

**Do not claim:** 42 guest-browser broken images; 76% measured image-weight savings; five live PNG fetches of full original bytes; rights to a source image; a live image repair. Current tooling cannot resolve `finalvestige.com` in its container, and public site retrieval is unavailable here. No production data, source photography, or homepage design assets were changed and there was no spending.
