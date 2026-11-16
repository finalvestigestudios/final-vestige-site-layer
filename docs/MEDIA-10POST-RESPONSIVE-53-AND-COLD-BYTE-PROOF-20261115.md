# Media delivery and 76% network-byte claim: measured-proof gate — 2026-11-15 PT

**Owner:** Final Vestige Media Recovery (#183). **Site QA #154** remains the owner of the guest-browser collector and P0 six image probes. This change is read-only GitHub draft QA. No WordPress writes, downloads, mirrors, block rewrites, homepage visual work, deployments or paid services.

## Actual latest 10-post WordPress VIEW sample

Authenticated `posts_get(context=view)` reads of published posts **285, 287, 407, 418, 288, 289, 283, 621, 34, 1924** found **53 exact rendered `img` slots**. Each URL, ALT, width/height, responsive markup and loading attribute is preserved in [53-slot read-only audit](../qa/media-recovery/wp10_53_responsive_markup_exact_urls_20261115_1925pt.json). This is not a random 66-post sample or a true visitor browser/network capture.

| VIEW markup observation | Of 53 |
| --- | ---: |
| No explicit width/height pair | **41** |
| Missing at least one of `srcset` or `sizes` | **47** |
| Jetpack-proxied `img src` | **50** |
| All 6 images in Malbone post 621 have dimension pairs and responsive markup | **6** |

In the seven P0/token/query-integrity investigations (285,287,407,418,288,289,283), **all 45 `img` tags lack responsive markup**, and 40 lack a dimension pair. This is a markup-level resilience/layout risk, **not confirmed CLS, a 404, a slow transfer, or evidence that a CSS/JS layout does not reserve space**. Malbone 621 is a useful contrasting case: apparent full-resolution `src` is paired with `srcset/sizes`, so visitors may fetch much smaller `currentSrc`. Media 39's PNG in post 34 already uses a Jetpack 1024px derivative, not necessarily its full original storage bytes.

The audit explicitly records `guest_http_status:null`, `guest_transfer_bytes:null` and `guest_broken:null` because browser evidence is missing. Previous `itok` losses in **288:5/418:5** and new query losses in **289:2/283:3** remain source-integrity risk, **not confirmed visitor failure**. All archival candidates (Florida Memory 287:5, USGS 407:1, USCG 418:1/418:2, NHHC 288:5) remain **item-rights/pixel-identity HOLD** with **maximum 960px review width and no upscaling**, no caching or Media Library upload authorization. Different archival frames are not interchangeable.

## Executable 76% transferred-byte methodology

[Node assessor](../qa/media-recovery/assess_cold_wire_savings_20261115.cjs) consumes normalized exports from **Site QA #154's existing CDP collector**; it creates no duplicate browser collector, network request or live edit.

Use:
```sh
node qa/media-recovery/assess_cold_wire_savings_20261115.cjs before.json after.json
node --test qa/media-recovery/test_assess_cold_wire_savings_20261115.cjs
```

A capture must have schema `fv-media-siteqa154-cold-cdp-image-bytes-v1`, `phase` before/after, and cohort `frozen-61` (complete 61 pages) or `current-66` (complete 66 pages). It must be a logged-out, cold-cache-disabled, service-worker-bypassed, full-page-lazy-scrolled CDP export, with matching browser/viewport/DPR/network protocol and unchanged content + image-slot manifest fingerprints. Each image request must be a complete, distinct HTTP 200 image response with explicit `CDP.Network.loadingFinished.encodedDataLength`, no disk/memory/SW caching, and complete redirect attribution. Each page must have every DOM image decoded, zero broken slots and signed-off screenshot/rights review. Otherwise the run is **HOLD**, not a partial success.

For fully matched complete captures calculate **100 × (Σ before image-network encoded bytes − Σ after image-network encoded bytes) / Σ before image-network encoded bytes**. Do **not** average page percentages, equate WordPress original storage bytes with downloaded bytes, include estimated resource sizes, silently omit unscrolled lazy images, or extrapolate a ten-post sample to a site-wide improvement. Compare desktop and mobile profiles separately. This measures a specified controlled capture, **not** a claim of production deployment or traffic-weighted savings.

**Current verdict:** 76% is **UNMEASURED**. The assessor has no real paired Site QA CDP inputs yet; this does not claim any measured savings. Historical 61 posts / 355 source images / 288 external-origin refs are deliberately separate from 66-post / 361-image newer census. The reported 42 broken third-party images remain **guest-browser unconfirmed**. WP's last verified >1.5 MB originals: **20 files totaling 64,385,752 stored bytes**, not network traffic.

## Test evidence and safety

Both added CommonJS files were executed locally with **Node v22.16.0**, `node --test`: **33 passed / 0 failed** (including synthetic 76.0% vs 75.9% boundary, weighted-by-byte summation, missing original metadata, 304s/cache, missed lazy images, different cohorts and fake statuses). All fixture URLs/bytes use `example.invalid` and are expressly synthetic. Git source/test blob hashes are pinned in the handoff comments. No native browser capture or CI result is claimed.

**Release sequence:** Site QA reuses its six P0 cold guest checks first, then Honda/Hilo token cases and Forrestal/Iroquois source-query anomalies, capturing request/redirect/decoded-image/screenshot evidence. On proven failure, Media Recovery selects only same-scene item-level rights-cleared source, computes `min(native width,960)` proportional dimensions, validates credit/crop, and proposes isolated reversible Media Library staging **without rewriting published blocks or enabling caching until authorized**. Only then compare complete before/after image network captures.
