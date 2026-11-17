# USS Thresher photographic recovery — complete seven-slot custody review
**Audit date:** October 31, 2026. **Source:** WordPress published post 220, `Too Deep for the Rescue Bell`, modified 2026-10-29 18:25:46; seven current `src` and complete ALT values verified against the frozen 61-post/355-image census via authenticated, READ-ONLY `posts.get(context=edit)`. No production WordPress writes.

## Exact-source review (institutional *records*, not downloaded assets)
Six of the seven existing Commons hotlinks are independently cross-referenced to **specific US Navy Naval History and Heritage Command** photograph catalogs. The seventh (Trieste II) is an exact Commons *file page*, with a Navy/secondary NavSource source claim but **no independently matched NHHC photo ID**.

| Slot | Individual Navy photo identifier | Commons original dimensions (metadata, NOT browser decoded) | Conditional no-upscale derivative | Source status |
|---|---|---|---|---|
| 220:0 | NH 97545 | 4918×6136 | 960×1198 | Exact Navy catalog/Commons cross-reference |
| 220:1 | NH 97552 | 740×574 | 740×574 | Exact Navy catalog/Commons cross-reference |
| 220:2 | NH 97310 | 578×737 | 578×737 | Exact Navy catalog/Commons cross-reference |
| 220:3 | NH 97567 | 740×532 | 740×532 | Exact Navy catalog/Commons cross-reference |
| 220:4 | No official image ID independently matched | 1700×1349 | 960×762 | Commons/NavSource only; source-identity gate HELD |
| 220:5 | NH 97570 | 739×574 | 739×574 | Exact Navy catalog/Commons cross-reference |
| 220:6 | NH 97557 | 740×576 | 740×576 | Exact Navy catalog/Commons cross-reference |

Source ledger with all seven **current stored URLs and full ALT**, individual Commons file pages, official Navy record links where verified, image chronology, dimensions, proposed widths, rights flags and explicitly **null network observations:** `qa/media-recovery/thresher_220_navy_primary_20261031.json`.

Primary institutional record URLs:
- `220:0` [NHHC NH 97545](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97545.html)
- `220:1` [NHHC NH 97552](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97552.html)
- `220:2` [NHHC NH 97310](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97310.html)
- `220:3` [NHHC NH 97567](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97567.html)
- `220:5` [NHHC NH 97570](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97570.html)
- `220:6` [NHHC NH 97557](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97557.html)
- `220:4` [Commons Bathyscaphe Trieste2 2.jpg](https://commons.wikimedia.org/wiki/File:Bathyscaphe_Trieste2_2.jpg) — *specific NHHC catalog ID not established*. The Commons record describes the later **1964 Trieste II** configuration, not the original bathyscaphe **Trieste** that photographed Thresher in 1963. Do **not** silently substitute a different Trieste image. The displayed ALT already says "later surveys"; keep it historically specific.

**Two editorial guardrails:** `220:2` NH 97310 is a **circa late-1950s/1960s** publicity halftone of USS Skylark, **not verified as a photograph taken during the April 1963 rescue-watch operation**; distinguish the depicted ship from the photograph's date. `220:6` NH 97557 is the rudder photographed in **October 1964**, not in the immediate April 1963 aftermath. The Navy's `220:3` watertight-door image NH 97567 dates to **August 24, 1963**. The changes are **editorial proposals**, not a published post rewrite.

## Rights and safe first-party caching / WordPress media plan
All six matched NHHC records describe official Navy photography. Commons marks the seven files under a U.S.-Navy-public-domain rationale, but the NHHC notes that **most, not necessarily all** photographs are public-domain. Check each catalog/image rights notice and retain exact institutional photo ID, credits and current ALT before approval; the seventh photo requires independent original-source custody confirmation. No license or permission has been conclusively cleared for WordPress republishing here.

Five documented Commons originals are **narrower than 960px** and should not be enlarged. Two (`220:0`, `220:4`) exceed 960px and have bounded proposals **960×1198** and **960×762**, respectively. Metadata describes the **Commons original**; actual `?width=1280` response, WordPress/Jetpack proxy rewrites, encoded bytes and intrinsic dimensions must be tested in a guest browser first.

If a source is **visibly broken in Chrome** and item-level rights & exact-image binary identity are independently approved: obtain the authorized master once through the institution's permitted access workflow, record SHA-256 and credit, prepare a visually inspected ≤960px responsive derivative with no upscaling, assign a distinct *new* WordPress Media ID only in an approved release, preserve caption/ALT/catalog attribution and permalink, verify mobile/desktop `currentSrc`, image HTTP GET/content-type, decoding and LCP/CLS. Keep the original public post unmodified until separately authorized. No wholesale mirroring of Commons originals or risky Gutenberg block replacement.

## Measurement and release restrictions
The **42 reportedly broken images are still unverified**, and a **76% image-byte reduction is not a measured improvement**. This source batch captures neither visitor HTTP status nor image-transfer bytes, and it has **no master binaries or SHA-256**. Do not conflate Commons displayed file dimensions with actually delivered network size, or citation-level public-domain rationales with legal approval.

The pure read-only validator `qa/media-recovery/validate_thresher_220.cjs` rejects source/ALT drift, impostor Navy IDs, fabricated network observations, incorrect width/aspect ratio, upscaling, or any premature asset/CMS release. Adversarial `test_thresher_220.cjs` contains **25 tests**, all **25 passed in exact-committed-GitHub-source V8 replay**; **native Node CI and network-connected Chrome remain unexecuted**.

**No production writes, copyrighted image downloads, homepage edits, duplicate Site QA #154 draft work, or spending.**
