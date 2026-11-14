# Five first-party historical reconstructions — 960px/DPR integrity preflight

2026-11-14 PT · read-only authenticated WordPress source/Media Library inspection · DRAFT / HOLD

## New finding and exact source custody

Five first-party images in published posts 34–38 are **AI-assisted historical reconstructions**, explicitly disclosed as such in both their public article figure captions and their Media Library descriptions. They are not archival documentary photographs and must not be silently relabeled as one. Each post's stored image tag explicitly declares width=1024 and height=576, while its WordPress original is 1672×941 pixels and has **zero derivative size descriptors**.

| Post | Media ID | Original stored bytes | Actual stored URL | HTML / native dimensions |
|---|---:|---:|---|---|
| [34](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) | 39 | 2,892,087 | [Exact original PNG](https://finalvestige.com/wp-content/uploads/2026/08/bceca0bd-a16f-44f7-be08-16376fbf08ca.png) | 1024×576 / 1672×941 |
| [35](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) | 40 | 2,552,136 | [Exact original PNG](https://finalvestige.com/wp-content/uploads/2026/08/377e08da-e121-4f57-9174-1548343402b3.png) | 1024×576 / 1672×941 |
| [36](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) | 41 | 2,498,247 | [Exact original PNG](https://finalvestige.com/wp-content/uploads/2026/08/a44f673d-a8a8-4c83-9f29-7e24dd55156b.png) | 1024×576 / 1672×941 |
| [37](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) | 42 | 2,488,823 | [Exact original PNG](https://finalvestige.com/wp-content/uploads/2026/08/c1237ffd-4a47-4988-8254-e3b021069e72.png) | 1024×576 / 1672×941 |
| [38](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) | 43 | 2,836,245 | [Exact original PNG](https://finalvestige.com/wp-content/uploads/2026/08/01340c2e-1165-4ca0-aa96-87398a83d13a.png) | 1024×576 / 1672×941 |

Five source originals total **13,267,538 WordPress stored bytes**. This is neither an actual browser payload nor a potential measured compression saving. The frozen research cohort is still 61 posts/355 images; the separate expanded cohort is 66/361. The reported 42 broken external originals remain guest-browser unconfirmed, and the claimed 76% real transfer reduction is still unmeasured.

All five public image URL opens on November 14 through the web retriever returned **tool inaccessible**, without reliable origin HTTP status, natural decoded dimensions or encoded transfer bytes. No image binaries were obtained. The distinct and newer authenticated WordPress edit source/Media Library metadata does verify the presence of those five stored URLs, dimensions and disclosure captions. The retriever result MUST NOT be represented as visitor-visible breakage.

## Critical visual-integrity gate: 960 does not automatically fit a 1024 image tag

The proposed maximum-width derivative is **960×540** (rounded proportional scaling from 1672×941), with no upscaling. It is a conditional geometry only, not an asset created or released. If a visitor actually sees the article image at 1024 CSS pixels, 960 source pixels provide only 0.9375 device pixels per CSS pixel on a 1× display. On a 2× display, the same file provides full density only up to 480 CSS pixels; on a 3× display, up to 320 CSS pixels. The HTML 1024 attribute alone does not tell us actual rendered CSS geometry: a browser measurement is mandatory. Never replace the existing image blindly with an undersized 960 rendition.

## Safe, reversible WordPress/CDN performance staging plan

1. Site QA #154 retains the **six original P0 browser-failure slots** and owns its CDP/Chrome collector. Do not add another collector. Rank verified actual missing images above this P1 performance cohort.
2. Confirm original production reuse rights, provenance and historical scene fidelity for all five reconstructions, including caption and alt-text preservation. First-party hosting is **not itself a legal clearance**; no license or rehosting permission was inferred. Do not swap a reconstruction for an archival image without editorial and item-level rights approval.
3. If licensed first-party binaries become available to an authorized staging job, build **offline** local WebP and AVIF candidate encodes at up to 960×540. Record SHA-256, actual encoded size, format, visual scene/crop parity, fine-detail/color/contrast quality review, and whether they remain legible at the intended CSS width and DPR. Neither this sprint nor the draft created/downloaded an image derivative.
4. Have Site QA measure actual rendered CSS dimensions, DPR, image currentSrc, srcset, intrinsic pixels, screenshots, complete CDP cache provenance, response MIME/status, and exact encoded network transfer bytes on logged-out cold desktop/mobile. Exclude memory/disk/service-worker cache bytes from uncached comparisons; do not mistake `Content-Length`, encodedBodySize, raw media-library size, or image catalog size for the same metric. Compute any percent reduction only on identical post/image-slot cohorts with unchanged scenes and consistent capture conditions.
5. Only if the candidate passes rights, sharpness, accessibility and network checks: plan a **reversible staging-only** native WordPress media/sizes/srcset path with explicit width/height, existing captions and ALT intact and rollback to frozen original URL. Avoid bulk Gutenberg HTML rewrites and avoid changing homepage design. Production writes, caching or rehosting, merges, deployment and spend remain prohibited.

## Machine-readable evidence and QA

Audit: `qa/media-recovery/five_reconstruction_p1_density_preflight_20261114.json`

Validator: `qa/media-recovery/validate_five_reconstruction_p1_density_preflight_20261114.cjs`

Tests: `qa/media-recovery/test_five_reconstruction_p1_density_preflight_20261114.cjs` — 39 cases (1 passing control, 38 adversarial) executed against the committed validator in an isolated V8 Node-compatible harness. Native Node CLI and repository CI still need execution; no browser proof supplied.

**Disposition: HOLD.** All 960px dimensions are conditional; encoded candidates and visitor bytes remain `null`; rights/quality approvals false; no WordPress writes or media downloads or cache.
