# Five live inline PNGs: source, disclosure, and weight evidence — 2026-11-13 PT

**Status: HOLD. Draft-only QA / no production edits.** Ownership: Media Recovery #1703; Site QA #154 exclusively owns guest Chrome collector, six priority original sources and any true HTTP/decode verdict. The homepage visual lead is unaffected.

## New authenticated WordPress readback

Read-only `posts.get(context=edit)` for post IDs **34–38**, and `media.get(context=edit)` for attachment IDs **39–43**, checked the five exact published HTML `<img src>` links against their original media `source_url` and against the prior 15-original worklist in PR #183 (source ledger Git blob `5e474e1cb293353b2226d84fceedca0a182894d8`). **5/5 match; five images are still published.** All original files are **1672 × 941 PNGs**, with **zero WordPress-generated subsizes** and **13,267,538 stored-original bytes** combined. They account for **28.17% of the 15 oversized originals' stored size** (47,096,779 B); this is *not* a browser transfer share or a forecast saving.

| Published post | Media ID | Stored bytes | Published `<img>` width × height | Conditional derivative |
|---|---:|---:|---:|---:|
| 34 — San Francisco firefighting | 39 | 2,892,087 | 1024 × 576 | 960 × 540 |
| 35 — Shackleton's James Caird | 40 | 2,552,136 | 1024 × 576 | 960 × 540 |
| 36 — Vicksburg cave shelter | 41 | 2,498,247 | 1024 × 576 | 960 × 540 |
| 37 — Petra water works | 42 | 2,488,823 | 1024 × 576 | 960 × 540 |
| 38 — San Francisco cistern | 43 | 2,836,245 | 1024 × 576 | 960 × 540 |

**Important historical-integrity correction:** Contrary to a potential inference from the image-block ALT attributes, **all five published captions already explicitly say "AI-assisted historical reconstruction."** The WordPress media-library ALT values say the same. Only the published `img alt` omits that phrase in every case; an editor can later consider making ALT provenance consistent, but the existing visible captions already disclose the synthetic reconstruction. Do **not** allege undisclosed AI imagery or modify captions blindly. The machine audit stores all five original source URLs, actual source/caption/ALT values, rights state and conditional resolution.

## 960px image-density and accessibility decision

`960 × 540` is an **output ceiling, not an approved replacement**. Every source is 1672 × 941, so it can be downscaled, but each block declares 1024 × 576 in the post HTML. **At a rendered CSS width of 1024 px, 960px output supplies only 0.9375 device pixels per CSS pixel** even at DPR 1; at DPR 2 its sharpness margin is worse. HTML attributes alone do not establish actual CSS layout or browser `currentSrc`. Record the real browser computed image width, devicePixelRatio, image decoding, visual screenshot and cold network bytes before choosing format/resolution. Historical graphics/maps and legible labels may need retained zoom/full-size access, but these five are illustrations; still check scene fidelity and compression artifacts.

Preserve the exact content/crop and existing disclosed caption. If the rights owner authorizes a derivative, generate a reversible **staging-only** `960 × 540` optimized WebP candidate (or PNG if the image needs lossless edges), hash and pixel-decode both source master and candidate, compare on actual mobile/desktop DPR, check screen-reader ALT/caption context, and obtain editor sign-off before considering an isolated per-post change. No automated block rewrites, bulk migration or binary rehosting. Add derivative to WordPress Media Library only after permissions and staging approval, with original permalink and source-master evidence retained for rollback.

## Why the 76% claim is not demonstrated

The frozen research baseline is 61 posts/355 inline references/288 offsite source positions. The expanded November 8 live scan was 66 posts/361 raw inline image tags, so never silently merge denominators. **42 supposedly broken originals have no authenticated guest-browser failure proof.** The 15 oversized original files total 47,096,779 stored bytes; **11** match published inline uses across eight posts (38,480,915 stored B). Some Vasa posts already embed Jetpack `fit=1024` transformed images; stored original size cannot be mistaken for network transfer. The proposed **76% reduction** must be measured from stable, uncached, identical-image/site baseline and candidate page loads as (sum baseline encodedDataLength − sum candidate encodedDataLength) / sum baseline encodedDataLength, with request/currentSrc, viewport, DPR, cache flags, pixel geometry and scene identity held. Do not count cache-served resources as successful transfer reductions.

The **P0 recovery order** stays `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1` with Site QA #154's exclusive collector. Only afterward should it check these five first-party images for actual rendered currentSrc and bytes. There is presently **no actual guest/origin image HTTP status**, no actual image transfer size, and no verified 960px performance outcome in this batch.

## Audit and test custody

- [Machine-readable five-row fresh WP evidence](../qa/media-recovery/live_p1_five_png_caption_weight_20261113.json): blob `0719054c8f15d9cabeb44a25274544f1ec851388`
- [Fail-closed standalone source/rights/size validator](../qa/media-recovery/validate_live_p1_five_png_20261113.cjs): blob `04b5a3cf45e8d19fde3bf01f62a72b00751a27ae`
- [25-case native Node-compatible test definitions](../qa/media-recovery/test_live_p1_five_png_20261113.cjs): blob `6ea887d9138facf5b7c7389080b4be2ea1fb467f`
- **25/25 PASS** in isolated V8 execution of the exact three *reread* committed files with restricted `require`/test/assert shims. **Native Node test runner, repository CI, actual browser QA and fresh binary status checks not run**; no claim otherwise.

**Release hold:** rights to create/use optimized derived artwork remain unverified; originals not downloaded; post/image src/alt/caption not changed; production WordPress untouched; homepage untouched; no media cache/rehost, merges, deployments or subscription spending.
