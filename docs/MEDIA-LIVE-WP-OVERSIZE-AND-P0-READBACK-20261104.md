# Media recovery — production WordPress readback, original weights and source drift (2026-11-04 Pacific / Nov 5 UTC)

**Status: DRAFT, zero production writes. Independent PR #183.** This is an authenticated WordPress **CMS-only** readback, not a browser transfer audit. Read-only `posts.get(context=edit)` was run for **285, 287, 418, 407, 291, 621, 299, 34–38, 434** (13 posts), and image-only `media.list` was paged **100+13 = 113** current media items. The frozen comparison is the Oct 30 61-post/355-image inventory; **61 posts were not freshly recrawled**, so don't call these figures the present full-post count.

[Machine-readable evidence](../qa/media-recovery/live_wp_p0_and_oversize_13_20261105.json) · [fail-closed validator](../qa/media-recovery/validate_live_wp_p0_and_oversize_13_20261105.cjs) · [21-case mutation suite](../qa/media-recovery/test_live_wp_p0_and_oversize_13_20261105.cjs).

## Immediate high-value performance worklist

**All 13 media originals strictly exceed 1.5 MiB (1,572,864 B) and still account for 43,522,829 bytes of *WordPress stored originals*, not proven guest downloads.** This rechecks the exact same numerical original-size total against the live media catalog rather than merely repeating the October inventory. No CDN transfer, responsive selection, HTTP status, LCP, CLS or 76% site-wide saving is verified.

**Five first-party, 1672×941 PNGs, all with no registered WordPress generated subsizes**, are each the single inline image in a currently published article: #39→post **34**, #40→**35**, #41→**36**, #42→**37**, #43→**38**. Their **combined original storage is 13,267,538 bytes**. A conditional non-upscaled **960×540** derivative per photo (only after artwork rights and scene/caption fidelity checks) offers a focused optimization batch. Existing raw `<img src>` points at each original URL. It is **not yet proven** that visitors actually fetch all original bytes, or that WebP would be visually equivalent.

**Malbone post 621** currently has two direct original JPEG sources: media **1257 = 4,798,395 bytes** (4000×3000) and **1258 = 5,553,669 bytes** (5667×3831). These are another high-priority exposed-original pair; their metadata lists WordPress subsizes, so inspect actual rendered `currentSrc/srcset` before changing content.

**Vasa post 299** currently references originals media **388 = 8,176,362 bytes**, **389 = 2,822,969 bytes**, **382 = 2,318,980 bytes** through `i0.wp.com/finalvestige.com/...` with **`fit=1024,...`**. Those values are *stored original sizes*, while the **browser may transfer CDN-generated smaller renditions**; never assume the 8.18 MB original travels to visitors. Rights and photographer attribution need individual review.

Three remaining oversized media **482 (2,293,016 B)**, **405 (2,201,573 B)**, **293 (2,090,327 B)** have **no exact use established in this selected set of 13 live published posts**. This is NOT evidence that the files are unused or can be deleted. Media attachment parent is not a proof of active use. Do not delete, duplicate, overwrite or rehost them without crosschecking live consumers and permission.

All proposals cap output **width to 960 pixels, proportional height, no enlargement**; dimensions in the audit are calculated from WordPress metadata rather than inspected image binaries. Photograph composition, embedded technical text, credit and rights remain `HOLD`.

## Missing-image queue: six exact stored sources still in live CMS

Rechecked six original source URLs and post image counts in read-only current WordPress content: **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**. **All six exact sources still match** the pinned Oct 30 inventory; 285 (Nov 2 21:39:59) and 287 (Nov 2 21:40:01) now have newer WordPress *modified* timestamps than the frozen record, so do **not** infer the original complete post snapshot has remained immutable. The six images are **not confirmed browser failures**. Their latest origin HTTP, guest `currentSrc`, redirects, MIME, actual decoded size and CDP image transfer bytes remain NULL.

**Site QA #154 keeps the existing P0 browser priority:** 285:5 → 285:2 → 287:5 → 418:1/2 → 407:1. Media Recovery has not modified Site QA scripts or homepage design. For each, confirm visible breakage using logged-out cold Chrome with `currentSrc`, the final **Image** request/status, network error, MIME, decoded width/height, screenshot and CDP encoded length. An independent retriever 403/404 or wrapper 500 is **not** an origin/visitor HTTP result.

## Rights-controlled recovery and staged WordPress plan

1. Capture guest-browser failures for P0 with Site QA's existing scripts; no duplicate probe or assertion based on source-retriever wrappers.
2. Select the identical historical photograph/crop from primary Navy, Coast Guard, Florida Memory, NARA, NASA or verified creator catalog; distinguish merely similar alternatives. Verify **item-specific** permissions, source credit and downstream commercial reuse.
3. Obtain only authorized binary masters; record source record URI, immutable SHA-256, pixel dimensions, rights basis, caption/date, and approved 960px non-upscaled geometry. Keep downloaded masters in controlled temporary staging, not blindly in WP.
4. Compare staged derivative against the published subject and any detailed labels/maps/figures; preserve aspect ratio, orientation, accessibility ALT and credit.
5. Only with separate release approval stage WP media and a reversible, scoped post image substitution. Repeat *matched uncached* CDP before/after, show actual transfer-byte deltas attributable to changed sources, mobile/desktop LCP/CLS diagnostics and screenshot parity. Roll back any visual, attribution or transfer regression.

**No third-party image binaries downloaded, transformed or cached this run; no publication rights cleared; zero WordPress production writes; no subscription spend.** The 42 allegedly broken and 76% improvement claims remain unverified/unmeasured. Production repair count was **not independently measured by this CMS-only read**, and is deliberately `null` in the new audit (previous independent reported count: zero).

**Validation:** 21/21 committed regression cases passed using an isolated V8-compatible execution of the exact committed validator, test script and machine JSON; this is **not native Node checkout/CI**. Native Node and actual browser/CDP execution are pending. The audit intentionally fails if anyone changes null browser statuses to invented 404s, claims 76%, assumes rights, authorizes uploads, upscales, or changes the 13/43,522,829 original-byte ledger.
