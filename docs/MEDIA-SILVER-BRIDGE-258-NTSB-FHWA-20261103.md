# Silver Bridge (post 258): NTSB host recovery and FHWA/Commons visual integrity — 2026-11-03

**Scope:** Independent media recovery PR #183 only; Site QA PR #154 retains logged-out browser validation. Authenticated *read-only* WordPress confirms post 258 published and modified `2026-11-02T21:39:47`, with six exact source image URLs unchanged from pinned `parts/04.json` Git blob `6df3251e5a67a971d87a516a1ba4a0cc32f51f96d`.

## Six exact image slots

| Slot | Published source observation (independent renderer only) | Authoritative candidate | Rights / dimensions |
|---|---|---|---|
| 258:0 | Commons Special:Redirect inaccessible; no HTTP status | [FHWA Commons file](https://commons.wikimedia.org/wiki/File:Silver_Bridge,_1928.jpg) | FHWA-public-domain claim; **286×154 only; never upscale** |
| **258:1** | **Old www-d.ntsb.gov exact JPG inaccessible; no numeric HTTP status** | [NTSB investigation 80267](https://www-s.ntsb.gov/investigations/Pages/80267.aspx) links **working same-name plate** `https://www-s.ntsb.gov/investigations/PublishingImages/80267-img.jpg` | Verify embedded rights, intrinsic size and actual crop. **Best prospective fix** |
| 258:2 | Old FHWA exact JPG displayed | [FHWA historical archive](https://www.fhwa.dot.gov/highwayhistory/national_bridge_inspection_standards.cfm) | Original file appeared working. No change without guest failure |
| 258:3 | Old FHWA exact JPG displayed | [New FHWA article](https://highways.fhwa.dot.gov/highway-history/general-highway-history/happy-50th-anniversary-national-bridge-inspection-standards) supplies working modern-route same-scene rendering | Binary/crop unverified; dimensions unknown |
| 258:4 | Old FHWA exact JPG displayed | Same FHWA official modern article supplies working five-engineer group rendering | Binary/crop unverified; dimensions unknown |
| 258:5 | Commons Special:Redirect inaccessible; no HTTP status | [DPLA/Columbus Metropolitan Library Commons catalog](https://commons.wikimedia.org/wiki/File:Silver_Bridge_-_DPLA_-_9fc0bcf07698072f128124fc79edd1c7_(page_2).jpg) | Original **3296×2080**, conditional ≤**960×606**. **'No Known Copyright' is NOT a public-domain grant** |

**Results:** three exact old FHWA sources displayed; three exact URLs inaccessible to the independent retriever; three authoritative replacement images (NTSB and two FHWA) independently displayed. These are *not origin HTTP 200/403/404 results* and cannot confirm visitor-facing failures. The official [NTSB investigation](https://www-s.ntsb.gov/investigations/Pages/80267.aspx) and [FHWA source](https://highways.fhwa.dot.gov/highway-history/general-highway-history/happy-50th-anniversary-national-bridge-inspection-standards) both establish the historic death toll at 46; the DPLA catalog includes a contradictory inflated count that **must not be propagated into Final Vestige captions**.

## Safe restoration path (NOT authorized for publication)

1. Send Site QA #154 the 258:1 exact old/new URL pair as P1, preserving P0 queue: 285:5, 287:5, 418:1–2, 407:1.
2. Obtain logged-out Chrome/mobile `currentSrc`, Image GET/MIME/redirect/status, decode/naturalWidth, screenshots. If the old diagram truly fails, confirm new NTSB rendition visually and rights review individually.
3. Only after approval, generate ≤960px non-upscaled derivative from lawful source, maintain original layout/ALT/caption and aspect ratio. The 286px Commons thumbnail must stay 286px. For NTSB/FHWA 258:1–4 intrinsic pixel dimensions remain **unknown**: do not invent target heights.
4. Prefer a rights-cleared WordPress Media Library attachment and responsive `srcset`, staged article block diff + two screenshots and rollback record. Do **not** rewrite post blocks, rehost external photos, or make WordPress production writes now.
5. Use paired, cold-cache, complete CDP image-only wire samples before claiming weight reductions. 61 posts / 355 references / 288 offsite origins / 13 >1.5MiB originals is the archive baseline; **42 reported broken not verified**, **76% reduction unmeasured**, **0 production fixes**.

Audit: [machine-readable six-slot source/candidate ledger](../qa/media-recovery/silver_bridge_258_ntsb_fhwa_20261103.json). Gate: [fail-closed validator](../qa/media-recovery/validate_silver_bridge_258_20261103.cjs), [26-case tests](../qa/media-recovery/test_silver_bridge_258_20261103.cjs), V8 CommonJS execution `Silver Bridge image evidence: 26/26 PASS`. Native Node CI and guest browser not executed. No binaries copied, licenses presumed, home design changed or subscriptions purchased.
