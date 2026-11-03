# Apollo R93 — Portable source-register and period lens (STAGING HOLD)

**Scope:** Experience 2.0 Apollo 1 evidence components only; not homepage PR #49, homepage lead's branches or original Research Desk PR #158. No WordPress writes, production merge, paid services, imagery, or NASA endorsement.

## New reader-facing capability

`R93_SOURCE_REGISTER.html` provides six primary-source-bound Evidence Atlas research entries with a documented **can establish / cannot establish** boundary, complete original NASA image-detail links, precise photographic-date certainty, explicit individual-image reuse holds, and four direct routes for each source back into the existing Hub, Reading Room, photo-date rail and rights-review board. Native semantic links and text work without JavaScript. A small optional `source_register_r93.js` allows a keyboard-operable photograph-period filter: all six; day-specific 1966–67 context; 2017 retrospective displays; and the month-only crew portrait. Categories are **photograph-date groupings only**, not an Apollo 1 accident reconstruction.

`R93_APOLLO_SOURCE_REGISTER.csv` offers a ten-column portable source table for independent research: record ID, title, proposed catalog ID, photograph date, certainty, supported claim, limitation, NASA URL, unresolved photo rights, and provisional/catalog status. All values are derived from the existing Research Desk **and** checked against R89's six canonical NASA URLs. CSV spreadsheet-formula injection is rejected before packaging. Source export preserves the proposed `S67-19766` catalog association as **provisional**, not verified. Neither photographs nor speculative coordinates/edges are included.

## Building from actual reviewed source

From repository root:

```bash
python -I experience2/evidence-atlas/tools/build_citations_r93.py /tmp/r93-stage /tmp/R93_A.zip
python -I experience2/evidence-atlas/tools/build_citations_r93.py /tmp/r93-stage-2 /tmp/R93_B.zip
cmp /tmp/R93_A.zip /tmp/R93_B.zip
python -I -m unittest discover -s experience2/evidence-atlas/tests -p test_citations_r93.py -v
```

R93 normally imports the actual R92 builder, which inherits the R91/R90/R86 source/asset custody checks against the original Research Desk and Evidence Atlas. An `--reviewed-r92 /path/to/r92` option is provided **solely** for offline inspection of a previously generated R92 package; it checks the R92 receipt and every recorded file checksum before exporting. CI must use the default real-source build path. The archive uses fixed zip metadata and a SHA-256 manifest.

## Acceptance and release

Real Chromium CI captures 320, 390, 768, 1440, 1920 widths with JS on/off, keyboard-operated period filters, all ten CSV download paths, link touch-target checks, source totals, no overflow, forced colors/reduced motion, axe-core scans at 390/1440, LCP/CLS observations, reproducible PNG screenshots and native PDF text validation for all six original NASA URLs and all six outstanding reuse warnings. The existing R92 source/Chromium and genuine disposable WordPress workflows run on the same stacked PR as inherited gates.

**Lab-only performance results never imply hosted or production Core Web Vitals.** Manual NVDA/VoiceOver, actual devices, authorized isolated hosted WordPress.com installation, six photo-by-photo usage decisions, independent editorial/QD review, investigation of intermittent Gutenberg LCP failures, and founder authorization remain blockers. No release, installation or activation is authorized. Read-only NASA policy: https://www.nasa.gov/nasa-brand-center/ .
