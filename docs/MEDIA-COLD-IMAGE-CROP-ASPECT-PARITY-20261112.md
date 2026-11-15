# Cold-browser image framing parity and P0 source handoff — November 12, 2026

## Reproduced offline fault

Before the patch, `compare_cold_pair_visual_parity_20261111.cjs` (blob `68793555d6ad8998283501f9cd45114612e8d0db`) accepted **synthetic 76% transfer savings as visual parity** with same source URL, ALT, slot, photo-identity label, 390×260 CSS box, `cover` fit and 50% position despite a 960×640 baseline being replaced by a 960×960 decoded selected image. Both selected dimensions individually matched natural dimensions, but the new square frame necessarily changes the displayed crop. This is a verified offline QA defect, not a live incident or true 76% savings.

## Safe fix

The existing recovery-draft comparator now rejects material cross-run selected-source aspect changes as `HOLD: SELECTED_SOURCE_ASPECT_OR_CROP_DRIFT` regardless of stable URL or purported replacement-review assertions. It protects `cover` cropping, `contain` letterboxing and `fill` distortion. A 0.5% relative (minimum 0.0025 absolute aspect ratio) rounding tolerance permits same-composition re-encodes such as 960×639, while the original physical pixel/DPR and framing checks remain required. Seven new regression/control cases were appended to its test suite. **24/24 isolated V8 checks passed** against precommit patch code; native Node CI and genuine guest Chrome are not claimed.

## Source triage and guest evidence

Machine-readable companion: `qa/media-recovery/p0_crop_parity_source_handoff_20261112.json`. It carries six exact published source URLs by P0 slot, external retriever wrapper observations, nullable genuine HTTP/currentSrc/bytes, primary archive or publisher leads and conditional ≤960px/no-upscale rights/scene-review holds, derived from existing handoff Git blob `0098216405f3415e57d2a3f13969bdb87ffbcd30`. This is not a duplicate CDP collector. The existing Site QA #154 collector retains queue `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`.

Two additional official Florida Memory catalogs are **excluded** as same-photo 1980 Skyway disaster replacements: [DOT2168 (1963)](https://www.floridamemory.com/items/show/104039) and [C022428 (1955)](https://www.floridamemory.com/items/show/73331). Their 1950s/1960s scenes differ from the 1980 collapse and publication rights and native digital dimensions remain unverified. They may serve as separately labeled historical context only after editorial and rights review, not invisible substitution.

## Performance and production boundaries

Frozen historical 61-post/355-image census is not the current expanded 66-post/361-inline cohort. The reported 42 broken originals remain guest-unconfirmed. Fifteen oversized WP originals total 47,096,779 **stored** bytes (11 inline matched = 38,480,915 bytes). Actual cold visitor image-transfer savings and the proposed 76% are **unmeasured**. Compute reduction from summed same-cohort logged-out CDP `Network.loadingFinished.encodedDataLength`, check selected image identity and framing on the same viewport/DPR, and separately assess current-site CSS/background images, LCP and CLS. These measures cannot be inferred from WP original file size.

No image binary downloads, licensed-or-unlicensed caching, WordPress post/media writes, automated image rewriting, homepage design changes, deployments, merges, subscriptions or spend. All changes remain draft and require independent rights, exact-scene/photo, natural-resolution and editorial review before any cached 960px derivative or staging action.
