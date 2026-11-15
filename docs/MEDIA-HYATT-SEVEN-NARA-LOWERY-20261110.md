# Hyatt post 255 — archival media recovery, 2026-11-10

**Draft only.** No WordPress, public interface, image binary/download/cache, homepage, post block edits, merge or spend. Site QA PR #154 retains guest-browser measurement responsibility.

Seven exact frozen published source URLs and ALT texts matched Oct 30 fixture Git blob `9b16b828342a9ac338f3e65610fd3d8d508355e9` (part 05) and prior 208-source register blob `0ab518f0badc690d4ef9143b78d1628bbf63cfc7`. All seven Commons catalogs were readable. All seven literal `Special:Redirect/file` source URLs were **inaccessible to the web text retriever**, not real HTTP failure evidence. Native network DNS failed before HTTP. Actual origin/guest status/currentSrc/natural dimensions/transfer bytes are **unknown and null**.

Four NARA/NBS accessions: **70172329**, **70172360**, **70172364**, **70172359**; catalog originals **3019×2384**, conditional **960×758** each. Commons NIST federal public-domain assertions require per-item rights and source/crop review; named original photographer is unknown. NARA direct catalog links could not be independently retrieved. [1982 NIST investigation](https://www.nist.gov/publications/investigation-kansas-city-hyatt-regency-walkways-collapse-2) confirms context but not identical image binaries.

**255:1 is a 2007 diagram, not a 1981 photo**; Commons names tracer DTR and original drawer K. Ha and flags SVG source W3C-invalid. SVG nominal 720×420 may render as 960×560 vector, only after sanitization/legibility/copyright check. Low-resolution **255:2 = 477×330** and **255:5 = 463×342** are Lee Lowery Jr. photographs (Commons PD-author claim), and **must never be upscaled**. Image versions and license provenance require checking. **255:4 ALT overclaim:** original NARA caption only identifies a side view of a collapsed walkway; 'preserved for federal investigation' requires editorial evidence or removal. No published ALT changed.

### Rights-safe WordPress plan (not executed)
Only after real guest failures are confirmed, editorial approval and clear exact-image licensing: compare candidate visually to original and verify crop/rights; acquire legally, record provenance and SHA-256; output <=960px raster respecting source width (no upscaling) with accessible captions. For 255:1 vet/sanitize SVG and preferably supply safe static derivative if legibility holds. Stage unlisted WP media only with explicit approval; keep original URL/ALT/blocks and rollback mapping; verify mobile/desktop guest load with Site QA before replacement. Never substitute a different photograph as equivalent.

### 76% performance claim requires data
Historical **61 posts / 355 images / 288 external** stays separate from live newer 66/361 cohort. Fifteen WP originals above **1,500,000 B** total **47,096,779 stored B** (11 inline-used total 38,480,915 B), not visitor wire weight. Cold before/after browser bytes must match post, slot, actual photographic scene and network cold/cache flags, record transferred/decoded sizes and LCP/CLS, then compute `(before-after)/before*100`. **76% remains unmeasured; 42 purported broken remain browser-unconfirmed.**

### Site QA priority unchanged
`285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. This audit does not replicate Site QA's collector.

Source records: [audit](../qa/media-recovery/hyatt_255_seven_archives_rights_20261110.json) blob `26ee57ba734ca584bf2efed845fcae41b88b9514`, [215-slot ledger](../qa/media-recovery/coverage_215_exact_pr1703_20261110.json) blob `e406db4d913d328261cba889a69ca931f78175d9`; [validator](../qa/media-recovery/validate_hyatt_255_coverage_215_20261110.cjs) and [regressions](../qa/media-recovery/test_hyatt_255_coverage_215_20261110.cjs). Native Node and guest Chromium are **not yet run**.
