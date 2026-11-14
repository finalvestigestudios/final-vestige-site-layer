# Reconciled external image count: 286 vs 288, exact two WP-proxy origins

2026-11-14 PT · safe read-only evidence batch · DRAFT / HOLD

The frozen 61-post, 355-image Site QA #154 CSV has **286 external refs (80.56%)**. The independent PR #183 eight-part media snapshot has **288 (81.13%)**. Recalculation across all **61 matching post IDs**, using original source URLs, isolates **exactly two +1 post differences**: Three Mile Island **285** (5→6), Teton Dam **291** (5→6); **59 of 61** post rows agree. The difference is **0.56 percentage points**, not two new confirmed broken images.

## Two pinned original URLs

- **285:1, TMI control room** — `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1`. It is a proxy for the independent publisher `www.squawkpoint.com`, **not first-party Final Vestige media**. Image visible in a Nov 14 web retriever, but no origin HTTP status or visitor Chrome status. Photographer, original source and republication rights unknown; do not download/cache/rehost.
- **291:0, Teton Dam breach** — `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1`. Proxy for the National Archives blog `text-message.blogs.archives.gov`. Image visible in Nov 14 retriever. [National Archives article](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/) provides authentic historic context and links multiple 1976 images by NAID, but the **precise accession and binary identity for this URL are not verified**. Federal hosting is not a blanket reuse clearance; item-level rights/credit remain pending.

**Key distinction:** `i0.wp.com/finalvestige.com/...` is a first-party Jetpack proxy. `i0.wp.com/www.squawkpoint.com/...` and `i0.wp.com/text-message.blogs.archives.gov/...` are external publisher-proxy dependencies. The **current** code in Site QA #154 already classifies these paths as external; it has not been modified. Since its frozen CSV does not provide the original per-slot URL snapshot, the **historical reason** for 286 instead of 288 is **unknown** (possible input-snapshot timing or older categorization). Do not assert a confirmed classifier bug.

## High-value handoff and release gates

The machine ledger holds 61 post comparisons, eight Git blob-anchored source inventories, exact two source URLs, source/retriever distinction, primary catalog links and per-image safety flags. The new offline validator independently recomputes totals from the original two branch snapshots when provided to `reconcile(csv, eightParts)`. Its audit validator fails closed on fabricated browser status, rights, geometry and release changes. Tests are in `test_proxy_origin_delta_20261114.cjs`.

**Priority:** preserve Site QA's exclusive six-slot cold-browser P0 queue; neither visible web-retriever image is a guest-browser success guarantee, and neither is an additional confirmed 404. Any actual missing image must be fixed only after item-level rights and exact historical-scene match, verified decoded natural dimensions, CSS width/DPR (conditional 960px maximum and no upscaling), alt/caption fidelity, reversible staging media plan and full browser transfer-byte measurement. Never rewrite production Gutenberg blocks speculatively, mirror publisher sources, touch homepage visuals or pay for tools.

The reported **42 broken originals remain unconfirmed** in a real guest browser; the hypothesized **76% visitor-weight reduction remains unmeasured**. The latest previously verified oversized-media census of 16 WordPress originals totaling 49,107,665 **stored original bytes** is not measured page transfer. The historical 61/355 audit must not be merged into the later 66/361 cohort.

**No** WordPress writes, caching, media copies, changed Site QA files, homepage changes, deployment, merge or spending.
