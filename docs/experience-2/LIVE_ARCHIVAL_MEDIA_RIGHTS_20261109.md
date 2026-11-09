# Source-led media and rights custody: FINAL VESTIGE flagship (2026-11-09)

**Status: audit evidence / not release approval.** On a fresh read-only authenticated Page 6 retrieval, modified 2026-11-05T12:07:24, there were 150710 Gutenberg source characters, 26/26 source checks passing; 10/10 actual-source negative mutations rejected. These checks ran in a V8 isolate. Full editor content was **not** committed or copied to GitHub.

## Three published archive assets

| WP media | Source and stored size (WordPress metadata; NOT HTTP bytes) | Rights evidence and caveat |
|---|---|---|
| 473 | NASA S67-19766 / s67-19766.webp, 1041x810, 78,346 bytes | Credited NASA in WP caption. NASA https://www.nasa.gov/nasa-brand-center/ prohibits implied commercial endorsement; item-level archival match still needs independent official original. NASA Apollo 1 collection: https://www.nasa.gov/gallery/apollo-1/ |
| 474 | Victory Point / Franklinexpeditionnote.jpg, 960x1526, 466,043 bytes | https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg identifies a 1869 printed reproduction, marked public domain. Current folio distinctly states editorial typesetting, not a facsimile. Physical object: https://www.rmg.co.uk/collections/objects/rmgc-object-504898 |
| 1258 | 1903 NYPL Brooklyn Rapid Transit map, 5667x3831, 5,553,669 bytes | https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0 says believed public domain **under U.S. law**, explicitly no international copyright determination. Do not claim worldwide rights. |

The live editor tags use descriptive alt text, width/height and responsive srcset/sizes with lazy loading. The NYPL image's default src is the 1024x692 Jetpack CDN transform, **not** the 5.55 MB source. Its actual transferred byte count and image decode are not measured. Media metadata alone is no delivery evidence.

### Release gates still open

1. Real anonymous-host browser/network receipt (HTTP status, downloaded bytes, MIME, natural sizes, srcset per 320/390/768/1440/1920 and DPR2). Container internet DNS is unavailable; WordPress.com screenshot service marked a capture ready but did not provide inspectable pixels. **No browser-pass claim.**
2. Rights review for NASA exact photo ID, preservation of attribution and nonendorsement; note NYPL geographical limits. Keep these archives away from marketing imagery for Inspire3/Mini Museum without additional clearance.
3. Genuine WCAG 2.2 AA screen-reader/keyboard/reduced-motion/200%-zoom, honest Lighthouse and field-CWV measurements, CI/QD and founder release approval.
4. Commercial dependency remains **P0**: PR #1681 false-signup success repair and PR #1726 paired CTA/Focus hold. No new homepage CTA should be released before real Jetpack acceptance. Never count CTA clicks as sales.

This PR adds read-only source guards, documentation and local test coverage only. No CMS writes, no raw source export to repository, no affiliate links, no commercial product claims, no changes to PR #49, no production deployment.
