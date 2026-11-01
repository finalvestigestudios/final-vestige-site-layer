# Apollo R51 — Crew photograph catalog-association disclosure (DRAFT / HOLD)

**Parent:** Apollo R50 PR #505, exact SHA `53dfb2ee9d529e8af92cfaf711b75b02f568a7d3`. Scope limited to `experience2/evidence-atlas/`; Research Desk PR #158, homepage PR #49, all homepage branches, WordPress content/settings remain untouched.

## Finding and source boundary

The R37 pinned crosswalk assigns NASA catalog `S67-19766` to the linked **Apollo 1 Crew Honored** January 1967 photograph. Its own `identity_note` states that NASA-hosted image filename evidence is the basis and structured catalog metadata is **not separately confirmed**. NASA's linked page, reviewed November 1, 2026, describes the crew and photograph month but does not print that catalog number. An alternative Apollo crew portrait has NASA's explicitly labeled `S66-30236` (a different photograph); neither confirms that `S67-19766` belongs to the R37-linked photograph. Do not silently replace IDs or shift records: that would violate pinned source custody and established Research Desk linkage. **Record 01 photo-to-catalog identity remains provisional; a NASA archives/catalog inquiry or unequivocal primary catalog record is required before release.**

Sources reviewed: https://www.nasa.gov/image-article/apollo-1-crew-honored/ ; https://www.nasa.gov/image-article/apollo-1-prime-crew-portrait/ ; https://www.nasa.gov/wp-content/uploads/static/history/SP-4029/Apollo_18-47_NASA_Photo_Numbers.htm . R37 custody Git blob unchanged: `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`.

## Implementation

- R51 adds a visible no-JS disclosure in the Atlas masthead, first EvidencePlate, complete citation register, source-register downloads, and WordPress suite header (unchanged Research Desk record label is not allowed to obscure the uncertainty).
- All six original source links, IDs, filters, chronology, drawers, pair inspector, printability and reciprocal navigation remain. No photographs, invented pins, map edges, or inferred historical relationships.
- Atlas staging version `0.0.51-staging`, with compiled HTML SHA-256 `139f64b52b27977c4caf71685a03065b21b477ac3fbbbe3b6fafd14e635736f3`. R50 integration adapter updated to version `0.0.51-staging`. The source crosswalk remains unchanged.
- New R51 Chromium QA covers eight widths 320–1920 in JS on/off, downloaded six-citation register integrity after filtering, keyboard/touch-capable rendering, no unexpected requests/overflow, and reproducible screenshots. Chromium uses PHP-assembled Atlas plus **synthetic Desk markup**, not original PR #158 HTML/CSS or authentic WordPress/HTTP.

## Release blockers (all HOLD)

Individual photograph rights for all six photographs; unresolved `S67-19766` association; authentic original Research Desk HTML/CSS browser QA and WordPress/Assembler co-installation; verified axe-core; Safari/assistive technology; hosted p75 LCP/INP/CLS; exact-head CI; independent QD and founder approval. NASA's official image/brand guidance forbids implied endorsement and requires review of third-party/publicity issues: https://www.nasa.gov/nasa-brand-center/images-and-media/ .

## Reproduce

```bash
cd experience2/evidence-atlas
python test_atlas.py
python -m unittest discover -s tests -p 'test_*.py' -q
php -l final-vestige-ex2-evidence-atlas.php
php -l integration/fv-ex2-apollo-suite.php
node --check atlas.js
python tests/browser_r50_suite.py --output /tmp/apollo-r50-regression
python tests/browser_r51_provenance.py --output /tmp/apollo-r51-qa
python tests/build_r51_bundle.py --qa-dir /tmp/apollo-r51-qa --output /tmp/apollo-r51-review.zip
```

These checks do not constitute production approval.
