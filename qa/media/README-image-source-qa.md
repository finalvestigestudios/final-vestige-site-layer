# Independent QA: published-article image-source resilience (source-level only)

**Status: DRAFT QA utility. No WordPress writes, site deployments, asset copying or network requests.**

## Finding (2026-10-30 UTC CMS read-only census)

The entire **61-post published** WordPress article set was inspected with authenticated `posts.get` in editor context. The stored Gutenberg content contains **355 inline `<img src>` references**. Of these, **286 (80.6%)** directly reference origins outside `finalvestige.com` or its own Jetpack WordPress.com image proxy (`i0.wp.com/finalvestige.com/...`, etc.).

The other **69** are directly first-party or first-party Jetpack-proxied references (including **7 Jetpack image-proxy references** in article 299). See `cms_image_census_20261030.csv` for the post-by-post counted snapshot, **not** a permanent content inventory.

Representative source observations:
- Post 268, *They Painted Over Archimedes*: **10/10** inline image URLs from offsite origins including Wikimedia Commons `Special:Redirect/file` links.
- Post 432, *They Buried the Dead Apart*: **7/7** images sourced from `www.floridamemory.com`.
- Post 407, *The Lake Wasn't There Yesterday*: **8/8** from an external Amazon S3 host.
- Post 434, *The Hatch Opened Inward*: **5/6** external images (including NASA image server).
- A separately inspected, published **podcast episode page 1484** embeds an artwork `<img>` with a `https://drive.google.com/thumbnail?id=...` source. This page is **not included in the 61-article, 355-image totals**.

**What this DOES NOT prove:** Broken images, invalid licensing, an actual slowdown, a failed public HTTP request, poor LCP, or a mobile browser defect. WordPress/Jetpack might rewrite or proxy sources at render time. An external source can be legitimate and highly reliable. The available independent HTTP runner cannot resolve `finalvestige.com`; no browser load, GET status or Core Web Vitals have been independently collected.

## Why review this

Final Vestige's archive-driven investigations depend heavily on visual evidence. A large dependency on third-party image hosts creates *potential* user-journey and archival-resilience exposure to changed source URLs, referrer/hotlink rules, origin outages, redirects, image transforms, and mobile latency. It also makes licensing/attribution review essential **before** moving any assets.

## CLI (read-only; deliberately offline)

```bash
node --test qa/media/test_source_image_dependencies.cjs
node --check qa/media/source_image_dependencies.cjs
node qa/media/source_image_dependencies.cjs /path/to/sanitized-published-article-snapshot.json
```

Snapshot schema:
```json
{"pages":[{"id":268,"url":"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/","content":"<img src=\"https://commons.wikimedia.org/wiki/Special:Redirect/file/Example.jpg\" alt=\"Illustration\">"}]}
```

The script classifies `first_party`, `jetpack_proxy`, generic `external`, `redirect_image`, `drive_thumbnail`, `non_http`, and `missing_src`. It marks pages for **source REVIEW** when at least 4 images exist and at least 75% are offsite. Its result always says `http_verified:false` and has no FAIL/BROKEN-image assertion. Input size, record count, and image count are bounded; raw Gutenberg snapshots and any authenticated WordPress data should stay off GitHub.

The snapshot CSV is an aggregate only. The count excludes `<picture><source>`, `srcset`, CSS backgrounds, featured images loaded outside post body, lazily injected images, and links inside scripts. URL rewriting by Jetpack or the live theme may change the browser-level dependency.

## Required next browser checks (without editing production)

1. Visit a representative set in a logged-out mobile browser, especially articles 268, 432, 407, 434 and the published podcast episode page 1484; include one article with primarily first-party sources for comparison.
2. Collect browser image `complete`/`naturalWidth`, failed requests, actual network URLs after Jetpack transformations, LCP/CLS and load waterfalls on constrained mobile data. Record specific failing image URLs privately for triage, not publicly in tickets if they include auth tokens.
3. For any **verified** failed or slow image, review provenance, reuse licence, attribution, hotlink restrictions, and preservation rules. Only then propose a *specific, authorized* replacement or image cache workflow, preserving existing permalinks, captions and credits. Do not bulk-copy third-party images.
4. Re-run this checker on fresh sanitized editor snapshots when Claude's editing pass is complete. Keep all findings separate from the Focus subscriber funnel and the existing Heading/SEO/Field Cabinet draft PRs.

No changes to homepage, navigation, Focus Fieldbook, Dispatch, PDF, plugins, subscriptions, user accounts, themes or published editorial content.
