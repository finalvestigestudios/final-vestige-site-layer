# Apollo R62 — immutable photographic-date identity (STAGING HOLD)

## Source-integrity defect

The R61 Atlas accepted any photograph year in {1966, 1967, 2017}, as long as the corresponding ChronologyRail entry was in an era labeled with the same year. It also accepted arbitrary changes to the displayed photograph date, the `<time datetime>` attribute and the exported citation date. A coordinated plausible-but-false date could therefore survive the optional browser filtering, comparison, and chronology-navigation checks.

## Minimal isolated correction

`atlas.js` now pins the exact six year / date / label triples from the **existing, SHA-reviewed R37 photographic custody crosswalk**, including record 01's explicit unknown day. `valid()` checks each original source card, the associated ChronologyRail `<time>`, the year grouping, and the source-register citation against those pinned dates. Hash/history navigation revalidates provenance even when a record is already visible. Source drift withdraws **only optional enhancements**, reveals all original evidence cards, and leaves static NASA source links/disclosures available. Neither the original R38 Research Desk files nor NASA/media assets are altered.

`integration/fv-ex2-apollo-suite.php` `atlas.js` pin and staging version are updated together. The date crosswalk remains photograph metadata, **not** a reconstruction of the fire or a geographic hypothesis.

## Reproducible local QA

- `python -I -m unittest discover -s tests -p 'test_*.py' -q`: 98 tests, 97 passed, 1 skipped (isolated PR #158 fixture absent).
- `python test_atlas.py`: 11/11 passed.
- `python tests/browser_r62_date_custody.py --output ...`: 16/16 actual-source Chromium configurations, eight widths 320–1920, JS on/off; 24/24 coordinated forged-year, forged-date, and hash-after-date-forgery cases withdraw enhancement; no external requests/errors/overflow; original R38 and Atlas retain six each; print preserves 30 Desk and 54 Atlas custody values.
- Prior R61 source/history Chromium 16/16 and R60 keyboard/target-size Chromium 16/16 rerun after changes.
- `php -l integration/fv-ex2-apollo-suite.php` and `node --check atlas.js`: pass.
- Screenshots, source/QA SHA-256 hashes, and byte-identical deterministic archive are included in the local staging package; no binary images checked into GitHub.

## Release HOLD — NOT CERTIFIED

This is PHP API **simulation** of the actual SHA-pinned R38 Research Desk and source-built Atlas, **not** an installed WordPress/Assembler. Private WordPress integration and rendering, independently verified axe-core, NVDA/VoiceOver, hosted p75 LCP/INP/CLS, independent QD and exact-head CI are outstanding. Individual NASA image reuse remains **0 of 6 approved**. `S67-19766` association remains provisional. No photographic image binaries are embedded; no speculative geography, analytics, paid services or WordPress writes.

Do not merge, deploy, install, publish, or change homepage PR #49, the homepage release lane or PR #158. Coordinate with the homepage owner before any eventual cross-component acceptance.
