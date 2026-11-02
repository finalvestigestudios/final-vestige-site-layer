# Media Recovery — protect historical image identity across Jetpack proxies and crop selectors

**Date:** 2026-11-01  
**Ownership:** Media Recovery PR #183 only; independent Site QA PR #154, public homepage, and WordPress remain untouched.  
**Scope:** Offline identity classification for existing sources, not an asset transfer, rights determination, or live-browser audit.

## Reproduced defect

The source validator `qa/media-recovery/browser_probe_core.cjs` previously unwrapped `i0.wp.com` / `i1.wp.com` URLs by reconstructing the underlying origin **without any query parameters**. For a non-static archival image endpoint, `?image=NH43900` and `?image=NH98039` can select **different photographs**. The old `sameSource()` wrongly returned `true` for those two proxied sources.

A separate static-image normalization rule discarded `?crop=...` as if cropping were always a content-neutral resize. The old classifier wrongly considered `https://archive.example.org/photo.jpg?crop=top` equivalent to the same URL with `?crop=bottom`—although the two may depict different surviving details of a historical scene.

These errors could allow a browser HTTP failure or decoded pixels to be associated with the **wrong historical visual**, even while the classifier otherwise enforces exact final CDP identities. This is a defect in the audit code, **not evidence that FinalVestige.com rendered a broken or incorrect photograph**.

## Isolated fix

- Preserve all underlying Jetpack origin query parameters **except the proxy-only `ssl` parameter** when reconstructing the source URL.
- For a **static image path**, continue ignoring documented resizing/quality parameters (such as `w`, `q`, `fit`, `resize`) but preserve `crop` as material to source identity.
- For a **dynamic endpoint**, retain all parameters except the existing explicitly documented Navy `rendition` handling. Thus `image`, `id`, `file`, and even `width` cannot be discarded without evidence that the origin treats them as size-only.
- A mismatch stays `alt_only_identity_unverified` or another non-definitive state, rather than creating a false broken-image count. Genuine same-image 404s and loaded same-image JPEGs remain identifiable.

## Verification

Old-source `sameSource()` reproduced both false equivalences (`true`); patched source correctly returns `false`. The exact committed core blob `437d4a7436a2d4c6abd63ceb100d58c934e91bb3` and newly committed regression blob `0cc4df5f4574df041a345c0008b607e248b55036` were read back and replayed together with the preexisting `browser_probe_core` tests in isolated V8 using test-only URL / `node:test` / assert shims: **31/31 pass** (19 new, 12 existing). Native Node.js CI and actual logged-out Chrome remain outstanding.

**Exact commits:** code `145de7900f5e16f7b09647e00bbd31ad2e6babc4`; tests `8b30a0768d2ac61381255e6685abb9139f46e9af`.

## Live verification and publication gates

Site QA #154 retains the existing logged-out desktop/mobile browser collection: source slot and stored URL, rendered `currentSrc`, final CDP Image GET URL including query/crop selectors, redirect chain, decoded intrinsic dimensions, HTTP status/MIME, encoded bytes, cache state, and exact-position screenshot. Cases with a changed crop or underlying dynamic image selector must remain **identity-unverified** pending an intentional visual inspection; this lane should not duplicate Site QA browser scripts.

A candidate asset can advance **only** after its archival identity and historical scene are verified, item-level rights/reuse and credit are established, and a separate production change is approved. Proposed derivative must be **`min(960px, verified source width)`**, preserve aspect ratio, avoid upscaling or unapproved historical crop, and be staged for controlled WordPress Media Library caching with responsive metadata—not rewritten into Gutenberg by string substitution. Compare full mobile article-image network transfers and actual LCP/CLS before claiming a reduction.

The frozen audit still covers **61 posts, 355 stored image references, 288 external references and 13 WordPress originals >1.5 MiB**. The claimed **42 broken images are not browser-verified**, the claimed **76% transfer savings are not measured**, and **zero production images have been repaired** by this change. No media downloaded/rehosted, no WordPress write, no homepage change, no subscription spend.
