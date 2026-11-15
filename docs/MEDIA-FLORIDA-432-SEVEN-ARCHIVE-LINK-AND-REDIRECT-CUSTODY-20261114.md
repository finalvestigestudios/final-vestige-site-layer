# Florida Memory image-source integrity — published post 432 (2026-11-14 PT)

**Draft-only.** WordPress, homepage design, Site QA #154 and images are unchanged.

Authenticated **read-only** WordPress edit-context inspection found all **seven** stored inline image URLs, ALT text, image-anchor clickthroughs and captions in [They Buried the Dead Apart](https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/) (last modified `2026-08-28T03:07:30`). Official Florida Memory indexed item records confirm all seven accession-to-`/fpc/` source-path matches.

## Three exact-item link corrections for editorial review (not image substitutions)

- **432:2 RC17068:** [hurricane exhibit](https://www.floridamemory.com/learn/exhibits/photo_exhibits/hurricanes/hurricane3.php) currently linked; exact primary [item 38362](https://www.floridamemory.com/items/show/38362) (Avenue A flooding, Sept 1928). Its caption **“Source record”** link also points to the generic exhibit rather than the exact item.
- **432:5 RC04344:** same generic exhibit linked; exact primary [item 27848](https://www.floridamemory.com/items/show/27848) (1928 coffins along a canal).
- **432:6 RC07668:** [search page](https://www.floridamemory.com/find?keywords=Burial%20of%20victims%20of%20the%201928%20hurricane) linked; exact primary [item 30741](https://www.floridamemory.com/items/show/30741) (1928 West Palm Beach burial).

Other **4/7** image anchors already link exact primary catalog items: PR04493 [4144](https://www.floridamemory.com/items/show/4144), RC10673 [33289](https://www.floridamemory.com/items/show/33289), N031889 [141398](https://www.floridamemory.com/items/show/141398), MSF-PB11548-001 [340182](https://www.floridamemory.com/items/show/340182). Keep the correctly documented **2001** date for the latter. Issue/PR #183 already noted that the N031889 ALT overstates disaster-response and post-hurricane timing; this PR does **not** duplicate that editorial change.

## Delivery observation vs actual browser evidence

All seven stored `https://www.floridamemory.com/fpc/...` JPG source URLs produced external reader **wrapper 500 redirect-target-inaccessible errors**, pointing to corresponding `https://floridamemory.com/fpc/...` targets. This is **NOT seven origin 500s or seven proven broken visitor images**. The JSON records exact stored URLs, catalog links, attempted result and redirect targets, with real guest HTTP, `currentSrc`, pixels and transferred bytes **unknown/null**.

## Rights, resizing, WordPress staging, and QA

[Florida Department of State in 2017](https://dos.fl.gov/communications/press-releases/2017/florida-memory-achieves-major-milestone-with-the-200-000th-historical-photograph-added-online/) broadly described Florida Memory photographs as copyright-free with archive credit. The inspected indexed item records did **not** expose explicit per-item license text; review individual reuse terms, credit and master provenance before any caching or WordPress upload. Physical print size is **not** image pixels. No native pixel dimensions are verified; proposed derivatives **max 960px wide, no upscaling**, preserving aspect and requiring `CSS width × DPR` coverage. Hold any derivative that would impair captioned detail.

Future approved remediation: collect Site QA's logged-out browser waterfall and `naturalWidth`, choose **exact-scene** and licensed master, record checksum and correct attribution, create responsive WordPress media only in isolated staging with rollback, and compare actual same-page transferred image bytes, LCP and CLS. The claimed **76%** byte reduction remains unmeasured. Historic 61 posts/355 images, 42 reported browser-unconfirmed failures and 16 >1.5 MB original stored files (49,107,665 bytes) are **not** new measured results.

Native test: `node --check qa/media-recovery/validate_florida_432_links_20261114.cjs && node --test qa/media-recovery/test_florida_432_links_20261114.cjs && node qa/media-recovery/validate_florida_432_links_20261114.cjs`. All outcomes remain **HOLD**. No media download, cache, WP production write, Gutenberg rewrite, merge, deploy, homepage change, or spend.
