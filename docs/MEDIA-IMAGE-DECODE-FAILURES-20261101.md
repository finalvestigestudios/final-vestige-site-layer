# Browser-visible image decode failure hardening — November 1, 2026

## Why this matters

A remote image can return **HTTP 200** with a valid `image/jpeg` or `image/png` response header and still be genuinely **broken to visitors** because the bytes cannot be decoded. The Media Recovery browser classifier previously left this case in `zero_intrinsic_width_needs_review`, potentially undercounting actual missing visual media. A remote text retriever cannot prove this failure.

## Isolated change

Own-branch `qa/media-recovery/browser_probe_core.cjs` now emits `confirmed_broken_in_probe_browser` with `visual_failure_kind=image_decode_failure` only when *all* of these hold:

1. Existing Site QA-style logged-out page verification and unique exact source/currentSrc DOM mapping hold.
2. The completed browser image has `naturalWidth === 0`.
3. A **single matched final browser CDP response** is HTTP **200**, has MIME beginning `image/`, contains a positive safe-integer `encodedDataLength`, and has no network error.
4. That exact response is neither disk-cached nor service-worker delivered and `currentSrc` matches the final image request identity.

The validator does **not** mistake a cached read, unrelated redirect, absent response, browser-blocked page, zero-byte non-HTTP observation, or a generic retriever 403/404 for a confirmed failed decode. Existing 404/network-error and HTTP-200 HTML error-payload classifications remain intact.

## Verification

New isolated Node test file: `qa/media-recovery/test_decode_failure_guard_20261101.cjs` (**14 cases**). Original browser-core regression file: `qa/media-recovery/test_browser_probe_core.cjs` (**12 cases**). **26/26 passing** when evaluated against the exact committed GitHub core and tests in V8 with URL and Node test API shims. Native Node CI and real Chrome observation remain outstanding; the test images are synthetic, not confirmed website breakage.

## Read-only source checks this sprint

- Three Mile Island post 285 slot 5: exact stored SayMedia URL again returned **404 from independent web retriever**, **not a guest browser**.
- Sunshine Skyway post 287 slot 5: old St Pete Catalyst URL returned **web retriever 404**; same publisher's relocated CDN image was rendered by the retriever. The publisher credits University Press of Florida, and exact crop/rights remain HOLD.
- Hebgen Lake post 407 slot 1: web retriever rejected the old USGS file's `binary/octet-stream` content type (wrapper **400**, not proven origin status). Guest MIME and decode remain unverified.

No new 42-broken or 76%-savings claim. Baseline inventory is 61 posts, 355 stored source images, 288 offsite references, and 13 originals >1.5 MiB (source storage, not visitor bytes). No production repairs, image downloads, rights approvals, homepage modifications, WordPress edits or spending.

## Handoff

Site QA PR #154 continues to own actual logged-out desktop/mobile Chrome capture, final CDP request status/MIME, completed `naturalWidth`, and screenshots. The above classifier hardening lives **only** on Media Recovery PR #183; do not overwrite QA's existing drafts. Request a real image-decoding example before treating this new code path as a confirmed public failure. Priority remains **285:5, 287:5, 407:1, 418:1, 418:2**.

Actual HTTP 200 image-decode failures are now an explicitly tested acceptance category in the isolated Media Recovery code, not a speculative website finding.
