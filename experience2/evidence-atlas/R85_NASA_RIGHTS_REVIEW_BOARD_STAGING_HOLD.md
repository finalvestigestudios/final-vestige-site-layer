# R85 — NASA photographic source / rights review board (STAGING HOLD)

**Scope:** Independent, non-deployed Apollo 1 Research Desk / Evidence Atlas review tooling. R85 adds a source-verified **static review workbench**, not a new site page, an image gallery with reproduced photographs, or a permission decision. No homepage change, WordPress content/plugin/settings write, merge, deploy or paid service.

## Editorial and rights problem addressed
The six NASA-linked records are now visible and testable across Apollo components, but zero of six original photographs has a documented image-specific reuse decision. NASA states that its material is generally available for certain informational uses **subject to conditions**: no implied endorsement or brand/logo misuse, third-party ownership considerations, and recognizable-person/publicity issues. A source citation or NASA credit does not independently resolve these questions. See https://www.nasa.gov/nasa-brand-center/ and https://gpm.nasa.gov/image-use-policy . We have not assessed or reproduced image binaries.

R85 makes the gap explicit in a polished, keyboard-usable, print-capable **no-JS review board** whose six evidence cards present: source identity, date certainty, NASA destination, source-page credit, documentary scope, limitation, catalog status, and four decisions a human reviewer must still evaluate. Every card provides a primary NASA source link, not a downloaded or embedded image.

The first crew portrait's proposed **S67-19766** association remains provisional and its day in January 1967 is unknown. Both January 24, 2017 images share a calendar date without asserting a time sequence. This board is organized by evidence number, **not a reconstruction of the January 27 fire or an ordered photo chronology**. Zero geo coordinates, map relationship edges, photo binaries or implied permissions were introduced.

## Hard custody gate
The builder independently loads three existing source-controlled JSON inputs:
- R37 photo crosswalk, Git blob SHA-1 `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`.
- R79 six-source NASA-page audit, Git blob SHA-1 `a3f9d8fe7a237e7b3b8aecb0bcc8aaec055e96d6`.
- R55 image-rights page audit, Git blob SHA-1 `12f7019678a1e6afb7a813a51524bca29a5b522b`.

The builder refuses any changed source bytes, altered URL, fabricated date/PIA, missing record, cleared-rights claim, page-audit inconsistency, embedded-image counter or speculative-geography counter. Any future genuinely approved image usage requires separate reviewed source changes and a new builder/release decision, **not** editing the current zero-permissions gate.

## Reproduce without WordPress
```bash
python -m unittest discover -s experience2/evidence-atlas/tests -p test_rights_board_r85.py -v
python experience2/evidence-atlas/tools/build_rights_board_r85.py /tmp/fv-r85-board
python experience2/evidence-atlas/tests/package_rights_r85.py --built /tmp/fv-r85-board --out /tmp/FV_R85_A.zip
python experience2/evidence-atlas/tests/package_rights_r85.py --built /tmp/fv-r85-board --out /tmp/FV_R85_B.zip
cmp /tmp/FV_R85_A.zip /tmp/FV_R85_B.zip
```

Dedicated exact-head GitHub CI additionally runs genuine Chromium with JavaScript on/off at **320, 390, 768, 1440, 1920**, axe-core WCAG automated rule checks, native Enter-key disclosure activation, 44px NASA link targets, deep-link anchors, no unexpected external requests, forced colors, reduced motion, print PDF, screenshots, plus **lab-only** LCP and CLS entries when supported. Accessibility automation does **not** substitute for NVDA/VoiceOver or physical devices. Hosted WordPress.com and production field Core Web Vitals remain **unverified**.

Review ZIP includes all input documents, source scripts, CSS, generated HTML/JSON and a deterministic file-level SHA-256 manifest. Screenshots, axe receipts and Chromium print PDF are retained separately by the browser CI job. This is **not an installable plugin**.

## Release decision — HOLD
- 0/6 photograph-specific rights assessments documented; no NASA photo reproduced.
- `S67-19766` official page PIA identity unconfirmed.
- Independent QD; hosted WP.com compatibility in an authorized isolated site; manual VoiceOver/NVDA, touch/zoom and physical-device checks; founder visual/release approval not complete.
- R84 Research Desk chronology remains unchanged; R85 builds only a review artifact.
- Homepage frozen PR #49, homepage leads' branches, original Research Desk PR #158 and production WordPress **must not** be altered.

Tracking: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150 .
