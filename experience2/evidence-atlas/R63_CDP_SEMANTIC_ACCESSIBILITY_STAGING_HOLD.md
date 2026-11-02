# Apollo R63 — Chromium semantic accessibility and high-contrast staging (HOLD)

## Source baseline and scope

R63 derives exclusively from R62 (`75a8af83b5838ecf667c7c30891d56a1a4bd2c64`), retains the original R38 Research Desk Git-blob-pinned source and NASA custody crosswalk, and changes only `experience2/evidence-atlas/`. Original Research Desk PR #158 and frozen homepage PR #49 are not edited. No NASA photo binaries, speculative geographic pins, WordPress writes, deployment, or paid services.

## Improvements

- Scoped `forced-colors: active` styling adds system `Highlight` outlines for Apollo suite links, buttons, text inputs, and native disclosure summaries, and underlines links independent of the antique-gold palette. No original component CSS/markup/source pin changed.
- `tests/browser_r63_semantic_accessibility.py` uses real Chromium CDP `Accessibility.getFullAXTree` on the unchanged R38 Desk and generated Atlas, failing if an exposed interactive control is unnamed, a fragment anchor is broken, duplicate IDs occur, unexpected network requests occur, or the two source collections disappear. It checks native keyboard disclosures, two independent filters, print conservation (6+6 sources, 30+54 custody values), 200% text reflow with JS, OS forced colors, reduced motion, and 320–1920px.
- Axe-core testing is **optional but fail-closed**: it runs only when both local bundle path and a matching SHA-256 are supplied; it does not silently equate CDP accessibility checks with axe certification.
- WordPress suite integration version updated to `0.0.63-staging` so the updated CSS can be cache-busted on approved staging; corresponding strict regression assertions updated.

## Executed local evidence

- `python -I -m unittest discover -s tests -p test_*.py -q`: 98 tests, 97 passed and 1 skipped (original PR #158 fixture unavailable in isolated package).
- `python test_atlas.py`: 11/11 passed.
- `python -I tests/browser_r63_semantic_accessibility.py --output <qa>`: **32/32** Chromium/CDP configurations (8 widths × JS on/off × normal/forced colors), no unnamed exposed controls, no duplicate IDs or broken fragment links, no unexpected requests, no overflow, keyboard disclosures working, complete printed custody.
- `php -l integration/fv-ex2-apollo-suite.php` and `node --check atlas.js`: passed.
- Local component LCP observations: 116–148ms, CLS=0. This **is not** a hosted performance or p75 CWV result.
- Two screenshots (390 and 1440) and an exact-configuration JSON receipt produced in the locally reproducible artifact; binary files are not committed.

## Release blocks

**HOLD:** No installed private WordPress/Assembler rendering; no checksum-verified local axe-core available to this run (so axe was **NOT RUN**); no NVDA/VoiceOver manual acceptance; no hosted p75 LCP/INP/CLS; no independent QD certification; CI must pass on exact head; 0/6 NASA image rights assessments are complete and S67-19766 association stays provisional. No approval to merge, install or deploy.
