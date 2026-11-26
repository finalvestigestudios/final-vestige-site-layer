# Okeechobee post 432 — seven official Florida Memory image records (2026-11-17)

This is a **read-only recovery and editorial-integrity batch** on draft PR #2747. The source of current VIEW image URLs is `qa/media-recovery/live_66_view_slice_2_20261117.json`, SHA `1c8cd5d1fd015705c0937d68471fb54546ed2f67`. All seven authored `<img>` sources are Jetpack-proxied Florida Memory originals; none has `width/height` or `srcset/sizes` attributes in this VIEW snapshot.

## Seven exact catalog identities

| Slot | Accession | Primary source | Image date |
|---|---|---|---|
| 432:0 | PR04493 | https://floridamemory.com/items/show/4144 | 1928 |
| 432:1 | RC17068 | https://floridamemory.com/items/show/38362 | 1928 |
| 432:2 | RC10673 | https://floridamemory.com/items/show/33289 | 1928 |
| 432:3 | N031889 | https://floridamemory.com/items/show/141398 | 1928 |
| 432:4 | RC04344 | https://floridamemory.com/items/show/27848 | 1928 |
| 432:5 | RC07668 | https://floridamemory.com/items/show/30741 | 1928 |
| 432:6 | MSF-PB11548-001 | https://floridamemory.com/items/show/340182 | 2001 |

Every catalog entry matches the current source's precise `/fpc/` image pathname (see [machine audit](../qa/media-recovery/okeechobee432_florida_seven_20261117_1730pt.json)). The public reader's attempt to open the seven `www` JPG URLs was intercepted by a redirect to apex `floridamemory.com`, then reported as inaccessible; **the reader's HTTP 500 wrapper is not proof of image-server HTTP 500 or a browser failure**. All seven current guest-browser statuses and image-decode outcomes are unknown. There are no downloaded image binaries or native pixel dimensions.

## Important corrections to historical meaning
- **432:3 — N031889:** Existing ALT asserts the Board of Health facility was the *post-hurricane disaster-response headquarters*. The official catalog documents State Board of Health personnel at its Pahokee headquarters in **1928**, but not that specific claim. Suggested ALT: "State Board of Health staff at its Pahokee headquarters in 1928."
- **432:6 — MSF-PB11548-001:** This is a **2001 color slide of the historical African American mass burial site**, not a 1928 photograph. Suggested ALT adds "photographed in 2001." These corrections are recommendations only; no live post change occurred.

## Rights, 960px, caching and WordPress release HOLD
Florida Memory's [reproduction FAQ](https://floridamemory.com/share/order-info/faq.php) states that its images are offered under **Creative Commons Public Domain Mark 1.0** and asks for credit under Florida Statutes §257.35(6). Its [disclaimer](https://floridamemory.com/learn/about/disclaimer.php) notes use responsibilities and underlying source terms. This is a **provider designation**, not a grant of missing rights on some unrelated image; item-level approval, proper source credit and identity review remain required. No bulk scraping or mirroring occurred.

Native **digital pixel** width/height must be measured from a rights-cleared master; physical print dimensions are not pixels. Only then calculate max width `min(originalWidth,960)` with original aspect ratio and no upscaling. A conditional future staging plan: inspect master and SHA-256; produce approved derivative; preserve ALT/caption/credits, image order and Gutenberg block IDs; test preview on mobile/desktop; receive Site QA's independent network response/decode/screenshot/byte evidence; log WordPress media item and per-item rollback. No production upload or block rewrite is authorized.

Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns logged-out browser captures, and earlier suspected P0 slots remain first priority. The 42 broken-image report and 76% savings claim are still not confirmed as visitor outcomes. The 20 oversized originals total 64,385,752 *stored* bytes, not transferred bytes.

Run `node qa/media-recovery/okeechobee432_florida_seven_20261117_1730pt_test.cjs` for the 27-case isolated fail-closed regression suite.
