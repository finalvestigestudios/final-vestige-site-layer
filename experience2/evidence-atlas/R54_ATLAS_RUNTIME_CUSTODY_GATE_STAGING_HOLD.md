# Apollo R54 — exact Atlas runtime source-custody gate (STAGING HOLD)

**Parent:** R53 draft PR #526, commit c3919b7aecc1d1e8c20f3481d09eb5b293618d2f. **Scope:** only experience2/evidence-atlas/. No WordPress writes, plugin activation, deployment, media embedding, source changes to Research Desk PR #158, or homepage PR #49 edits.

## Concrete runtime defect addressed

R53 required the *Research Desk* runtime to match a complete pinned PR #158 or R38 profile but accepted an Atlas shortcode without independently verifying the **Atlas plugin, CSS and JS** bytes. An altered Atlas script or stylesheet could therefore be served by the suite despite its reviewed template requirement.

R54 requires exactly reviewed Atlas Git blob hashes:
- Plugin PHP: cb3cbf0bfb2cd915fcc91f74627ca66edb90bd63
- CSS: aeac4a457ceb6d463113041afa4e037bb3681459
- JS: 23212093d354917e403a5a9dbd9dca6b0eb8ca28

It additionally requires the compiled template's SHA-256 to match 139f64b52b27977c4caf71685a03065b21b477ac3fbbbe3b6fafd14e635736f3, as defined by the already-pinned Atlas PHP plugin. The integrated shortcode and pre-head asset admission both fail closed when any runtime file is missing or altered; users retain the existing Apollo investigation fallback. This is an accidental-drift/source-custody gate, **not** a hostile-server integrity security boundary. Future Atlas updates need an explicitly reviewed new pin-set.

## Reproducible testing

Run from a complete repository checkout containing the exact R37 Research Desk crosswalk:

    python -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q
    python experience2/evidence-atlas/test_atlas.py
    python experience2/evidence-atlas/build_wordpress_stage.py --output /tmp/fv-r54-stage
    python experience2/evidence-atlas/tests/browser_r54_real_atlas.py --output /tmp/fv-r54-qa
    php -l experience2/evidence-atlas/integration/fv-ex2-apollo-suite.php
    node --check experience2/evidence-atlas/atlas.js

The new PHP probe and Python unit test execute an **exact reviewed** temporary plugin bundle, test positive admission, mutated plugin PHP/CSS/JS/template rejection, restoration after each mutation, missing-template rejection and recovery, and the existing fail-safe when Desk verification is absent. The tests never modify source-controlled files or WordPress.

The new R54 browser runner uses the **real, R37-source-built Atlas**, not a synthetic Research Desk. Chromium tests eight widths (320, 360, 390, 428, 768, 1024, 1440 and 1920px) with JS on/off, reduced motion, mobile touch, native SourceDrawer, keyboard focus, chronology jumps, filtering, six-record citation export, comparison, corrupted-source fail-open, print, console errors, network requests, horizontal overflow, and byte-stable mobile/desktop screenshots.

## Actual execution (November 1, 2026)

- Python discovery: **86 run, 85 passed, 1 skipped**; the pre-existing R52 original-R38 test was skipped because complete original R38 files were absent from the standalone archive.
- Standalone Atlas suite: **11/11 passed**.
- R54 PHP mutation probe: **14/14 true** on independently checked exact template and PHP/CSS/JS assets.
- WordPress stage package **generated successfully** from exact R37 custody blob ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea; six source records, zero embedded photographs, zero geographic pins.
- R54 **real-source Atlas Chromium: 16/16 passed** at 320–1920px with JavaScript off/on and print checks. No unexpected network requests, page errors or horizontal overflow in those controlled tests. Six-reference text export tested.
- Lab fragment LCP observed approximately **156–472ms, CLS zero**. Not hosted Core Web Vitals; these measurements are not p75 field data.
- Screenshots at 390 and 1440px repeated byte-identically in the same stable page state. See packaged QA receipt for SHA-256.
- PHP and JavaScript syntax checks passed.
- **Not executed:** original complete R38 Desk in Chromium, genuine isolated WordPress/Assembler nested Gutenberg first paint, independently verified axe-core, screen readers/Safari, Lighthouse/hosted metrics, completed CI, independent QD.

## Source and release boundaries

Six individual NASA photograph-rights assessments remain unresolved. The S67-19766 catalog-to-linked-photo attribution remains provisional and explicitly disclosed; no photograph is embedded. Photo chronology is not the fire sequence. No speculative geographic pins or connections.

**RELEASE: HOLD.** Do not merge, install, deploy, alter production WordPress, touch homepage PR #49 or Research Desk PR #158, or introduce paid services. Next: execute original R38 cohost runner in a full checkout and genuine private WordPress/Assembler staging; obtain axe/AT, independent QD/CI, photographic-source review and explicit founder approval.
