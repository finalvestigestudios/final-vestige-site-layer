# Seven-chapter homepage — NYPL capture rights-safe alternative (DRAFT / HOLD)
Date: 2026-11-02 | Parent candidate: PR #643 exact `59e5a88ed25334514b92573317c44b50dbb9f8f6`

## Why this alternative exists
The existing proposed homepage **embeds** NYPL Image ID 5003296 (1903 Brooklyn Rapid Transit system map) as a third archival image. Its caption now properly says digital capture rights are unresolved, but a disclaimer does **not** constitute reproduction permission. This independent branch offers an evidence-first, image-free way to retain the complete Malbone chapter while the exact capture's reuse rights remain unverified. Neither the embedded image nor a tracing/crop/derivative of it is shipped in this alternative.

## What changes
- Replace only the Malbone **embedded image** with original Final Vestige chronological typesetting: 1903 / fifteen years between / 1918. This is editorial typography, **not an archival facsimile, geographic alignment, rail plan or recreation of the map**.
- Keep all three investigation buttons and all seven chapters, Malbone source/limits disclosure, official NYPL catalog links, and the accurate explanation that the 1903 system map cannot depict the later temporary Malbone curve.
- Retain the NASA Apollo and Franklin historical images. Limit real HTTP image-payload admission to these **two** verified candidate images. Never treat image dimensions or filename alone as delivery proof.
- Introduce a fail-closed source parity guard against both sources silently re-embedding the unverified NYPL image, plus an HTTP gate that fails if the forbidden NYPL capture URL is requested.
- Preserve the site's charcoal/antique-gold palette, no-JS article meaning, WCAG-targeted semantics, reduced-motion options and existing Focus/Jetpack commercial boundaries.

## Authentic references, rights distinction
- Original map item: https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0 (NYPL ID 5003296).
- NYPL's own 1903 transit-map identification: https://libguides.nypl.org/nyc-rail-transit/companies.
- NYPL Digital Collections permissions policy: https://qa-digitalcollections.nypl.org/about .
- NYPL capture-specific rights model: https://api.repo.nypl.org/ (service marked deprecated August 1, 2026; not proof of capture clearance).
- No sourced evidence establishes permission for this **specific digital capture**; its U.S. public-domain status is **not claimed**. The original NYPL web page is linked; the image is not reproduced in the proposed homepage. Copyright review of any images retained elsewhere on the production site is a separate matter.

## Scope / release governance
This is a **separate optional, unmerged release candidate**, not a change to frozen PR #49, Apollo PR #158, Mind issue #171, WordPress.com page ID 6 or existing media. Unlike a true native WordPress.com Business staging clone, the isolated WordPress Playground/Assembler environment cannot prove Jetpack or Atomic host behavior. Independent QD, human browser zoom, screen reader and physical-device review, measured host performance, and founder publication approval remain mandatory. If capture-specific NYPL clearance is later established and its display is authorized, compare both candidates visually and by exact source SHA rather than silently restoring image bytes.

## Test plan
1. Source and proposed page-6 fixture interiors identical; source Git blobs pinned; two image sources only.
2. Original NYPL image URL absent from the proposed seven-chapter source, WordPress DOM and observed HTTP image responses.
3. No-JS Malbone source text and disclosure readable; keyboard/touch chapter switching and native details work.
4. Independent WordPress/Assembler Chromium five widths, image-body MIME/magic/bytes, axe and lab Lighthouse rerun, with actual viewport screenshots. A PASS in the isolated engine is **not** WordPress.com host acceptance.
5. No merge, WordPress changes, activation or publication during this sprint. Release remains HOLD.
