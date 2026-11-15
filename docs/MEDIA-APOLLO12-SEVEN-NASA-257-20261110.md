# Final Vestige Studios — Apollo 12 Seven-Image Source Integrity and Recovery Hold (2026-11-10)

**Scope:** Draft PR #1703 only, read-only media engineering. Site QA draft #154 owns actual logged-out visitor-browser image verification and the original P0 queue. Interim lead owns homepage visuals. **DO NOT MERGE OR DEPLOY.**

## Reconciled evidence and measurement
- Read source worklist `docs/IMAGE-WEIGHT-WORKLIST.md` from draft PR #183, reviewed Site QA draft #154 and the latest source register from draft #1703.
- Frozen 2026-10-30 census: **61 posts, 355 inline image positions, 288 external-origin positions** (separate from later 66-post/361-image census). This batch adds post **257**, *The Numbers Came Back* (Apollo 12), positions **257:0–257:6**. All 7 original published URLs and ALT fields match frozen `qa/media-recovery/parts/04.json` Git blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96`.
- All seven Commons **catalog HTML** records were accessible from independent search/retrieval. All seven literal `Special:Redirect/file?width=1280` source URLs were inaccessible through the **text retriever**, which is **not an actual image-origin 404/403, not a visitor HTTP result, and not proof of a broken image**. Independent native HEAD was attempted on the site and Commons but container DNS resolution failed before any HTTP connection. Image binaries, cryptographic identity, guest `currentSrc`, naturalWidth/naturalHeight, redirect chains and transferred bytes remain **unmeasured**.
- Reconciled full ledger: **208/288 uniquely researched**, **80 pending**, **213 total research-evidence records** (not 208 restorations or confirmed loads). Exactly seven previously pending slot records were enriched; every unrelated existing slot remained unchanged. **Reported 42 broken originals remain guest-browser unconfirmed. Proposed 76% *visitor image network transfer* reduction remains unmeasured.**

## Seven archival identities and conditional no-upscale max-width geometry
| Slot | NASA archival context / ID | Commons original px | CONDITIONAL maximum px |
|---|---|---:|---:|
| 257:0 | NASA S69-60068, Nov 14 1969, film image showing lightning **near** Pad 39A, digitization credited to Ed Hengeveld | 7521×5207 | 960×665 |
| 257:1 | NASA KSC-69PC-646 / 69-HC-1181, three astronauts walking to transfer vehicle | 3402×2477 | 960×699 |
| 257:2 | NASA S69-58564, Saturn V launch | 1082×1418 | 960×1258 |
| 257:3 | NASA KSC-69P-0856, Firing Room 2 at T+2:54 | 2304×1536 | 960×640 |
| 257:4 | NASA Apollo Operations Handbook Block II control panel technical drawing | 3420×1640 | 960×460 **subject to labels remaining readable** |
| 257:5 | NASA AS12-51-7507, `Intrepid` in lunar orbit on Nov 19 1969 | 4074×4095 | 960×965 |
| 257:6 | **2009** Lunar Reconnaissance Orbiter view, 800×800 original; official NASA PIA12903 appears related but **not proven pixel-identical** | 800×800 | **800×800, never upscale** |

These intrinsic dimensions are reported by the catalog, **not decoded image transfers**. The `?width=1280` query in the source URL is **not** evidence that 1280 pixels were actually delivered, or of any particular byte cost. The 800px original is a concrete avoid-upscaling risk. NASA's larger PIA12903 (1600px) is an **editorial candidate**, not an authorized identical-scene/image replacement for slot 257:6.

## Three editorial-integrity review items
1. **257:0:** The current ALT wording says the lightning channel was *reaching Launch Pad 39A*. Wikimedia's source description only says lightning struck **near** Pad 39A, seen in a film image. Suggested review-only wording: `Film frame showing lightning near Launch Pad 39A during Apollo 12's November 14, 1969 launch.` Do not introduce an unsupported physical-strike claim.
2. **257:4:** The diagram predates and explains Apollo Block II controls. Never present it as a contemporary photograph taken during the Apollo 12 lightning anomaly. A 960px target may make its switches and captions unreadable; this is an explicit accessibility exception until human testing.
3. **257:6:** The lunar-landing-site orbital view was taken in **2009** by the LRO, decades after the 1969 mission. When displayed alongside period launch photographs, the image's time and instrument should be explicit. The NASA PIA12903 scientific catalog credits **NASA/GSFC/Arizona State University** and describes the same general site, but the extant Commons crop is **not verified identical**.

## Copyright/rights and authoritative sources
NASA material is generally available for editorial information under its [official usage and branding conditions](https://www.nasa.gov/nasa-brand-center/), but individual photographs must be checked for third-party capture/scanning rights, astronauts' personality rights in commercial promotion, logo/emblem restrictions, attribution and false endorsement. **Wikimedia's PD-USGov-NASA template is not an item-by-item publishing authorization**. The 2009 LRO imaging credit includes ASU; photo 257:0 additionally credits a scanner. Do not apply the older NASA original's rights assertion automatically to any digitization, crop or third-party rendition.

Catalog anchors:
- [NASA Apollo 12 mission](https://www.nasa.gov/mission/apollo-12/) and [NASA Apollo 12 photo gallery](https://www.nasa.gov/gallery/apollo-12/)
- [NASA Apollo 12 first-look LRO PIA12903](https://science.nasa.gov/photojournal/first-look-apollo-12-and-surveyor-3/), **different/original-rendering identity unresolved**.
- Exact seven Commons file catalog URLs and their NASA ID provenance are preserved in the adjacent [seven-row audit](../qa/media-recovery/apollo12_257_seven_nasa_20261110.json).

## Safe restoration and image-weight protocol (proposed, not run)
1. **P0 first:** Leave actual guest-image adjudication to Site QA #154, in priority order **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. No duplicate browser collector. Require final `currentSrc`, response status and redirect chain, explicit cold-cache flags, positive natural width/height for decoded success, screenshot of failed scene, and the uncached `encodedDataLength`.
2. **Only after an actual failure is established:** Seek same original photograph from archival primary catalog, verify asset binary/visual crop identity, copyright and credits; classify a different-photo alternative separately and require editorial approval. Preserve original Gutenberg block and ALT text for rollback.
3. **No unlicensed scraping/mirroring**. Before a proposed WordPress upload, verify copyright and credit; obtain specific permission, generate a derivative no wider than 960px without upscaling (unless critical diagram/map legibility needs an explicitly authorized exception), inspect real image text and visual quality.
4. Stage an isolated **single-image, reversible** change only after explicit WordPress write authorization; no blanket Gutenberg source replacements. Re-test desktop/mobile rendering, alt/date/caption integrity and reversible rollback.
5. For claims of **76% image transfer savings**, measure identical *image-slot/source*, device/viewport and responsive sizes before/after using **actual uncached visitor wire bytes**. Do not substitute stored WordPress originals, 1280-px URL query, compression estimates or different-content replacements. Record both network payload and visible correctness. Never claim reduction until comparable samples complete.

**Oversized originals:** Existing live media inventory identifies **15 WordPress original attachments >1,500,000 decimal bytes**, totaling **47,096,779 stored-original bytes**; **11** appear inline across eight published posts, but even their **38,480,915 original bytes** do *not* establish guest-browser transfer or savings. Site QA P0 confirmed failures remain higher priority than this P1 optimization.

## Engineering verification and release boundaries
- `qa/media-recovery/validate_apollo12_257_exact_coverage_208_20261110.cjs` and its 22 Node-compatible adversarial tests verify exact immutable source URLs, independent catalog evidence, null genuine HTTP/byte outcomes, 960px/no-upscale and human diagram-label gate, 2009 orbital-image chronology, all rights/WordPress holds and 288-slot invariance.
- **22/22 regression checks PASS** in isolated V8 with Node-compatible test mocks against the exact GitHub-committed file contents; **native Node CI and logged-out Chromium have NOT run**. The archive entry and full register were independently fetched from GitHub by blob SHA.
- **0 production images replaced; 0 cache/mirror/download operations; 0 WordPress uploads/edits; 0 homepage design changes; 0 merges; $0 spend.**
