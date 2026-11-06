# Media transfer measurement gate — November 6, 2026

This is an **offline analysis-only** supplement to media draft PR #1228. Site QA PR #154 owns guest-browser collection and visual checks. No duplicate collector, WordPress write, homepage design, hotlink mirror, image download or subscription spend.

## What was verified

The historical 61 published articles / 355 inline sources and the newer 66 / 361 cohort are **different denominators**. The 294 offsite source references and 13 original WordPress files totaling 43,522,829 **stored** bytes do not establish actual transferred weight. **42 broken originals** is an unverified report, not a guest-browser count; **76% transfer reduction** is a target hypothesis, not a measurement. Worklist `docs/IMAGE-WEIGHT-WORKLIST.md` remains absent on default and media branch.

The machine-readable `wire_gate_targets_20261106.json` pins **13 exact source URLs** (the six priority suspected failures plus the seven Florida Memory originals) with all true guest-browser HTTP, decoded size, transfer bytes and visitor failure fields **null**. This deliberate NULL prevents treating the web retriever's 404/403/wrapper-500 as image-network facts. Its Sunshine Skyway original-publisher relocated JPG is viewable via web retriever, but reproduction permission and original binary identity are unverified. Florida Memory's archive catalog and public-domain mark policy preserve item-level review and statutory credit. Do not assume a 960-pixel derivative exists; never upscale an archive scan or substitute another photograph.

## New executable fail-closed benchmark

`node --test qa/media-recovery/test_measure_cold_wire_pairs_20261106.cjs`

`node qa/media-recovery/measure_cold_wire_pairs_20261106.cjs /path/to/curated-browser-before-after-evidence.json`

The *curated* input is **not** a HAR decoder or a browser collector. It must use `schema: "fv-cold-image-wire-pairs-v1"`, `published_cohort_size: 61 | 66`, `expected_page_urls: [the complete intended page URLs]`, and `pairs: [{page_url,before,after}]`. Each before/after capture requires positive guest-browser verification, Chrome/viewport/DPR/network profile equality, disabled cache and service worker, full scroll and image loading, a capture timestamp, and image network rows with **actual** `chrome_har_entry_transferSize` or `cdp_loadingFinished_encodedDataLength` values in `wire_bytes`, status 200, actual image MIME and `from_cache:false`. DOM rows require stable `slot`, network-matched `current_src`, `complete:true`, and positive `natural_width`/`natural_height`. Unknown bytes, 304/404, browser decoding failures, changing image-slot coverage, proxy rewriting not reflected in currentSrc, cache hits, CORS-hidden zeros, mixing measured byte sources, different test environments, or incomplete page cohorts fail validation.

An isolated page can yield a **page-level** measured saving. Only exact complete 61- or 66-page cohorts can yield a site-wide unweighted byte-sum claim; even that is not a traffic-weighted production savings estimate. The claim of **≥76% site-wide saving** is supported only when that fully observed cohort meets the threshold. Browser timings, real-user LCP/CLS and responsive visual fidelity remain separate requirements. For any suspected **broken** image, Site QA logs status and naturalWidth separately; this comparator deliberately rejects HTTP failures and therefore must never be used to conceal missing images.

## Release path

First, Site QA #154 supplies logged-out Chrome desktop/mobile evidence for the six P0 slots plus Florida Memory seven. Verify actual visitor failures and exact displayed images. For each confirmed defect, obtain authoritative same-image catalog, item-level rights/attribution, original dimensions, conditional ≤960px/no-upscale preview, and an isolated WordPress **staging** visual comparison preserving captions, alt text and full-size archival map access. Only after rights, before/after cold-wire, browser decoding and separate production approval should any single image be changed. **No production fixes were made in this batch.**
