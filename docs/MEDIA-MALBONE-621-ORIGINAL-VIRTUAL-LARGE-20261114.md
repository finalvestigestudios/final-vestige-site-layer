# Malbone published post 621 — original-src versus virtual-large preflight (Nov 14, 2026)

Authenticated, read-only WordPress `posts.get(621, edit)` and `media.get(1257/1258)` confirmed **two `sizeSlug:large` Gutenberg blocks whose stored `img src` points to first-party originals**. A front-end visitor may instead receive a Jetpack transformed `currentSrc`; no actual guest network response, decoded image, CSS width or bytes have been measured. Treat as **source-level performance risk, not demonstrated 10.35MB visitor download**.

| Position | Original URL | Original stored bytes | Native dimensions | Existing WordPress virtual large URL | Conditional geometry |
|---|---|---:|---|---|---|
| 621:0 | [GeneralPunger tunnel](https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg) | 4,798,395 | 4000×3000 | [1024×768 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v01-malbone-tunnel-generalpunger-original.jpg?fit=1024%2C768&ssl=1) | 960×720 |
| 621:1 | [1903 NYPL map](https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg) | 5,553,669 | 5667×3831 | [1024×692 proxy](https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg?fit=1024%2C692&ssl=1) | 960×649 |

Both proxy URLs are **WordPress metadata descriptors** `virtual:true`, *not* verified asset responses or local subsizes. The published 2021 GeneralPunger photograph is documentary evidence of the surviving tunnel, not a 1918 scene. Caption claims CC BY-SA 4.0; **exact Commons file not identified**, so credit/ShareAlike/change notice and item identity remain review gates.

[NYPL's primary map record](https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0) identifies the Street Railway Journal 1903 Brooklyn BRT map and states NYPL believes it is in the U.S. public domain, without clearance in other jurisdictions. The uploaded JPEG binary/crop has not been proven identical. Smaller renditions must preserve readable map labels and zoom/full-resolution access.

At conditional maximum 960 source pixels, upper supported CSS widths are **960px at DPR1, 480px at DPR2, 320px at DPR3**. If actual display size needs higher density or map detail, do **not** mandate 960px. Ask Site QA #154 to append to its existing collector *after P0 six*: cold guest `currentSrc`, `naturalWidth/Height`, CSS dimensions, DPR, response/cache provenance and encoded transfer bytes; compare representative viewport/connection and editorial visual/zoom quality. Only then propose reversible WP staging and compare before/after. No third-party file downloads, caching, production Gutenberg edits, homepage changes, merges, deployments or spending.

Historical 61 posts/355 inline images; 42 alleged failures remain browser-unconfirmed; 76% visitor-byte reduction unmeasured. Current oversized-original cohort: 16 media totaling 49,107,665 stored bytes. This Malbone pair is 10,352,064 stored bytes, **not measured transfer savings**.
