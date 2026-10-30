# Experience 2.0 — Apollo 1 evidence walk and verified-post Atlas

**R&D STAGING ONLY — NO WP INSTALL, NO PRODUCTION RELEASE.** This independent, source-controlled candidate builds on the unmerged [Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), but neither edits that branch nor touches frozen homepage PR #49. Charter: [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150).

## What is actually implemented

- **Six-stage Apollo 1 documentary:** evidence plate + source drawer + simple anchor-based chronology rail. Every stage has a specific Board-supported finding, a clear evidentiary limitation, a corrected NASA image-record title/description/date/credit, and a link to the Board. No false continuous replay or speculative ignition instant.
- **Research Desk / source-custody section:** makes the distinction between Board evidence and contextual photograph explicit, warns about unreviewed media rights and no NASA endorsement.
- **Curated Atlas:** six published WordPress posts were independently read by post ID on Oct. 30, 2026; no invented coordinates (`geometry: null` in every item), no misleading relationship edges or map animation. Search and theme filter work when JS exists, all cards stay visible when it does not.
- **Accessible, progressive enhancement:** native `<details>` source drawers, focusable navigation anchors, keyboard-operable search/filter, `aria-live` results, reduced-motion styles, static-first DOM with no modal/focus trap and no dependencies. IntersectionObserver adds only active-rail location hints; missing/throwing API leaves all evidence visible.
- **Image gallery strategy:** typographic record plates and linked NASA image records. **No NASA photographs have been downloaded or embedded.** This is a deliberate safety and performance gate until exact image files, third-party/image subject restrictions, responsive image sizing, and media distribution are reviewed. The current visual preview is an **archive index/gallery of six verified NASA records**, not a cleared photograph gallery.

## Critical source-custody correction

Older prototype labels paired historical claims with photos that **do not portray the specific claimed measurement/event**. Their photo pages were checked on the NASA site October 30, 2026:

| NASA image record | What the published NASA image metadata says | What it cannot prove |
| --- | --- | --- |
| [Apollo 1 crew honored](https://www.nasa.gov/image-detail/apollo-1-crew-honored/) | January 1967 crew training portrait near Launch Complex 34 | Ground-test pressure or capsule fire safety; image contains identifiable people |
| [S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/) | Jan. 3, 1967 movement of spacecraft 012 for adapter mating | Oxygen concentration or any live pressure sensor trace |
| [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/) | Oct. 18, 1966 altitude-chamber astronaut training | Fire telemetry, ignition or Jan. 27 fire timeline; image contains identifiable people |
| [KSC-20170124-PH_KLS01_0164](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/) | Jan. 24, 2017 Apollo 1 tribute mockup and hatch displays | 1967 rupture or hatch opening moment |
| [S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/) | Jan. 28, 1967 heat-damaged command-module interior | A definitive photographed ignition arc |
| [KSC-20170124-PH_KLS01_0090](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/) | Jan. 24, 2017 redesigned hatch at memorial exhibition | Direct 1967 accident imagery; it illustrates the later design response |

All **historical conclusions** in the six plates are linked to NASA's [1967 Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), not claimed as facts depicted in these photographs. Example: first report 23:31:04.7 GMT, rupture about 23:31:19 GMT, at least 29 psia; electrical arc most probable, no single ignition source conclusively identified. **Observed records and Board reconstructions are distinguished; these are not direct firsthand measurements by Final Vestige.**

### Rights / media gate

[NASA Brand Center and media policy](https://www.nasa.gov/nasa-brand-center/) reviewed. NASA generally has no objection to informational uses of released material subject to exclusions; no NASA logo or endorsement, properly credit NASA, check third-party credits and recognizable people's publicity rights, and do not assume the NASA distribution grants commercial advertising rights to third-party likenesses. All six image links are **source-page-only** for now; no claim of full asset-level usage clearance, despite verified pages/credits. Source-policy review is not legal counsel.

## Build and tests

Python stdlib only: `python render.py` produces `index.html` byte-for-byte from `records.json`, `assets/app.css` and `assets/app.js`. Repeating the command should not change output/hash. HTML uses inline CSS and JS **only to make a self-contained offline preview**; a WordPress staging adapter and external optimized assets are separate future tasks.

Run `python qa/verify_browser.py` with Python Playwright and locally installed Chromium at `/usr/bin/chromium`; the script uses `page.set_content()` because browser network/navigation is blocked in this sandbox. It still executes in **real Chromium**. It records seven full-page screenshots, SHA-256 hashes, 320–1920 viewport overflow checks, filter/search/reset/empty state, keyboard source drawer, no-JS, missing/throwing observer, 200% zoom, reduced motion, and synthetic PerformanceObserver metrics in `qa/QA_RESULTS.json`. The test intentionally does not need NASA network image requests.

October 30 local test: **PASS at 320, 360, 390, 768, 1024, 1440, 1920**, six stages and six Atlas cards on every viewport, no overflow, 7 reproducible screenshots, no external assets, 5 fail-open/accessibility checks, six functional interaction assertions. Synthetic local-browser LCP **172 ms** and CLS **0** at 1440 (in-memory HTML, no photos); **not field Core Web Vitals, not WordPress staging results**. Playwright Python environment does not have axe-core, so **automated axe is unrun**; don't present this as WCAG certification.

Screenshot artifacts from this isolated run are stored under local `qa/screenshots/` and their hashes in `qa/QA_RESULTS.json`. Git stores the deterministic renderer and QA runner, not full-size PNG binaries. The founder's conversation can receive the PNG ZIP separately.

## Remaining release gates

1. Founder approval of Black Dossier visual direction, photography policy and content scope; this prototype is not authorized for production.
2. WordPress Assembler/Jetpack staging adapter, shortcode lifecycle including nested/dynamic block, CSP and caching checks; no WP edits made here.
3. Individual image download, byte-level review and responsive media strategy/rights clearance, especially identifiable persons; do not infer this from NASA metadata alone.
4. Automated axe-core audits in a network-enabled/packaged CI environment, manual screen-reader (NVDA/VoiceOver) and Safari/iOS touch checks, actual touch target measurements.
5. Actual staging/field p75 LCP, CLS and INP with full production CSS/theme/fonts/pictures, not synthetic preview metrics.
6. Independent QD and green hosted CI on exact head, then separate founder-approved deployment. Hosted GitHub Actions currently reports a runner-dispatch problem; do not use it as a pretext to bypass release controls.
