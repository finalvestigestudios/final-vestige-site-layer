# Apollo 1 NASA five-image provenance and visual-integrity gate — 2026-11-06

**Draft QA-only, non-production.** Authenticated WordPress post 434 (modified 2026-11-03T22:12:30) has six inline images: one first-party WebP and five NASA external JPEGs. Unlike earlier Navy/USGS/Florida batches, this covers NASA's five-image host in the sitewide 66-post inventory. Does not modify Site QA #154 collector or homepage design.

| Image slot | Official NASA catalog | Published catalog pixels | Conditional ≤960-wide geometry |
|---|---|---|---|
| 434:1 | [S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/) | 1514×1920 | 960×1217 |
| 434:2 | [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/) | 1920×1546 | 960×773 |
| 434:3 | [KSC-20170124-PH_KLS01_0164](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/) | 1920×1280 | 960×640 |
| 434:4 | [S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/) | 1920×1297 | 960×649 |
| 434:5 | [KSC-20170124-PH_KLS01_0090](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/) | 1280×1920 | 960×1440 |

**Major new P1 finding:** the 2017 NASA photograph `KSC-20170124-PH_KLS01_0164` used as **434:3** is visibly a **large white Apollo spacecraft mockup in a gallery**. The current WordPress ALT/caption says the photo is of the *original three-part Block I hatch*. NASA's description mentions that the tribute includes the hatch, but it does not establish the mockup image as a photograph of the hatch itself. Publisher image was inspected through the image viewer on Nov 6 PT. Different image **434:5** (`KSC-20170124-PH_KLS01_0090`) shows a hatch exhibit and is cataloged by NASA as the redesigned hatch. Preserve this crucial distinction; editorial review should either correct 434:3's ALT/caption to describe the mockup or obtain an individually identified actual Block I hatch photo. **No automatic rewrite.**

Five NASA catalog pages were individually opened. All five show pixel dimensions matching WordPress's stored HTML dimensions, but **this proves neither that the present photo binary has the same crop nor that visitors download those bytes**. Two publisher image previews rendered in a web image viewer; no logged-out browser HTTP, `naturalWidth`, actual cold `encodedDataLength`, or original binary hash was captured. The reported 42 broken and 76% transfer savings remain unverified/unmeasured. The 13 >1.5MiB WordPress originals total 43,522,829 original stored bytes only.

NASA [official media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally permit informational reuse, with NASA credit, no endorsement, and exceptions for third-party content, publicity and NASA identifiers; credit NASA/Kim Shiflett for the two 2017 images. Rights to commercial use or derivative caching are not granted by this audit. Item-level rehost review, binary/crop verification, attribution and editorial approval remain HOLD.

**Controlled staging plan (not performed):** Guest Chrome verify each `currentSrc`, response, MIME, decode, cold bytes, dimensions and responsive view via existing Site QA. Review license for exact binaries, preserve hashes and attribution. Only then create no-upscale ≤960px candidate JPEG/WebP with quality review and correct portrait sizing (434:5 960×1440); compare 2x density, legibility and desktop/mobile screenshots; retain original URL in rollback ledger, stage in WordPress media staging, seek separate approval for targeted caption/photo repair. Zero site writes, image downloads, caches, binary derivatives, repairs or spending in this work.

**Run offline checks:** `node qa/media-recovery/validate_apollo1_nasa_five_20261106.cjs qa/media-recovery/apollo1_nasa_five_20261106.json`; `node --test qa/media-recovery/test_apollo1_nasa_five_20261106.cjs`. Guest Chrome and native CI pending.
