# Experience 2.0 — archival media rights, capture lineage and network admission
**Review date:** 2026-11-06 (Pacific) · **Decision:** HOLD, review-only · **Source baseline:** draft PR #1232 at `34d752463419b9a95e465885f812c15dfb33a078`
**Scope:** Published WordPress Page 6; connected media IDs 473, 474 and 1258; isolated seven-chapter Assembler Playground Blueprint. Read-only collection; no deployment, paid services, image download, change to WordPress, or new merchant integration.

## Material findings

1. **We have an item-level identification for the NYPL map, but NOT a capture-level rights grant.** NYPL's own BRT research guide identifies the published 1903 *Map of the borough of Brooklyn, N.Y., and vicinity showing the street railway system controlled by the Brooklyn Rapid Transit Co.*, catalog shelf **Map Div. 14-1309**, creator **Street Railway Journal**, and its digital item link. The companion NYPL guide names **Image ID 5003296**, matching media #1258's filename. The NYPL guide links item UUID `c745e730-d2a9-012f-5ecc-58d385a7bbd0` at `https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0`. Direct access to the item/capture rights field returned HTTP 403 in the research browser. **The rights of this exact capture remain UNVERIFIED**, irrespective of a public-domain claim in WordPress metadata or third-party reposts. NYPL states rights are documented at capture level, with distinct outcomes including CC0, no-known-U.S.-copyright, copyright held/managed, and undetermined. Leave this map **OUT of the portable Playground**; do not remove or replace the already published image without approved release governance.
2. **The Franklin image's underlying Wikimedia Commons file is explicitly marked public domain, but is a printed reproduction.** `File:Franklinexpeditionnote.jpg` is identified by Commons as a scan from McClintock's **1869** *Voyage of the Fox*, displaying the 1847 message and 1848 added message. It is not a 2026 photograph of the original Royal Museums Greenwich museum object. WordPress media #474's caption correctly identifies the 1869 reproduction. The WordPress upload is **960 × 1526 px, 466,043 bytes** per REST *metadata*, not a verified browser download; its modified/cropped identity has not been bitwise compared with Commons. Editorial copy must distinguish reproduction from autograph/museum facsimile.
3. **Apollo image may be used as editorial evidence subject to NASA rules, not as a commercial endorsement.** WordPress media #473 is `s67-19766.webp` (1041 × 810; 78,346 bytes *metadata*), credited as NASA image S67-19766. NASA's Apollo 1 gallery verifies the crew/historical incident, but independent original-item provenance for the **precise S67-19766 file** was NOT established this session. Some search results concern a different identifier, **S67-19770**; do not conflate them. NASA's current brand/media guidance generally allows informational uses of its publicly available imagery with acknowledgement, but expressly prohibits implying NASA endorses commercial products and restricts use of NASA names/insignia and some astronaut likenesses in advertisements. Keep this crew photograph tied to an investigation/source context, **not** Mini Museum or Inspire3 paid-product artwork.
4. **Cross-origin archival image selection is not automatically first-party.** The #1232 Blueprint's two archive `<img>` elements have `src` at `finalvestige.com`, but **their `srcset` candidates all point to `https://i0.wp.com/finalvestige.com/...`**. An actual responsive browser may select the WordPress image CDN rather than the first-party origin. The existing source checks alone cannot certify selected `currentSrc`, redirect chain, final host, HTTP status, decoded pixels, downloaded bytes, or whether the user reached a first-party asset. Browser admission should record both selected URL and actual responses and distinguish approved CDN delivery from origin delivery, without falsely claiming first-party network transfer. Do not change image URLs on production without measured tests.

## Source and comparison receipts

| Asset | WP media / measured *metadata*, not transfer | Independent source and claims | Decision |
| --- | --- | --- | --- |
| Apollo 1 crew training | #473, `s67-19766.webp`, 1041×810, 78,346 metadata bytes; caption credits NASA S67-19766; exact downloaded image not checked | NASA Apollo 1 gallery and NASA brand/media policy. Photo's exact S67-19766 original record still to be matched; NOT interchangeable with S67-19770. | **EDITORIAL ONLY / CONDITIONAL** — item-level original, actual bytes and on-page caption to verify |
| Franklin Victory Point note | #474, `Franklinexpeditionnote.jpg`, 960×1526, 466,043 metadata bytes; WordPress notes McClintock 1869 reproduction | Wikimedia Commons exact file page marks public domain and links its 1869 reproduction provenance. | **PUBLIC-DOMAIN SOURCE IDENTIFIED / CAPTURE-MATCH PENDING** — measured transfer and caption QA needed |
| NYPL Brooklyn BRT map | #1258, `edit-017-v02-nypl-5003296-original.jpg`, 5667×3831, 5,553,669 metadata bytes (smaller 768/1024/1536 derivatives listed) | NYPL BRT guide item ID 5003296, shelf Map Div. 14-1309 and digital collection item UUID above; direct capture rights field inaccessible in this session | **CAPTURE RIGHTS NOT VERIFIED** — exclude from isolated package pending NYPL capture-specific rights; live remains unchanged |

### Primary and repository links

- NYPL official BRT map list: https://libguides.nypl.org/nyc-rail-transit/brt
- NYPL official confirmation of Image ID 5003296: https://libguides.nypl.org/nyc-rail-transit/companies
- NYPL linked item page (capture rights field still needs direct access): https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0
- NYPL rights taxonomy: https://api.repo.nypl.org/api_documentation_v1
- NYPL public-domain item policy: https://qa-digitalcollections.nypl.org/about
- Commons Franklin original and licensing: https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg
- NASA Apollo 1 primary gallery: https://www.nasa.gov/gallery/apollo-1/
- NASA media/identity restrictions: https://www.nasa.gov/nasa-brand-center/
- NASA advertising/endorsement rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/
- Source-controlled Playground review: `experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json` at `34d752463419b9a95e465885f812c15dfb33a078`
- Published Page 6 modified `2026-11-05T12:07:24`, read with WordPress edit-context connector. **Do not assume its editor source == browser DOM.**

## Required release actions (read-only until separate approval)

**Owner: Media/editorial reviewer.** Obtain the NYPL *capture-specific* rights statement for image ID 5003296 (exact item UUID), record its public permalink/rights classification; separately verify precise NASA image S67-19766 catalog original and subject/context. Do not treat labels on generic collection pages, WordPress self-entered metadata, or third-party mirrors as rights proof.

**Owner: Homepage/independent Site QA.** In isolated WordPress Playground with actual Assembler, capture archive `img.currentSrc` after responsive `srcset` selection at 320/360/390/768/1440/1920. For each selected URL, log redirect chain, final host, response status/content type, body bytes, SHA-256, and `naturalWidth/naturalHeight`; assert two source-approved images decode. Include network failure/CSP scenarios and 200% zoom. Separate `finalvestige.com` vs `i0.wp.com` deliveries. No invented Lighthouse, field CWV or WCAG claims.

**Owner: Art director/conversion QA.** Keep primary investigation context/caption by each evidence plate, never visually attach the NASA crew photo to affiliate CTA as a promotional endorsement. Preserve the free 52-page Focus Fieldbook, Jetpack signup, seven chapters and all 72 Margins records; proposed Hero→Focus CTA remains an *unreleased experiment*, not a paid sale.

**Owner: Claude/independent QD.** Perform permissioned production-host acceptance and verified attribution separately; WordPress Personal lacks native staging. An isolated Playground can establish browser/frontend behavior but cannot certify Jetpack email, WordPress.com redirects, host cache/cookies or actual paid conversion. Exact-HEAD CI/QD and founder release approval remain mandatory. **No production write / no merge / no deployment**.

## Verification boundaries
Source: connected WordPress media metadata and read-only Page 6; exact GitHub #1232 source; linked first-party NASA, NYPL and Commons policies. HTTP/download measurements were NOT run in a network-capable Chromium session. This receipt is **rights/provenance research**, not a license opinion, clearance certificate, browser pass or release approval.
