# Apollo R97 — Rights-safe source gallery (STAGING HOLD)

This isolated gallery is an engineering candidate attached to [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150). Its source-of-truth is the real R92 → R93 → R94/R96 staging chain, not an invented set of map markers or media assets.

## Purpose

R97 creates an editorially useful, photo-free gallery from six NASA photographic source records. **The archival photographs are intentionally withheld** because six individual reuse assessments remain pending. Visual placeholders must never be described as archival imagery. Each source card exposes title, catalog assertion, photo date, source URL, photographic limitation, and explicit reuse warning. SourceDrawer uses native HTML details; cross-component anchors take readers to Research Desk, chronology, Atlas and source passports. Two checked source records may be compared in a keyboard/touch-accessible text-only table; the interface explicitly disclaims any inferred causal, temporal or geographic relationship.

Without JavaScript, the six complete cards, NASA links and native source drawers remain visible. With JavaScript, optional compare controls activate only after the expected DOM is complete. A malformed DOM fails open. CSS covers 320–1920px layouts, reduced motion, forced colors, 44px controls, focus indication and print. The native PDF must retain the six NASA URLs and six reuse warnings.

## Source custody and build

The builder verifies the R94 release/rights/geospatial flags and rehashes all 24 inherited files, rejecting extra/missing/symlinked assets. It cross-checks each R93 source passport against its R85 NASA rights register entry. Crew portrait catalog S67-19766 and its exact day remain provisional. January 24, 2017 exhibits remain retrospective records with no invented order.

Run from the repository root:

~~~sh
python experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py /tmp/r92
python experience2/evidence-atlas/tools/build_source_passports_r93.py --src /tmp/r92 --out /tmp/r93
python experience2/evidence-atlas/tools/build_curated_atlas_r94.py --src /tmp/r93 --out /tmp/r94
python experience2/evidence-atlas/tools/build_source_gallery_r97.py --src /tmp/r94 --out /tmp/gallery --archive /tmp/gallery.zip
python -m unittest discover -s experience2/evidence-atlas/tests -p test_source_gallery_r97.py -v
~~~

The independent CI workflow twice builds the deterministic ZIP and runs **real HTTP Chromium/Playwright** across 320, 390, 768, 1440 and 1920px with JavaScript on/off, keyboard, touch, forced colors, reduced motion, measured laboratory LCP/CLS, axe-core 4.14.0 WCAG scans, screenshot SHA manifest and printable PDF validation. These are lab diagnostics, **not hosted WordPress.com Core Web Vitals**. Do not report success until the exact GitHub head checks complete.

## Release blockers / boundaries

- Six NASA photographic-use reviews remain pending. Linking is not a reuse license.
- S67-19766 identity remains provisional; no exact crew portrait day.
- Hosted WordPress.com / real Assembler compatibility, physical devices, NVDA/VoiceOver and independent editorial QA remain pending.
- Founder release approval remains pending. **No merge, deployment, WP settings/content/plugin installation, paid SaaS, or production writes.**
- Homepage PR #49, homepage development branches and original Research Desk PR #158 must remain unchanged.
