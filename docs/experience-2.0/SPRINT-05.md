# Experience 2.0 - Sprint 05: Recovery, production-oriented design system, hardened flagship

**Status:** integration candidate on an isolated branch. Nothing here is installed, merged, approved or deployed. PR #49 was read (status only) and not touched.
**Date:** 2026-10-30 to 2026-11-01. **Branch:** `feature/experience-2-living-archive-sprint5`, cut from `origin/main` (not from PR #49's branch).

## Release ladder (what each artifact is)

| Level | Meaning | What is at this level today |
|---|---|---|
| 1. Design prototype | Local study. No integration contract. | `experience-2.0/prototypes/` (the supplied Sprint 1-4 sources, kept verbatim); the three art directions in `concept-board.html` |
| 2. Integration candidate | Source-controlled, tested, staging-only. | Design system, Apollo 1 companion experience (standalone page), Research Desk and Atlas (shortcodes), Atlas data model and tools |
| 3. Approved production release | Passes the seven gates in the directive. | Nothing. Founder art-direction approval, independent source and accessibility review, independent QD on the exact SHA, green hosted CI, deterministic artifact verification, deployment authorization and rollback proof are all outstanding. |

No `FVSL-QD-PASS` marker was issued.

## A. Recovery report

**Recovered and verified.** Both ZIPs matched the stated SHA-256 (`d41fdeaa...e4ff` foundation v4, `8c7afa33...5ac05` staging candidate). The foundation ZIP's `verify_all_v4.py` reproduces 6 of 6 only after two environment fixes:

- Its verifiers hard-code `executable_path='/usr/bin/chromium'`, which fails on any other machine. Run unmodified here: `BrowserType.launch: executable doesn't exist at \usr\bin\chromium`. With the launch pointed at Edge, `verify_concept_board`, `verify_flagship`, `verify_atlas_preview`, `build_ledger` and `verify_ledger` all pass.
- `php -l` needs PHP, which was not installed. I installed PHP 8.3.36 (official windows.php.net build, SHA-256 checked against the published release list) and the plugin lints clean.
- `verify_ledger.py` imports a sibling module, so it fails under `python -I`; it passes without `-I`.

**Genuine defects found in the supplied prototype** (verified by reading the NASA records and looking at the images, not assumed):

1. **Wrong caption on the hatch image.** Record 4 used KSC-20170124-PH_KLS01_0164 and called it the "original three-part Block I hatch". NASA's description and the photograph show a spacecraft **mockup**. Replaced with KSC-20170124-PH_KLS01_0129, which NASA describes as the three-part hatch that was on the Apollo 1 spacecraft.
2. **Images that looked like evidence of the event but are not.** The "Fourteen seconds" chapter used a 1966 training photograph, and two chapters used 2017 museum photographs. Every plate now states its role ("Context photograph", "Museum exhibit, 2017", "Post-fire photograph"), its date, and whether it depicts the event.
3. **Shortcode ids repeat.** The staging plugin always emitted the same ids, so two desks on one page would duplicate them (by code inspection; the builder already supported an instance id but the plugin never used it).
4. **Assets enqueued only from direct post content**, which misses template parts and widgets (by code inspection).
5. **Cache-busting by a constant** rather than content, and **no integrity check** of the bundled template.
6. **A `h1` inside an embedded component**, and 11 px labels.
7. Public copy said "the prototype deliberately keeps this uncertainty visible".

**Still unverified:** see section E, "Not verified".

## B. Implementation report

New source is under `experience-2.0/` (all editable, no generated media):

| Area | Files |
|---|---|
| Canonical data | `data/apollo1.json` (six records, images with identity and rights fields, claim crosswalk, chronology) |
| Design system | `design-system/src/css/00-16*.css`, `design-system/src/js/fv-ex2.js`; tokens `--fvx-*`; selectors `.fv-ex2*`; hooks `data-fvx-*` |
| Components | cinematic hero, evidence plate, provenance list, investigation chapter, chapter bar, interactive chronology, source drawer, Research Desk record, Atlas result card, section transition, buttons/chips/field/callout, gallery page |
| Builders | `tools/build_all.py`, `render_flagship.py`, `render_desk.py`, `render_atlas.py`, `render_gallery.py`, `fvx_lib.py` |
| Plugin | `wp-plugin/final-vestige-experience-2/` (shortcodes `[fv_ex2_research_desk]`, `[fv_ex2_atlas]`) |
| Atlas | `atlas/schema/atlas.schema.json`, `atlas/data/{curation,wp_snapshot,atlas}.json`, `atlas/tools/{ingest_wp,build_dataset,validate_atlas}.py` |
| Verification | `tests/`, `tools/{run_all,verify_media,verify_hero_contrast,measure_perf,capture_evidence,fetch_axe}.py` |

Design decisions worth knowing:

- **No JavaScript decides which evidence is on screen.** Each plate is sticky inside its own chapter with CSS alone. This removes the whole class of bug behind the Sprint 4 fix (a stale sticky viewer showing exhibit 01 beside later chapters).
- **Enhancements only reveal controls after wiring succeeds.** Source buttons and the chronology slider are `hidden` in the HTML. Modules are independent; a thrown error in one leaves the others working (tested).
- **Scroll-linked reveals move text, never fade it.** An opacity ramp failed axe color-contrast mid-animation, so it was removed.
- **The chronology never interpolates.** Four documented markers on a proportional axis, dashed between them, with a slider that reports "Nothing is recorded between markers".
- **Atlas:** places are `unverified_reference` with null geometry. `map_eligible()` is the only gate to a pin and requires verified coordinate, stated precision, geography sources and an approved review. Today 0 of 6 places qualify, so nothing is plotted. Relationships are `documented` (cited) or `interpretive` (labelled). Forbidden: causal and adjacency predicates, and co-occurrence of place or date as a justification.
- **Atlas themes are now the real WordPress categories** (Catastrophe, Conflict, Discovery, Ingenuity, Lost, Survival) read from the live site, replacing the prototype's invented labels.

Bundle size: CSS 22,979 B (4,798 gzipped), JS 9,264 B (3,130 gzipped). No webfont, no third-party code, no network calls.

## C. Visual evidence

24 real-browser captures (Edge) at 360, 390, 768, 1024, 1440 and 1920 px for the flagship, Research Desk, Atlas and design-system gallery, with **all real NASA images loaded** (flagship 7/7 images per width, no horizontal overflow). Screenshots are generated into `experience-2.0/dist/evidence/` by `python experience-2.0/tools/capture_evidence.py` and are deliberately not committed.

Fixed because of what the captures and measurements showed: primary-button label invisible (gold on gold, specificity), plate label shifting as images arrived (CLS 0.226), hero eyebrow text at 3.6 to 3.7:1 over the bright part of the photograph.

## D. WordPress integration status

See `ARCHITECTURE-DECISION.md`. Summary: a separate Experience 2.0 plugin, not part of Site Layer. The plugin (`0.5.0-sprint5`) stores nothing, registers no admin screens or REST routes, and makes no remote requests. Hardening versus the candidate: attributes ignored; per-instance ids; assets registered early and enqueued on render or when post content contains a shortcode; content-hash asset versions; template verified against the build manifest before output (tampered, missing or empty template falls back to a plain link to the article and loads no assets); `defer` script strategy; headings drop to h2 inside posts.

**Blockers (environment):** no WordPress.com Atomic staging was used or authorized in this session. Not tested: Assembler theme, Jetpack, page caching, block-theme template parts (the shortcode renders there, but styles enqueue in the footer rather than the head). A dynamic block wrapper for the editor is not built.

## E. Test results

Command: `python experience-2.0/tools/run_all.py --perf` (exit 0).

| Stage | Result |
|---|---|
| Build deterministic; plugin payload matches a fresh build | PASS |
| Atlas dataset matches a fresh assembly; validates (0 map-eligible places) | PASS |
| Builders, data validation, CSS/JS static analysis | PASS, 19 tests |
| Atlas model, invariants, ingestion | PASS, 22 tests |
| WordPress plugin (real PHP 8.3, WordPress stubs) | PASS, 11 tests |
| Browser: responsive x6 widths + 320 px, behaviour, fail-open, axe-core | PASS, 31 tests |
| Live media and NASA record verification (33 URLs) | PASS |
| Hero text contrast over the real photograph (50 regions) | PASS, tightest margin 5.68:1 |
| Lab performance, desktop profile | PASS |

**Accessibility (axe-core 4.10.2, WCAG 2.0/2.1/2.2 A and AA plus best-practice):** 0 violations on the flagship, Research Desk, Atlas and gallery at 1440 and 390 px, with the drawer open, and with scroll motion enabled. axe reported `color-contrast` as *incomplete* for 13 flagship nodes (text over the hero photograph, which it cannot sample); those were measured separately by `verify_hero_contrast.py`, which found and fixed a real failure. Also tested: skip link, landmarks, heading outline, visible focus, 44 px touch targets, drawer focus return and keyboard, reduced motion, 320 px reflow, no-JS, missing and throwing `IntersectionObserver`, no scroll lock outside the dialog.

**Lab performance (not field data; real NASA images; Edge):**

| Page | Profile | LCP | CLS | Slowest event |
|---|---|---|---|---|
| Flagship | desktop | 336 ms | 0 | 24 ms |
| Flagship | mobile (390 px, 4x CPU, ~Slow 4G) | 1,020 ms | 0 | 72 ms |
| Research Desk | desktop / mobile | 84 / 804 ms | 0 | 0 |
| Atlas | desktop / mobile | 68 / 716 ms | 0 | 0 |

**Regression tests have teeth.** The plate-reservation test was run against the original CSS and fails (frame collapsed to 1.09 of its 1.27 ratio); against the fix it passes. A first attempt at that test did not discriminate and was discarded.

**Not verified (cannot be inferred from the above):** Safari and Firefox; real screen readers (NVDA, JAWS, VoiceOver) and iOS touch; field Core Web Vitals (INP especially: the event timings above are a lab proxy); WordPress.com Atomic staging, Assembler theme, Jetpack and caching; hosted CI (a workflow is included; its first run is the evidence); the independent source review and QD review; per-image rights confirmation by a human; 200 to 400% browser zoom beyond 320 px reflow; high-contrast mode.

Tooling notes: PHP 8.3 and axe-core 4.10.2 (SHA-256 pinned, matched to the cdnjs SRI) were installed as test-only tools. Firecrawl credits ran out during the NASA review, so the NASA pages and APIs were read directly.

## F. GitHub state

See the commit list and Issue #150 comment. PR #49 at last read: open, head `bb59f1a`, `verify` check failing, `deploy` skipped. Untouched.

## G. Next sprint (prioritized)

1. **Hosted CI and review.** Confirm the new workflow is green on the pushed SHA; request independent QD of that exact SHA.
2. **WordPress staging.** Install the plugin on a staging site (Assembler theme, real plugin stack). Check shortcode rendering in a page and a template part, header vs footer style enqueue, Jetpack Dispatch, page cache. Build the dynamic block wrapper (`final-vestige/research-desk`) with an editor placeholder.
3. **Flagship as a WordPress page.** Add a fragment mode (theme owns header, footer, `main`, `h1`) and a third template; decide the URL. Keep the published article canonical.
4. **Human editorial review** of the items marked in `MEDIA-AND-SOURCE-REVIEW.md`: S67-19766 identity; the sentence on the inward-opening hatch; the "most probable arc" wording; the "fourteen seconds" title versus the Board's "approximately 15 seconds"; two claims that are article-only.
5. **Assistive technology pass:** NVDA + Firefox, VoiceOver + Safari (macOS and iOS), TalkBack. Add Playwright Firefox and WebKit to CI.
6. **Atlas geography queue.** For each of the 6 places find an authoritative coordinate source and stated precision, get it reviewed, approve, then render the first pins. Decide SVG vs MapLibre only after that. Add `ingest_wp.py --check` to a scheduled workflow.
7. **Founder decisions:** select the art direction (Black Dossier is provisional); self-hosted Fraunces (OFL) versus the Georgia-class fallback; URL and naming of the companion experience.
