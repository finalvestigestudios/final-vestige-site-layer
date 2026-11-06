# Directly embedded oversized image — fresh WP readback, 2026-11-06

**Scope:** independent read-only media engineering, not homepage design, not Site QA #154's guest-browser collector. Live WordPress editor-content and media metadata were read for posts 34–38, 621 and image attachments 39–43, 1257–1258. Absolutely no WP writes, downloads, caching or spending.

## Critical correction: the five PNG article images already have intrinsic HTML dimensions

The stored content of posts 34–38 uses **one directly embedded PNG per article** and **every PNG already has `width="1024" height="576"`**, with **no stored `srcset` or `sizes`**. Each original is **1672×941** in WordPress and has **no registered smaller sizes**. Therefore, *do not* create a false five-image "add missing dimensions" task. The potential concern is needless original-byte transfer, subject to logged-out browser measurement; runtime WordPress/Jetpack HTML may be different.

| Post / article | Media | Original source URL | Original storage | Conditional ≤960px preview |
| --- | --- | --- | ---: | --- |
| [34, San Francisco fire](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) | #39 | https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png | 2,892,087 B | 960×540 |
| [35, Shackleton](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) | #40 | https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png | 2,552,136 B | 960×540 |
| [36, Vicksburg](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) | #41 | https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png | 2,498,247 B | 960×540 |
| [37, Petra](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) | #42 | https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png | 2,488,823 B | 960×540 |
| [38, cisterns](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) | #43 | https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png | 2,836,245 B | 960×540 |

**Combined original storage: 13,267,538 bytes.** The WordPress post captions explicitly label these **AI-assisted historical reconstructions**, not period photographs. All new size/format proposals must preserve that distinction and existing ALT meaning. Derivative rights require review despite first-party hosting.

## Separate Malbone issue: no dimensions, but existing 768px WP variants

In [post 621, *Six Miles an Hour*](https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/), two directly embedded originals have **no width/height/srcset/sizes in stored img HTML**, but WordPress **already registered 768px and 1024px derivatives**:

- Slot **621:0**, media **#1257**, exact original https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg — **4000×3000 / 4,798,395 stored bytes**. Existing, **not newly downloaded**: https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original-768x576.jpg. Conditional 960×720 candidate *not created*. Attribution in WP caption: GeneralPunger / Wikimedia Commons, CC BY-SA 4.0.
- Slot **621:1**, media **#1258**, exact original https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg — **5667×3831 / 5,553,669 stored bytes**. Existing, **not newly downloaded**: https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original-768x519.jpg. Conditional 960×649 candidate *not created*. Attribution in WP caption: New York Public Library Digital Collections, U.S. public domain. **Preserve full-resolution map access/zoom for legibility.**

These two original files total **10,352,064 stored bytes**. **DO NOT treat the captions as independent rights/license clearance**; review the exact Commons/NYPL items, photographer and share-alike conditions before localization or changed distribution. Do not blindly rewrite Gutenberg image blocks or overwrite the original WP attachments.

## Weight measurement and staging gates

The 7 originals represent **23,619,602 WordPress stored bytes across six articles**, **not one page's transmitted image weight**. A purely mathematical 76%-below-storage hypothetical target is **5,668,704 bytes** (24% of that aggregate); it is *not* an achieved transfer reduction or a defensible page KPI. Guest Chrome cold image network bytes, exact `currentSrc`, decode, `naturalWidth`, srcset after runtime rewriting, cache booleans, matched viewport, LCP/CLS and preserved visual quality are required before any conclusion. Reuse the existing cold-image comparator in Media PR #183 and the existing Site QA #154 collector; do not duplicate either.

**Priority stays with confirmed real missing media**, especially P0 285:5, 285:2, 287:5, 418:1/2, 407:1. The historical 42-broken allegation remains *browser-unverified*. Other 13 oversized original inventory remains **43,522,829 stored bytes** (13 image items), not wire bytes. No production media repaired, no homepage changes. Source cross-check: `qa/media-recovery/oversize_snapshot_20261106.json` blob `6e6fb1048f643a33fb6e0e1d5881657400e74968`. Published HTML can be modified by runtime delivery; this document describes **stored post markup only**.
