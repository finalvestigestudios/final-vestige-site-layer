# Image-weight claim guard: byte-weighted pooled CDP transfer totals (2026-11-03)

## What changed and why

The read-only media-performance evaluator in `qa/media-recovery/evaluate_image_wire_20261103.cjs` previously reported the **median of percentage reductions across repeat cold browser runs** as the overall measured reduction. This can misleadingly report at least 76% savings when a single large run transfers almost unchanged bytes: percent-median ignores the amount of network data transferred in each run. It is a **measurement logic flaw proven synthetically**, **not evidence of any visitor-visible broken photograph or achieved live site savings**.

Now the headline `measured_reduction_percent` is calculated as:

```text
100 * (SUM(baseline cold CDP encoded image bytes) -
       SUM(candidate cold CDP encoded image bytes))
      / SUM(baseline cold CDP encoded image bytes)
```

Each sample must retain the same browser, viewport/DPR, cache and network profile, image-only CDP resource type, slot identity, HTTP/MIME/decode and cold transfer provenance. The evaluator now also verifies that pooled byte sums remain within JavaScript safe-integer precision. `median_repeat_reduction_percent` and `minimum_repeat_reduction_percent` remain diagnostic fields; neither silently replaces the byte-weighted ratio.

**The `sitewide_76_percent_verified` flag is gated on the frozen 61-post/355-slot inventory, at least three comparable repeats, a raw pooled reduction >=76%, AND each raw repeat reduction >=76%.** A single degraded repeat blocks the badge even when the median rounds to 76%. A qualifying metric would still describe only **stored inline <img> slots** (not total page weight, CSS background media, real visitor traffic, or an editorially approved asset replacement).

## Reproduction and regression result

The 61-post synthetic adversarial fixture uses per-repeat baseline CDP bytes **61,000; 61,000; 6,100,000** and candidate bytes **14,640; 14,640; 6,100,000**. The *median* per-repeat reduction is **76%**, but pooled savings are **92,720 / 6,222,000 = 1.49%**. The former metric could overstate a 76% gain; the new result reports **1.49%** and blocks the verified flag.

A second mutation changes one post in one repeat from a 240-byte candidate to 800 bytes, leaving the other measurements at 76%; pooled savings fall to approximately **75.694%** and the badge is blocked. An additional mutation makes each repeat safe in isolation but aggregate stored byte counters exceed `Number.MAX_SAFE_INTEGER`; the evaluator now returns `INSUFFICIENT_DATA`.

**36/36 exact GitHub-committed-source synthetic tests PASSED** using the isolated V8 CommonJS compatibility shim. This is **not native Node CI** and **not** a CDP/Chromium guest measurement. Native Node and logged-out browser verification remain outstanding. No synthetic bytes are attributed to finalvestige.com visitors.

- Code commit: [da1e6a53b87ae010ff9771efcd885072def53ce7](https://github.com/finalvestigestudios/final-vestige-site-layer/commit/da1e6a53b87ae010ff9771efcd885072def53ce7).
- Test commits: [09c40f175d6afac11d60ee324140c4f969af0445](https://github.com/finalvestigestudios/final-vestige-site-layer/commit/09c40f175d6afac11d60ee324140c4f969af0445), [9bcce163c3a1e48b8bb2577aa7f1473b5040de73](https://github.com/finalvestigestudios/final-vestige-site-layer/commit/9bcce163c3a1e48b8bb2577aa7f1473b5040de73).
- [Machine-readable falsification audit](../qa/media-recovery/pooled_cdp_wire_claim_integrity_20261103.json).

## Existing P0 repair evidence and rights gate (unchanged; not a new browser test)

Slot **287:5**, published Sunshine Skyway, still references `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`. The **independent image retriever wrapper** returned 404 on Nov 3, but **origin status, guest Chrome status, pixel decoding and CDP bytes remain unknown**. Never label it a proven browser 404. The [primary Florida Memory archival candidate K894127](https://floridamemory.com/items/show/131903) is H. Milo Stewart's circa-1987 photograph of old and new bridges, *not* a verified identical photo of the 1980 disaster. Its Commons rendition is 600×595, so do **not upscale** to 960. Florida Memory's Public Domain Mark 1.0 and credit guidance still require item-level rights, donor-condition, context, and visual/crop checks before any lawful WordPress media caching. [Prior exact six-image audit](../qa/media-recovery/skyway_287_p0_florida_archive_20261103.json) remains the source of truth. No binary copies or WordPress writes are authorized.

## Site QA handoff and release limitations

Site QA draft [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) keeps its source and browser diagnosis queue (**285:5 → 285:2 → 287:5 → 418:1–2 → 407:1**). Media Recovery PR [#183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) owns this separate *aggregation-only* evaluator. Do not replace QA's scanner or duplicate its drafts. When the existing guest CDP probe is available, collect request-ID joined, noncached full lazy-scroll image GET `encodedDataLength` with same cohort conditions, after checking genuine missing-image statuses. Preserve before/after image identity, copyrights, credits and screenshots separately; code metrics never authorize publishing.

The Oct 30 baseline remains **61 published investigations / 355 inline image slots / 288 external-origin references / 13 WordPress originals >1.5 MiB**. The independently reported **42 broken** are not confirmed guest-browser failures. The claimed **76% savings is unmeasured**. The prior 67.06% is only stored-original byte concentration, not downloaded-image reduction. Production fixes **0**; WordPress writes **0**; third-party downloads **0**; homepage-design changes **0**; subscription spend **0**.
