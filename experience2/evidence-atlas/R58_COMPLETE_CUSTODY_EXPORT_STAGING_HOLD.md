# R58 — Complete NASA source-custody text export (STAGING HOLD)

Parent R57: `6e6a97983606c43df39d1e6df67aebe4fa2e2ff0`. Issue #150. No homepage PR #49, PR #158, WordPress content/settings, themes, or paid services were changed.

## What changed

The prior exported `apollo-1-nasa-source-register.txt` contained six brief NASA catalog/date/URL citations. The downloadable research sheet now contains **each of the six complete visible SourceDrawer custody disclosures** as plain text, including catalog status, identity limitation, displayed NASA credit/producer, last-updated and editorial-check dates, reuse status and documentary boundary. The original six citations and NASA direct links remain. It is a source *metadata* export, not an image download or rights clearance.

The export button and explanatory copy explicitly state that the text sheet includes custody notes and pending image-rights status. The exporter does not fetch anything. It reads only the nine native `dt`/`dd` pairs in each already compiled source drawer, and refuses download if a field is absent, reordered or altered in a way that could misrepresent source identity, catalog status, missing human verification, reuse status or documentary limits. Example adversarial mutation: replacing the first rights field with 'Cleared for reuse' prevents export and presents an accessible status; original static records and citations stay available, including when JavaScript is disabled.

**Crucial:** this protects the optional export from accidental DOM drift, not a security boundary against arbitrary hostile scripts or a human verification of NASA images. The first catalog association S67-19766 remains provisional. All six individual image-rights assessments remain pending; no image, geo pin, inferred relationship, or third-party service is introduced.

## Executed local QA (source-built actual Atlas; isolated archive)

- `python -m unittest discover -s tests -p 'test_*.py' -q`: **94 tests, 92 passed, 2 skipped**. Original PR158 fixture-based tests skipped because the isolated ZIP lacks PR158 HTML/CSS; original R38 complete cohost also unavailable.
- `python test_atlas.py`: original 11 tests passed (prior verified in this sprint).
- `python tests/browser_r58_custody_export.py --output qa-r58`: **16/16** actual-source Chromium widths/modes (320, 360, 390, 428, 768, 1024, 1440, 1920; JS on/off), plus **8/8** rights-field tamper denials. Export inspected for all 6 citations, 54 metadata fields, NASA links, unconfirmed S67-19766, no rights clearance; no-JS disclosure works; print preserves the six records and drawers; no unexpected requests, JS page errors or horizontal overflow.
- Existing R54, R55, R56 Chromium suites: **48/48** completed; R57 also separately passed **16/16** earlier during this sprint. A subsequent combined regression invocation hit local command timeout before its last R57 invocation completed. This is not counted as a completed combined run.
- `node --check atlas.js`; `php -l final-vestige-ex2-evidence-atlas.php` and `php -l integration/fv-ex2-apollo-suite.php`: pass.
- Local fragment LCP observer 84–132ms; CLS=0 in 8 JS-enabled set-content cases. These are **not** hosted/Core Web Vitals values.
- 390px and 1440px screenshots captured twice byte-identically; SHA-256:
  - 390px `50aae8a4c28a8c257a70a2cbde2ad6570a74fc79533cbd578cb8975d1402a996`
  - 1440px `06b9e4a6ff47782bc72dfbe0ff53516179c9bfcd7e4539a112a42825f9bc75fe`
- Two independently built 84-file deterministic `STAGING_HOLD` ZIPs are byte-identical, SHA-256 `8a9436c1b7900cd93a750b4cb6a01230f55409085fb40dd50d965e10c28c5a32`. Builder: `tests/build_r58_bundle.py` with `--qa qa-r58`. The screenshots and receipt are downloadable from the run artifacts; not committed as binary blobs.

## Integrity and limitations

New `atlas.js` exact Git blob: `7bfc8d7fe216a7b786c6dc33ffd7841abcf92914`. Atlas PHP exact blob after version bump and export-copy update: `8f5a21b42cbd00acf0e390aaeb22e55f3bb216f8`. Regenerated static Atlas template SHA-256: `33c72ea1b64d5b3b93dd949da9143debea6bda1cc1143402a20e9e1abcaef82a`. The suite's reviewed-asset hashes were updated for these files; The Atlas template changed **only** in the export explanation/button copy and its expected digest was updated. Versions: `0.0.58-staging`. Regression pins updated; missing original PR158 HTML fixture now produces an explicit skip, not an uncontrolled test-suite error.

**Release HOLD:** Actual original R38 Desk + Atlas cohost, isolated WordPress/Assembler installation, verified axe-core and assistive-technology audit, hosted LCP/CLS/INP, independent QD, and successful CI on final head have not occurred. All six image-rights reviews remain pending. No production installation, publishing, CMS/settings writes, merges, speculative mapping or rights assertions.
