# West Loch 1944: eight-image primary-source custody / rights-closed 960px plan

**Read-only review:** 2026-10-31. Article [370, *The Lines Were in the Fire*](https://finalvestige.com/2026/08/19/the-lines-were-in-the-fire-west-loch/) (WordPress editor source modified 2026-10-29T15:27:15): **8/8 exact current src URLs and 8/8 full ALT texts** independently matched the frozen 61-post/355-image census. Four references point to `history.navy.mil/bin/imageDownload`; the other four are already first-party `/wp-content/uploads/`. This does **not** constitute a logged-out browser HTTP/decode test.

## Four exact Navy catalog IDs embedded in the current external source URLs

| Slot | Primary photo/catalog record | Historically precise identification | Optional 960px conditional sizing |
|---|---|---|---|
| 370:0 | [NHHC 80-G-276907](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276907.html) | West Loch T-8/T-9 aerial with burning LSTs, 21 May 1944 | high TIFF catalog 4320×4530 → **960×1007** |
| 370:1 | [NHHC 80-G-202485](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/80-G-202000/80-G-202485.html) | **Bougainville 6 Nov 1943**, USS LST-353 unloading troops; historical context, *not* a 1944 fire photograph | **unknown**; NHHC mirrored records report differing high-res dimensions |
| 370:3 | [NHHC 80-G-276940](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276940.html) | Burned/grounded LST-39 off Naval Ammunition Depot, 22 May 1944 | 6254×5002 → **960×768** |
| 370:4 | [NHHC SC 427947](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/sc-series/SC-400000/SC-427947.html) | Army Signal Corps firefighting, 22 May 1944. NHHC says possible **LST-480** and **probably USCGC Woodbine**; avoid definitive identifications | 6084×4942 → **960×780** |

The exact photo number is evident within the encoded `image=` parameter of each stored URL and independently appears on its NHHC catalogue page. These are original **identity/custody associations**, *not* binary master SHA matches, successful live image downloads, or blanket rights clearance. Original TIFF dimensions describe NHHC high TIFF files, **not** the site's delivered JPEG/Jetpack pixels. The conditional sizes are usable only if the unmodified exact master is later obtained and checked.

## Four already first-party photographs — preserve rather than duplicate

| Slot | WordPress filename | Provenance evidence level |
|---|---|---|
| 370:2 | `west-loch-lst-480-lst-39-burning.jpg` | NHHC [West Loch history](https://www.history.navy.mil/browse-by-topic/wars-conflicts-and-operations/world-war-ii/1944/west-loch.html) cites Army Signal Corps **SC 185701** for LST-39 firefighting; plausible caption/photo correspondence, **not byte-matched**. |
| 370:5 | `west-loch-lst-480-afire-again.jpg` | NHHC [80-G-276945](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-270000/80-G-276945.html) describes the **23 May 1944** LST-480 reignition scene; no current WordPress master hash or pixel comparison. Conditional high-TIFF 6286×5018 → **960×766** only if same original/crop. |
| 370:6 | `west-loch-lst-480-overhead.jpg` | [Commons description](https://commons.wikimedia.org/wiki/File:LST-480_following_West_Loch_disaster.jpg) attributes **SC 276944** to the Army Signal Corps. A separate secondary ship-history index appears to omit one digit, so official-photo ID confirmation and visual binary comparison remain **HOLD**. |
| 370:7 | `west-loch-unidentified-headstone.jpg` | Headstone photo has **no independently verified image author/archival item**; no invented provenance or permission. |

## Rights / optimization / WordPress caching decision gate

[NARA](https://www.archives.gov/research/still-pictures/publish-photos) says most federal photographic records can be published without special permission but some records carry restrictions; the user must verify specific item restrictions and credit the photo ID. [NHHC](https://www.history.navy.mil/content/history/nhhc/about-us/instructions-and-forms/obtain-duplications-of-records-and-photos.html) says a majority of its photos, not all, are public domain. The batch's individual reuse status is therefore `HOLD_item_level`; **no assets copied, edited, uploaded, or cleared**.

For an image proven *actually missing to visitors*, first capture logged-out desktop/mobile `currentSrc`, Image network request/final status, image content type, `naturalWidth`, screenshot and encoded transfer. Match exact master identity and inspect reuse restrictions. Only then stage a visually verified, aspect-preserving ≤960px derivative (WebP/JPEG appropriate to photo, no upscaling); record original and output SHA-256, credit and alt, proposed WordPress Media ID, delivered responsive `srcset`, cache behavior and before/after image bytes/LCP/CLS. Preserve pre-existing first-party assets and unchanged historical captions unless separately editorially reviewed. Never copy entire source websites, bypass redirects or perform production post-block rewrites.

**Machine readable:** `qa/media-recovery/west_loch_370_custody_20261031.json`, validator `validate_west_loch_370.cjs`, tests `test_west_loch_370.cjs`. **37/37** tests passed in isolated V8 replay of **exact committed GitHub blobs**, not native Node CI or live Chromium. Site QA PR #154's source classifier and homepage art direction remain untouched.

**Still unverified:** the reported 42 broken original images, claimed 76% transferred-weight reduction, and actual serving sizes/bytes of 13 originals above 1.5 MiB. Production changes = **0**.
