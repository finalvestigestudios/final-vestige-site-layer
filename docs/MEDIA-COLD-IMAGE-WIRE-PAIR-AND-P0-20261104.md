# Media Recovery: cold-browser image-wire comparison + P0 source recheck (Nov 4 Pacific / Nov 5 UTC)

**Independent media lane, draft PR #183. Not a production repair or a claim of 76% measured savings.**

## What changed

Added `qa/media-recovery/compare_cold_image_wire_v1.cjs`, an **offline**, read-only, zero-dependency Node 22 comparator for *two actual output JSON files* from existing `qa/media-recovery/browser_probe_chrome.cjs`. Run:

```sh
node --test qa/media-recovery/test_compare_cold_image_wire_v1.cjs
node qa/media-recovery/compare_cold_image_wire_v1.cjs BEFORE.json AFTER.json > measured-pair.json
```

The CLI writes SHA-256 of each input file into the machine-readable result. It does **not** access the network or contact WordPress.

A `LAB_PAIR_MEASURED` result requires matched post URLs and complete article image-slot identities; identical viewport, browser product, run profile and mode; a complete 0-broken-image census on both sides; a full-height scroll; uncached and service-worker-bypassed image responses; and a decoded, successfully identified DOM `currentSrc` bound to a unique CDP **Image requestId**. For each request, independently reconcile HTTP 200, `image/*`, encodedDataLength and the page's already-attributed article wire-byte sum. Count a reused request only once. Extra same-photo preloads/retries, missing slots, partial lazy images, differing post sets, bogus status or stale caches => **HOLD**, not zero bytes. Recompute the aggregate as **(sum baseline encoded CDP bytes - sum candidate encoded CDP bytes) / sum baseline encoded CDP bytes × 100**, without using WordPress stored-original sizes or summing duplicate slots. The result contains exact before/after published URLs, `currentSrc`, status, individual request IDs and encoded bytes, plus post-level nonduplicated totals. Individual slot bytes are explicitly nonadditive if slots share a network request.

**Important:** A single valid pair is laboratory evidence for the *same measured post set*, not a production-wide 76% result. The comparator always returns `sitewide_76_percent_claim_permitted:false` and `production_repair_claim_permitted:false`. To support a broader site-wide claim, first reconfirm the current number of published articles and complete all of their image slots, gather multiple stable cold runs on both mobile and desktop, compare like-for-like before/after content with authenticated source provenance, and report the distributions and any regressions. Field LCP/CLS require separate real-user evidence. Lossy image-format transformations, captions, historical labels and reuse rights still require human visual/editorial review.

**Source integrity:** exact locally native-tested file Git blob SHA `4e9566fd43719938c9f2c110c5f34bdcec12b83f`; test blob SHA `0ceea1a34d2f2ff157c8d557d6800e9625787d51`. **21/21 native Node 22 tests passed**, including a synthetic 1000 → 240 = 76% example (synthetic numbers, **not site metrics**); cached responses, unbound preloads, altered source slots, mismatched CDP IDs and invented sums all fail closed. CI in GitHub still needs an independent run.

## Four retriever observations on unchanged live P0 source URLs

[Machine-readable six-source source/retriever/rights ledger](../qa/media-recovery/p0_retriever_source_recheck_20261104.json), based on the already independently read-back six current WordPress image URLs, was rechecked Nov 4 Pacific. These are **retrieval-tool responses only**, not browser/network HTTP statuses.

| Exact live image key | Tool observation on original URL | Production diagnosis |
| --- | --- | --- |
| 285:5 — Three Mile Island image | Not checked this batch | Unknown |
| 285:2 — UCS image | Wrapper 500 after `blog.ucsusa.org` redirects toward inaccessible `blog.ucs.org` URL | Visitor status unknown |
| 287:5 — Sunshine Skyway image | Wrapper 404 on old St Pete Catalyst WordPress path | Visitor status unknown; source migration suspected |
| 418:1 — Scotch Cap portrait | Not checked this batch | Unknown |
| 418:2 — Scotch Cap debris | Wrapper 403 on USCG original path | Visitor status unknown |
| 407:1 — Hebgen Lake USGS image | Wrapper 400: octet-stream unsupported by retriever | Visitor status unknown; browser may decode it correctly |

No actual guest-browser `currentSrc`, image GET/redirect status, decoded pixels, CDP encoded bytes or LCP/CLS was obtainable from this runner: outbound DNS for the public site is unavailable. The 42 originally reported broken images are still **not confirmed as 42 visitor-visible failures**. Avoid mass mirroring or blanket block rewrites.

## New Florida archive candidate for Sunshine Skyway 287:5

A catalog crosswalk identified **Florida Memory item 131903**, `View of the old and new Sunshine Skyway bridges from St. Petersburg, Florida, 1987`, photographed by **H. Milo Stewart**. The Commons rendition is **600 × 595 JPEG**; its creator/date/source and the Commons contributor's CC0 declaration are documented at the Commons file page. The primary Florida Memory item URL returned a retrieval-wrapper 403, so **the master geometry, rights basis and attribution need review at the primary record**. It is only a **different photograph on the same subject**, not the identical Skyway documentary image currently embedded. Its provisional derivative ceiling is **600 × 595** from the 600px rendition; don't enlarge it to 960px. Do not silently swap content because the current ALT references the old wreckage and replacement.

Primary record: https://www.floridamemory.com/items/show/131903

Secondary catalog: https://commons.wikimedia.org/wiki/File:View_of_the_old_and_new_Sunshine_Skyway_bridges_from_St._Petersburg,_Florida,_1987.jpg

**Rights and WordPress release gate remains HOLD**: exact visual equivalence versus editorial alternative; per-item photographer/ownership permission for commercial reuse and required credit; legitimately obtained source file SHA-256, genuine pixel dimensions, proportional max 960px/no upscale; image/text legibility; accessibility ALT and historical date; before/after logged-out browser screenshots, cache-bypassed request traces, reversible scoped staging, and separate publishing approval. Never infer reuse permission from government hosting, a Commons uploader's license alone, or an old hotlink.

## Remaining performance opportunity and ownership split

The already verified WordPress storage ledger is **13 originals >1.5MiB, 43,522,829 stored bytes**, not measured network weight. Ten are mapped to selected current articles. Five first-party 1672 × 941 single-image PNGs in posts 34–38 total **13,267,538 original stored bytes** and have no registered subsize. They are candidates for optional owner-approved **960 × 540** WebP derivatives *after* measuring real currentSrc bytes and checking artistic ownership. Two Malbone originals are directly used; three Vasa originals are delivered through Jetpack `fit=1024`. Prioritize actual missing photos before performance-only replacements.

**Site QA PR #154 retains sole guest-browser verification of P0 images**: 285:5 → 285:2 → 287:5 → 418:1/2 → 407:1. This sprint did not modify its existing probe, drafts, or the interim engineering lead's homepage-design files. No WordPress writes, third-party binary downloads, caching, post block rewrites, billing or subscription spend. Production images repaired this batch: **0**.
