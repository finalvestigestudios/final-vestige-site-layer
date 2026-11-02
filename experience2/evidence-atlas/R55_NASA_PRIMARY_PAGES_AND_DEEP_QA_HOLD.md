# Apollo R55 — NASA primary-page audit and deep Chromium acceptance (STAGING HOLD)

Parent R54: 404684c8a22504dbb795cf433a180a7e4d182cd2. Scope strictly experience2/evidence-atlas/. The approved runtime Atlas/adapter remain byte-identical to R54. No WordPress, homepage, Research Desk, NASA image, or production changes.

## Source-verification result (reviewed November 1, 2026)

Six NASA image-detail pages were inspected for official displayed date, identifier, credit, producer and photographic context. Machine-readable records in sources/NASA_PAGE_RIGHTS_AUDIT_R55.json are tied to unchanged R37 crosswalk blob ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea.

- Record 01 — https://www.nasa.gov/image-detail/apollo-1-crew-honored/ — NASA credit, January 1967; **S67-19766 is NOT printed on this NASA page**. Its association remains provisional.
- Record 02 — https://www.nasa.gov/image-detail/amf-s67-15717/ — NASA page displays PIA S67-15717, Jan 3 1967, producer JSC.
- Record 03 — https://www.nasa.gov/image-detail/amf-s66-58038/ — PIA S66-58038, Oct 18 1966, producer JSC; the earlier crew rehearsal is not the fatal fire.
- Record 04 — https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ — PIA, Jan 24 2017, credit NASA/Kim Shiflett; later tribute exhibit, not original incident.
- Record 05 — https://www.nasa.gov/image-detail/amf-s67-21294/ — PIA S67-21294, Jan 28 1967, producer JSC; post-fire cabin image does not itself establish an ignition mechanism.
- Record 06 — https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ — PIA, Jan 24 2017, credit NASA/Kim Shiflett; redesigned-hatch memorial.

NASA's general guidance (https://www.nasa.gov/nasa-brand-center/) permits some informational uses under conditions, but does not waive third-party copyright, likeness/publicity, emblem or non-endorsement requirements. **All six individual photograph-use decisions remain PENDING.** The program has not personally checked links, downloaded binaries, placed imagery, introduced geo pins, or claimed licensing clearance.

## Exact-source R38 availability, with honest limitation

At R54, GitHub contains all five exact R38 Research Desk files: plugin 44a43c63, template 4842afb8, stylesheet 7b0972fc, script 57f4a639 and custody crosswalk ca00a51d. The original PR #158 template remains retrievable at blob 403d128c. All six R38 source URLs/identifiers appear in the original template. This is SOURCE-LEVEL custody verification, **not a successful R38 browser/WordPress co-installation**. A complete checkout and original-R38 runner are still required.

## Executed tests

- Python component suite: **92 run, 91 passed, one skipped** (complete original R38 files absent from the isolated R54 archive); six new NASA ledger tests pass.
- Original Atlas Python checks: **11/11 pass**. Deterministic Atlas WordPress staging build exits 0; PHP lint and Node syntax pass.
- New real-R37 Atlas Playwright/Chromium: **16/16 pass** at 320, 360, 390, 428, 768, 1024, 1440 and 1920 pixels, JS on/off, touch and reduced-motion emulation, native keyboard SourceDrawer, crosslink focus, source pairing, tamper fail-open, complete no-JS records, accessible ID references and zero unexpected outbound network requests.
- **Browser print visibility verified**: even with a filtered screen, all six photographic records and all six expanded source-custody descriptions are rendered visibly for print. No horizontal overflow.
- Deterministic screenshot SHA-256: 390px d68ce29a7a4843203da823726730f28d0aa2ba90f2efb40dcf36b376da4da3e4; 1440px b6b25d745872a8f647479a805bc14d818a6b8244402349b2c9123981497001ab.
- Local Playwright set_content fragment LCP 124–332ms, CLS 0. **Not** hosted or p75 Core Web Vitals. axe-core not run; no verified bundle.

## HARD HOLD

Real R38 + Atlas + adapter browser acceptance; genuine private Assembler/WordPress rendering (including pre-head nested-block assets); verified axe-core, Safari/screen-reader testing, hosted LCP/CLS/INP, independent QD, green CI, catalog identity #01 and six individual media/likeness rights reviews remain outstanding.

Never merge, publish, install plugins, update WordPress settings/content or edit homepage PR #49/lead branches or Research Desk PR #158 without express governed approvals. R55 supplies research evidence and tests only, not a release.
