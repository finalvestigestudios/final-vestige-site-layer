# Media Recovery — 81-host blast radius and source-only risk queue (2026-11-06)

**Scope:** Independent media integrity and performance evidence. Read-only GitHub-derived inputs. Does not touch homepage design, Site QA #154 collectors, published Gutenberg content, WordPress Media Library or subscriptions. This is a separate, small **main-based** review rather than adding more commits to the broad draft PR #183.

## Exact provenance and denominators

- Source: eight frozen `qa/media-recovery/parts/*.json` inventories (October 30, 2026; **61 articles, 355 stored <img> references**), plus `new_five_post_six_images_20261106.json` from read-only CMS inspection (**five newer published articles, six images**). The machine audit pins all nine exact Git blob SHAs.
- As of the source snapshots: **66 published articles; 65 contain stored inline <img> tags; one published article (post 1922, Change Blindness) has zero**. Do not mistake zero-image article for a broken image.
- **361 total stored source image references, 359 unique exact URLs, 294 external-origin slots, 67 first-party/first-party-Jetpack-proxied slots, 311 missing one/both intrinsic width/height attributes**, and **81 effective upstream hosts**. Figures are source-level, not loaded browser resources.
- `i0.wp.com/<external-host>/...` remains **externally dependent** despite the Jetpack request domain. The inventory distinguishes upstream/provider host from request host. **13 upstream hosts** account for at least four image references each.
- This does **not** prove actual browser failures or CLS. A host outage is a conditional blast-radius model, **not a measured outage**; for Commons redirect sources, the browser can ultimately request a different CDN.

## Highest-concentration publishers — number of stored references and affected article IDs

| Effective upstream | References | Published articles | Browser-confirmed failures |
|---|---:|---:|---|
| commons.wikimedia.org | 124 | 24 | Unknown |
| upload.wikimedia.org | 18 | 10 | Unknown |
| www.history.navy.mil | 15 | 4 | Unknown |
| d9-wret.s3.us-west-2.amazonaws.com (official USGS image hosting) | 9 | 2 | Unknown |
| www.floridamemory.com | 7 | 1 | Unknown |
| cdn.loc.gov + tile.loc.gov | 14 combined | See exact machine rows | Unknown |
| images-assets.nasa.gov | 5 | 1 | Unknown |
| media.defense.gov | 5 | 3 | Unknown |
| www.history.uscg.mil | 3 | 1 | Unknown |

**Important:** first-party Final Vestige plus its `i0.wp.com/finalvestige.com` transforms accounts for **67** slots in **25** articles. Do not interpret those as offsite publisher media. Wikimedia redirect file pages (124) and Wikimedia static upload host URLs (18) are separate raw upstream classes and should not be merged without browser network evidence.

## Actual source retrieval observations (November 6, 2026; NOT Chrome/network status)

- **287:5 old Sunshine Skyway publisher URL:** web retriever reports **404** for `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`; the publisher's newer `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` **renders in the retriever**. They refer to an old bridge-wreckage scene, not the later replacement bridge. Photo credits/redistribution rights remain subject to publisher review. Do not mirror or rewrite content automatically.
- **418:2 original USCG debris URL:** web retriever reports **403**, not proof of guest-browser failure: `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg`. Museum 600×463 rendition of the named scene requires attribution, exact-subject and reuse checks before any localization.
- The other four existing P0 slots were **not** independently probed in this particular run. All six image slots retain **NULL actual origin/browser status**.

The machine audit records actual stored URLs and the separate result-method field; it never turns a third-party retriever 403/404 into visitor-browser evidence.

## Six-image recovery candidates; no automatic swap

| P0 slot | Exact/potential archival source | Visual integrity | Conditional size / rights |
|---|---|---|---|
| 285:5 | [Publisher-linked Commons Three Mile Island image](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) | Exact transformed crop not proven | Listed 819×614, never enlarge to 960. PD-self catalog, verify uploader and attribution. HOLD. |
| 285:2 | [1979 Commission report / TMI-2 tagged-control-panel photo](https://commons.wikimedia.org/wiki/File:TMI-2_control_panel.png) | NRC inspector photo is **not** the tagged-control-panel event image; retouch review required | 604×590 catalog image, never enlarge. Original federal provenance and rendition rights review. HOLD. |
| 287:5 | [Current St Pete Catalyst photo URL](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg); [Florida Memory archival alternative](https://www.floridamemory.com/items/show/131903) | First is original publisher relocation, second 1987 old/new bridge view, not interchangeable | Master geometry and publisher reuse clearance unverified; conditional ≤960, no upscale. HOLD. |
| 418:1 | [Coast Guard catalog, VIRIN 210330-G-DE713-0002](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) | Official portrait ID matches stored image stem; Pettit/Petit spelling disputed | Pixels unknown; USCG/DoD credit and reuse rules. HOLD. |
| 418:2 | [National Coast Guard Museum historical article](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) | Named 1946 debris scene; avoid NOAA's erroneous 1964 date | Known preview 600×463, no upscaling; museum rehosting rules. HOLD. |
| 407:1 | [USGS primary catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959-0) | Catalog Original link matches published URL; retrieval-wrapper binary unsupported is not breakage | Dimensions pending; USGS public-domain catalog with J. R. Stacy credit; keep existing unless guest failure is verified. HOLD. |

Other authoritative-source exploration (Navy, NASA, Coast Guard, Florida Memory, NARA/USGS) must be scoped to actual failing URLs. Rights are **item-specific**; an official federal agency page is not a universal clearance to copy website photographs.

## Safety-first 960px and WordPress recovery protocol

1. Site QA #154 uses its **existing** logged-out Chrome desktop/mobile collector for the six P0 slots, and captures `currentSrc`, `naturalWidth/naturalHeight`, network Image request IDs, true browser HTTP/failure, redirect chain, decoded geometry and cold cache/encoded transfer bytes. At least one successful comparison source per article prevents false domain-block diagnoses. No new competing collector here.
2. Restore only a **visitor-confirmed** missing specific image after verifying archival item identity, date, crop, caption/ALT semantics, photographer/rights/license/credit/nonendorsement, download permissions, and exact usable dimensions. Fail closed when any are unknown.
3. For permitted reuse, create a separately named candidate media file in **nonproduction staging**, downsize to `min(960, original_width)` while preserving aspect ratio, orientation, legibility and (if applicable) transparency. Detailed maps/documents must preserve access to full-resolution views. Run the existing visual-identity comparator; do not replace historic photo with a merely related event photo.
4. Once explicitly authorized, prefer a new WordPress Media Library filename/attachment (and native responsive `srcset`/intrinsic dimensions) rather than overwriting cached originals. Check CDN/Jetpack transformation and attribution/caption. Save rollback mapping `post_id:slot -> original exact URL` before any controlled post block changes. **No production edits authorized in this branch.**
5. Prove image-weight reductions only by paired **cold**, same viewport/scroll, uncached network comparisons of actual decoded image assets and encoded transferred bytes (account for reused identical URLs, CSS/background/featured assets, caches, redirects and responsive variants). The **76% proposal remains unmeasured**; the 43,522,829 bytes in 13 >1.5 MiB WordPress originals are *storage bytes*, **not browser transfer**. Address true broken images first, then prioritize the five 1672×941 first-party no-subsize PNGs in posts 34–38 and large Malbone originals after matched browser measurements.

## Validation and safety boundaries

- Data: `qa/media-recovery/host_blast_radius_verified_20261106.json`, including all 81 effective upstream hosts, post IDs, exact sample URLs, source snapshot Git SHAs, and six unchanged P0 URLs/statuses.
- Offline validator: `qa/media-recovery/validate_host_blast_radius_20261106.cjs`; `qa/media-recovery/test_host_blast_radius_20261106.cjs`. Fail-closed checks separate source retrieval from browser success and forbid changing copyright/960px/WordPress HOLD states.
- Tested with **23 independent isolated V8 assertions** against the exact proposed validator and audit, all passed; Node-native test source is committed for CI but native Node and Chrome integration are not claimed here.
- Production WordPress writes **0**, binary downloads **0**, media caches **0**, paid subscriptions **0**, homepage changes **0**, verified visitor-facing broken images **unknown** (not 42).
