# USS Thresher post 220 — Navy archive provenance and 960px restoration gate (2026-11-05)

This is a **read-only catalog and live post source review**, NOT a CMS repair, image download, proxy, optimization claim, or proof of browser 404. Separate from the homepage design lead and Site QA PR #154. Exact live WordPress post #220 source was read with `posts_get(context=edit)` on November 5; publication status `publish`, last modified **2026-11-02T21:39:38**. All seven image URLs and ALTs were read from the live post and pinned in the JSON audit. Source data may change; re-read before any release.

## Findings

Six of seven published Wikimedia Special:Redirect/file items have an individually matching **official U.S. Navy NHHC catalog photo number**. The Commons original pixel sizes are below; they are *Commons rendition metadata*, not a physical inspection of the NHHC master binary or a current browser decoded image. The proposed derivative is capped at 960 pixels wide and never upscales.

| Slot | Navy catalog | Commons original | Conditional derivative | Identity |
|---|---|---|---|---|
| 220:0 | NH 97545 | 4918×6136 | 960×1198 | Catalog subject match |
| 220:1 | NH 97552 | 740×574 | 740×574 | Catalog subject match |
| 220:2 | NH 97310 | 578×737 | 578×737 | Catalog subject match |
| 220:3 | NH 97567 | 740×532 | 740×532 | Catalog subject match |
| 220:4 | Primary record unresolved | 1700×1349 | 960×762 | Secondary Commons/NavSource only |
| 220:5 | NH 97570 | 739×574 | 739×574 | Catalog subject match |
| 220:6 | NH 97557 | 740×576 | 740×576 | Catalog subject match |

**Editorial nuance:** Slot 220:2's ship portrait is cataloged as a late-1950s/1960s *Skylark* halftone, not a proven photograph taken on the exact April 10, 1963 dive. Slot 220:4 depicts a **mid-1964 reconfigured Trieste II**, not Trieste's August 1963 initial search phase. Slot 220:6's upper rudder photograph is dated **October 1964**, not an August 1963 recovery photograph. The article's captions appear broadly consistent, but keep chronology explicit. Navy identifies slot 220:3's watertight door as photographed **August 24, 1963** and slot 220:5's brass pipe as released **September 13, 1963**. These dates are not interchangeable with the submarine's loss date.

## Image availability and permissions

The Wikimedia Commons *catalog pages* were independently accessible in external research. **No** public logged-out Chrome capture could be made of `finalvestige.com` in this runner (DNS fail). Exact guest-browser `currentSrc`, image `naturalWidth/naturalHeight`, true original HTTP statuses, and transferred bytes are **null**. Seven Commons pages are accessible; that does NOT show seven Final Vestige image loads. No newly confirmed broken images, no 76% actual site-wide transfer reduction and no successful production repair.

NHHC identifies these six as official U.S. Navy photographs, commonly U.S. public-domain federal works. Commons asserts this licensing status. Slot 220:4 is labeled U.S. Navy public-domain on Commons but its exact primary Navy item identity has **not** been independently verified, so it is **rights/provenance HOLD**. All seven remain **item-specific reuse HOLD** for this workflow until verification of chosen binary, any overlays/scan additions, jurisdictional considerations, proper credit and attribution.

## Controlled staging, no publication authorization

If Site QA identifies a genuinely failed slot (or a separate editorial visual-identity correction is authorized): (1) verify exact historic subject and caption against listed catalog, (2) confirm item-specific rights and binary SHA256, (3) download only an authorized image to a nonpublic isolated staging folder, (4) create a derivative <=960px with no upscaling and no crop/ALT drift, (5) propose media-library attachment with attribution and rollback manifest, (6) compare logged-out desktop/mobile browser screenshot and cold CDP transfer bytes before and after, (7) seek separate production publication authorization. **No steps (3)-(7) have been executed.** Do not rewrite Gutenberg image blocks automatically. Preserve original URL/alt/credit and media ID as rollback data.

Frozen site baseline from Media Recovery #183 (not new full-site census): 61 posts/355 references/288 offsite origins, 13 first-party WP originals above 1.5MiB totaling 43,522,829 **stored** bytes. Reported 42 broken images are still visitor-unverified; claimed 76% reduction is not a measured site-wide *wire* saving. Do not claim it.

## Primary-source records

- **220:0**: [Navy NH 97545](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97545.html) — Bow view 24 July 1961.
- **220:1**: [Navy NH 97552](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97552.html) — Launching 9 July 1960.
- **220:2**: [Navy NH 97310](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97310.html) — Skylark halftone, late 1950s or 1960s; not necessarily 10 April 1963.
- **220:3**: [Navy NH 97567](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97567.html) — Watertight door seen 24 Aug 1963; official caption released 5 Sep 1963.
- **220:4**: No exact official Navy catalog located; [Commons secondary record](https://commons.wikimedia.org/wiki/File:Bathyscaphe_Trieste2_2.jpg) — Commons describes Trieste II configuration circa mid-1964, primary exact catalog not independently established.
- **220:5**: [Navy NH 97570](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97570.html) — Brass pipe recovered in second Trieste dive series, official caption released 13 Sep 1963.
- **220:6**: [Navy NH 97557](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-97000/NH-97557.html) — Upper rudder photographed October 1964; not 1963 recovery.

**Code QA:** `validate_thresher_220_navy_20261105.cjs` is offline fail-closed, and `test_thresher_220_navy_20261105.cjs` contains 31 native Node test cases. The exact validator logic was executed in this run in isolated V8 against the live-derived JSON fixture and 30 negative mutations (31/31 passed), not falsely described as native Node CI. **Do not duplicate Site QA's guest-browser collector**, or modify homepage design.
