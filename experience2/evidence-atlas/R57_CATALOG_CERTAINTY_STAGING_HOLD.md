# Apollo Evidence Atlas R57 — NASA-page catalog certainty (STAGING HOLD)

Parent: R56 f503538d615e69836c14de30f8a385aaf60243fc. Issue #150. Isolated Evidence Atlas changes; no homepage branch, frozen PR #49, Research Desk PR #158, WordPress settings, or production changes.

## Implemented

The map-free, source-built Evidence Atlas now offers an optional catalog-provenance filter: **all six**, **five whose identifiers appear on the linked NASA pages**, or **one provisional catalog-to-photograph association (S67-19766)**. This describes source-page metadata, NOT photographic reuse permission. Existing year/search controls combine with this facet. Reset, accessible native source-index links, and deep links restore hidden records; print and the citation register always preserve all six. SourceDrawer disclosures are unchanged and readable without JavaScript. The runtime validates the expected six catalog-state values and fails open to all static evidence if modified. No image binaries, maps, geo edges, analytics or external services were introduced.

Version: 0.0.57-staging. Reviewed WordPress fragment SHA-256: 51de8c18f7b58be0a02d1a45cbcb2794dd822cc768d31fc6a05c6d4022e14de4. Atlas runtime Git blobs: PHP 7d91dcacc9d921c032923826dfefca731dac1d64; CSS 079f2ef9785184a098ec7686f5018a474181031b; JS 596746d3a7f2194d1b179fcb339df460daffb031. NASA R37 custody and R55 audit JSON remain unchanged.

## Executed local QA (November 1, 2026)

Standalone R56 archive with R57 code: 99 Python unit tests, 98 pass and one R38 skip; original Atlas tests 11/11. R57 actual-source Chromium 16/16 cases at 320, 360, 390, 428, 768, 1024, 1440 and 1920px with JS on/off, mobile touch and reduced motion. Verified provenance-facet intersections, reset, native navigation, full six-record print, native SourceDrawer access, no overflow and zero external requests. R56/R55/R54 regressions each passed 16/16. PHP and JS syntax checks passed. Local fragment LCP 92–124ms and CLS 0 are NOT hosted CWV. Screenshots SHA-256: 390px adc63d900bdc41cf089ce795b5fa8625d5e6556825f5a4b46a6834ada8f7d74b; 1440px 14104b8b518e1c66ec083e39be98f81adde73de28350c6749bb4d42894721cb2.

## Release blockers: HOLD

The isolated archive does not contain the original complete R38 Research Desk or all full-repository PR #158 test fixtures; GitHub's additional R49 fixture test needs the full checkout. Authentic WordPress/Assembler cohosting, verified axe-core, manual screen-reader review, independent QD, hosted performance and green exact-commit CI are pending. Zero of six NASA photographs have individual rights/likeness/use clearance; S67-19766 remains provisional. Do not publish, merge, install, or imply NASA endorsement.
