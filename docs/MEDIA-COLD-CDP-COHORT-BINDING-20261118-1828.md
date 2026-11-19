# Media Recovery — all-image wire cohort identity (2026-11-18 18:28 PST)

## Defect and scoped fix

The offline full-CDP image-request companion had compared source-supplied inline captures with full image-request captures, but did **not** independently require the published 61-/66-post census identities. Before this patch, a fabricated 61-post set using post IDs 1–61 and `/example-N/` article URLs, with matching fabricated CDP events, could pass `threshold_met`. That result was a test false positive, **not** observed Final Vestige bandwidth savings.

The existing `qa/media-recovery/full_image_request_census_20261118.cjs` now imports `MANIFEST_SHA256` and `verifyCapture` from the *preexisting* `cohort_manifest_guard_20261118.cjs`. It refuses any non-pinned hash and checks published post IDs, canonical article URLs, counts, and image-slot IDs for **before and after, desktop and mobile**. The original full-CDP request matching, cache/Service Worker, decode, response, byte and 76%-integer gates remain in place. No additional browser collector or homepage visual work was created.

The companion tests now build against actual frozen article cohorts: **61 posts, 355 authored inline slots** historically; **66 posts, 361 slots** currently. The zero-inline-image Change Blindness article, post 1922, is deliberately accepted as a valid 66-post census member. Five new negative tests exercise invented IDs, forged article URLs, bogus asset slots, invented snapshot hashes, and the zero-slot edge case. **21/21 tests passed in isolated V8 against the exact patched source with simulated Node assert/test and crypto digest**. Native Node execution of the committed files, repository CI, guest Chromium, trace authentication and visual review remain **outstanding**. Do not represent synthetic test results as site measurements.

## High-value archival review, no automatic substitutions

- **USS Tang 274:6:** original War History Online JPEG previously returned 404 to a public retriever on November 18. The Navy's [80-G-227989](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html) is a promising *possible same-frame* source, but exact crop equivalence and federal-work rights must pass item review. Catalog 1,910×1,288; target 960×647, no crop/upscale.
- **Sunshine Skyway 287:5:** documentary JPEG previously returned public-retriever 404. [Florida Memory RC09237](https://floridamemory.com/items/show/32083) is a **different photograph**, not an exact replacement. Dimensions are not verified, and general rights guidance is not item-specific clearance.
- **Three Mile Island 285:5:** movie-related original previously returned public-retriever 404. Do **not** replace with an unrelated reactor/accident image or mirror unlicensed film photography.
- **Teton Dam 291:2:** prior source audit shows cleanup imagery under a breach caption. [NARA NAID 28894685](https://catalog.archives.gov/id/28894685) is a breach candidate (2,798×1,966, proportional 960×675), subject to exact-image/rights and editorial review. 291:5, the actual cleanup caption, should remain separate.

These prior **original-source** observations are not fresh logged-out browser confirmations. All present guest final HTTP codes, transfer bytes and decoded dimensions remain unknown. The reported 42 broken guest images and asserted 76% wire savings remain **unverified**. Twenty >1.5 MB originals totaling 64,385,752 *stored* bytes in the 132-media WordPress census are still not measured visitor downloads.

## Controlled follow-through and rollback

Site QA [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) remains owner of guest Chromium image/network evidence. Feed its existing trace into the patched gate; do not duplicate the collector or its draft. Demand exact item provenance and reuse grants, per-image approval, <=960px proportional/no-upscale derivative, correct historical caption, responsive selection and cache behavior on both devices. Only stage an approved first-party WordPress asset with a per-slot rollback plan when independently verified. **No WordPress production writes, source downloads, rehosting, risky Gutenberg rewrites, homepage redesign, merge, deployment or subscription spend** occurred in this sprint.

Machine-readable evidence: [`qa/media-recovery/full_image_manifest_binding_audit_20261118_1828.json`](../qa/media-recovery/full_image_manifest_binding_audit_20261118_1828.json).
