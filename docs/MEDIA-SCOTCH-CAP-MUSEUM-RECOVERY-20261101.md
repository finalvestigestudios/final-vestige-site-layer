# Scotch Cap: 3-image Coast Guard/Museum recovery crosswalk (2026-11-01)

**Scope:** Isolated image-recovery evidence, not a public browser result or CMS change. Current source strings are from the frozen published inventory in PR #183. Site QA PR #154 retains logged-out browser verification.

## High-value exact-scene discovery

Final Vestige post **418**, image **418:2**, currently uses `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg`. An independent web-image retriever returned **403**; this does not prove a visitor-facing 403.

The [National Coast Guard Museum's 2024 Scotch Cap article](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) publishes a **600×463 JPG** named `5_-Scotch_Cap_debris2_1946-600x463.jpg`, captioned as the remains of Scotch Cap Lighthouse photographed from the bluff, credited to the **U.S. Coast Guard**. This is a stronger *same-named historical scene* candidate for the broken external reference than an unrelated disaster photo. The historical source cannot currently be compared byte-for-byte or crop-for-crop; **do not claim exact binary match**.

The Museum also illustrates **debris1** (a separate overhead rubble-pile scene, 600×471) and **debris3** (a different surviving-wall photograph, 600×458). These are **not interchangeable** with the debris2 source. Two separate images being about the same disaster is insufficient evidence of a faithful replacement.

**418:0** has a candidate Museum preview (`2_-new-and-old-lighthouses-19849609-e1728394749751-600x480.jpg`) credited to USCG, depicting the same snowy pre-tsunami scene as the original title/ALT, but visibly cropped or transformed. Its original filename suggests 1200×984, which is NOT independently verified master dimensions. Keep a cautious identity state and no silent substitution.

**418:1** USCG's [individual photo catalog record](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) directly provides a different `media.defense.gov` asset path under `2002905913` but with the **same unique VIRIN/filename** `210330-G-DE713-0002.JPG` as Final Vestige's original `2002610812` path. The official photograph page reports that this image is **public domain, cleared for release, credit required**, with DoD restrictions covering endorsement and recognizable subjects/marks. This is an exact catalog/VIRIN relationship, not a verified matching hash or crop. The Coast Guard photo caption says **Pettit**, while a casualty listing says **Petit**: retain the existing ALT pending editorial source review.

## Actual observation and no-upscale sizes

| Slot | Original web-retriever outcome | Primary institutional derivative | Conditional non-upscaled width/height |
| --- | --- | --- | --- |
| 418:0 | No origin HTTP response obtained | National Coast Guard Museum, pre-1946 two-lighthouse scene | 600×480 |
| 418:1 | Retriever 403, not visitor 403 | Official USCG photo catalog / alternate media.defense.gov VIRIN route | Unknown; do not invent 960px height |
| 418:2 | Retriever 403, not visitor 403 | National Coast Guard Museum, filename/scene `debris2` | 600×463 |

All three candidates remain **rights/cache/WordPress HOLD**; the two Museum image *derivatives* require separate rights and modification review. Museum credit to USCG establishes provenance but does not automatically license a privately hosted derivative for redistribution.

## Cache/remediation release sequence

1. Site QA #154 independently verifies visitor-facing desktop/mobile `currentSrc`, final network URL/HTTP, `naturalWidth`, screenshot, encoded image bytes and possible cross-origin 403 for **418:0/1/2**.
2. Check the actual missing image against the candidate scene/crop. Record permitted master SHA-256, dimensions, creator, explicit credits and rights decision. Never substitute the different debris1 or debris3 photographs.
3. Only after explicit release authorization, create <=960px **no-upscale**, aspect-preserving media in WordPress (using responsive image variants where already present), retain historic ALT/captions unless approved editorial correction, then compare complete visitor-network transfers and visual screenshots.
4. Neither the reported **42** broken images nor **76%** saved image weight is established by this source-only batch. The site inventory still contains **61** posts, **355** source references, **288** external references, and **13** WordPress originals exceeding 1.5 MiB. **Production replacements: zero.**

## Evidence and automated safeguards

- Machine-readable three-slot ledger: `qa/media-recovery/scotch_cap_museum_sourcecrosswalk_20261101.json`.
- Deterministic read-only validator: `qa/media-recovery/validate_scotch_cap_20261101.cjs`.
- Regression tests: `qa/media-recovery/test_scotch_cap_20261101.cjs` with 27 cases guarding provenance, wrong-photo substitution, guest-browser claims, 960px/no-upscale, rights and no-write gates.
- Native Node CI, original hashes and logged-out Chrome proof must be executed in a network-enabled, appropriate deployment testing environment. No third-party image was scraped or downloaded, no WordPress post touched, and no homepage design changed.
