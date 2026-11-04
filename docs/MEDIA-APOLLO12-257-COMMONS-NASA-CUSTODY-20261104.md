# Media Recovery — Apollo 12 post 257, seven Commons / NASA image-source identities (2026-11-04)

## Verified custody and evidence limitations

Independent of homepage visual design and Site QA's separate PR #154. Frozen published WordPress content from 2026-10-30 `qa/media-recovery/parts/04.json`, blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96`, records **7/7 distinct image slots**, all Wikimedia Commons `Special:Redirect/file` requesting `width=1280`, with original exact URL and ALT text. Snapshot says post 257's then-current revision was modified 2026-10-29. **No fresh WordPress read** and **no real guest-browser HTTP, decode, screenshot or bytes** in this batch; do not treat frozen content as proof nothing changed.

On November 4, text retriever could not open seven exact Commons redirect URLs. That observation is **not origin HTTP status, visitor image failure, a 404 or 403**. The seven *Commons File catalog pages* were read independently and their reported originals used to compute purely **conditional** width-limited derivatives. None of these master sizes are actual browser transfer bytes. No source binary downloaded or mirrored.

## Seven source identities and proposed bounded sizes

| Slot | Catalog / NASA identification | Commons catalog master | Conditional <=960px rendition |
|---|---|---:|---:|
| 257:0 | [Apollo 12 Blitzeinschlag](https://commons.wikimedia.org/wiki/File:Apollo_12_Blitzeinschlag.jpg), NASA S69-60068; 16mm scan credit Ed Hengeveld | 7521 × 5207 | **960 × 665** |
| 257:1 | [Apollo 12 crew walk](https://commons.wikimedia.org/wiki/File:Apollo_12_crew_walk_to_transfer_van_(KSC-69PC-646).jpg), NASA KSC-69PC-646 | 3402 × 2477 | **960 × 699** |
| 257:2 | [Apollo 12 Saturn V launch](https://commons.wikimedia.org/wiki/File:Apollo_12_Saturn_V_launch.jpg), NASA S69-58564 | 1082 × 1418 | **960 × 1258** |
| 257:3 | [KSC-69P-0856 Firing Room](https://commons.wikimedia.org/wiki/File:KSC-69P-0856.jpg) | 2304 × 1536 | **960 × 640** |
| 257:4 | [Apollo command module main control panel](https://commons.wikimedia.org/wiki/File:Apollo_Command_Module_Main_Control_Panel.gif), technical source NASA Apollo Operations Handbook (GIF) | 3420 × 1640 | **960 × 460** |
| 257:5 | [Lunar module AS12-51-7507](https://commons.wikimedia.org/wiki/File:Lunar_module_AS12-51-7507.jpg), NASA image AS12-51-7507 | 4074 × 4095 | **960 × 965** |
| 257:6 | [Apollo 12 LRO landing site](https://commons.wikimedia.org/wiki/File:Apollo_12_LRO.jpg), NASA 2009 LRO | **800 × 800** | **800 × 800 — DO NOT UPSCALE** |

**Important:** source slot 257:6 *requests* a 1280-pixel rendition even though its Commons **catalog original is 800×800**. There is no evidence 1280px was actually delivered; the safe cached candidate must preserve the 800-pixel original or a smaller derivative.

All seven images lack explicit width and height in frozen HTML, which is a *potential* layout shift risk, **not measured CLS**. Slot 257:4 is a technical GIF; do not blindly convert to a photo format or crop away labels. Slot 257:0 is a scan/repackaging case with an additional author credit and therefore demands rights check beyond “NASA original.” The precise same-photo binary hash and whether a Jetpack proxy changes source URL/bytes are **unknown**.

## Primary evidence and permissions

NASA [Apollo 12 gallery](https://www.nasa.gov/gallery/apollo-12/), NASA [lightning account](https://science.nasa.gov/resource/lightning-strikes-twice/), NASA [Apollo 12/S3 LRO landing-site overview](https://science.nasa.gov/photojournal/first-look-apollo-12-and-surveyor-3/) and [Apollo 12 Flight Journal](https://history.nasa.gov/afj/ap12fj/01launch_to_earth_orbit.html) are archival subject references. They have **not** been verified byte-for-byte identical to Commons image files. NASA's [media use policy](https://gpm.nasa.gov/image-use-policy) does not excuse checking individual third-party credits, trademark/endorsement and depicted people in commercial use. Each item remains explicitly **copyright/usage HOLD**. The Commons catalog's NASA origin and public-domain designation are *indicators*, not preauthorization to download, host, crop or republish these particular works.

No local caching, file download, image conversion, WordPress upload or published-post rewriting took place.

## Release path: P2 after confirmed broken images

Site QA #154 preserves its P0 guest browser queue: **285:5 → 285:2 → 287:5 → 418:1/2 → 407:1**. This Apollo 12 batch is *P2* unless a real guest failure is discovered. For guest desktop and mobile Chromium, collect each rendered `currentSrc`, final CDP Image request status, all redirects, MIME, `complete` and `naturalWidth`, screenshot, cold request bytes, and LCP / synthetic-scroll CLS separately. Compare originals with rendered Jetpack sources and avoid declaring all seven broken based on text retriever refusal. If a confirmed defect is selected, verify exact photograph/crop, item rights and credit, prepare <=960px derivative without upscale, stage on nonproduction WordPress, visually test desktop/mobile, then request release approval. Back up original Gutenberg source and preserve rollback; **no bulk block rewrites**.

## Machine evidence and verification

- [Seven-slot machine-readable manifest](../qa/media-recovery/apollo12_257_catalog_20261104.json) pins every original URL/ALT and primary catalog candidate, with all browser statuses/decoded dimensions/wire bytes null and release flags false.
- [Fail-closed source-custody validator](../qa/media-recovery/validate_apollo12_257_20261104.cjs) cross-checks the actual frozen part 04 snapshot, catalog filenames, aspect ratio, rights and unknowns.
- [25-case Node regression suite](../qa/media-recovery/test_apollo12_257_20261104.cjs) includes 24 adversarial edits (fake HTTP, invented savings, changed photo, image upscale, unauthorized cache/upload, etc.). **25/25 cases from the exact committed blobs passed under isolated V8 Node-test compatibility replay**. Native Node CI and guest Chromium **not run**.

Site-wide prior baseline **61 posts / 355 image refs / 288 external refs / 13 oversized first-party originals**; all source counts only. The “42 broken” claim remains unverified in visitors, “76% savings” remains unmeasured on actual transfer, and **production repairs remain zero**.
