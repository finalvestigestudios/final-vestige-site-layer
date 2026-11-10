# R255 — Apollo 1 evidence-path navigation continuity (STAGING HOLD)

Parent: Issue #150; conversion governance #820/#818; stacked on R254 draft PR #1850 at `aefdc987252f64272876ed4cd6943a7e69836546`. This branch contains no homepage PR #49 or original Research Desk PR #158 edits, no live WordPress writes and no production integration.

## Observed defect and bounded correction

The protected, source-custody-checked R238 Apollo Atlas, with R253 and R254 source-link overlays, still presents **three answer-guide cross-reference links** at 22 CSS px high at viewport widths 320/390/768/1440/1920: “Check the atmosphere finding,” “Check the ignition finding,” and “Examine the aftermath record.” These are essential internal evidence-reading actions, not NASA outbound links. The new standalone `evidence-path-touch.css` increases them to at least **44px** without modifying the original archived fragment, citations, source classifications, chronology, 2017 exhibit caveat or editorial destination.

This final overlay MUST be applied *after* R238 stylesheet, R253 overlay and R254 overlay in an **isolated staging review only**. It is **not wired to the live plugin or homepage**. Native links still work without JavaScript; Space/Enter on the source drawer stays native. The print reset removes touch spacing in archival documents and forced-colors focus remains visible.

## Reproduce original-PHP browser QA

Prerequisites: local PHP CLI, Python 3, Playwright Python package, Chromium at `/usr/bin/chromium`. Use the exact sealed R238 fixture from the prior source-custody archive. It is **not** a new source document or a license grant.

```bash
python experience2/apollo-r255/qa/r255_gate.py \
 --atlas path/to/sealed-r238 \
 --r253 experience2/apollo-r253/atlas-source-actions.css \
 --r254 experience2/apollo-r254/provenance-tap-continuity.css \
 --r255 experience2/apollo-r255/evidence-path-touch.css \
 --out /tmp/apollo-r255-qa

python experience2/apollo-r255/qa/ax_perf_probe.py \
 --atlas path/to/sealed-r238 \
 --r253 experience2/apollo-r253/atlas-source-actions.css \
 --r254 experience2/apollo-r254/provenance-tap-continuity.css \
 --r255 experience2/apollo-r255/evidence-path-touch.css \
 --out /tmp/apollo-r255-qa
```

Both runners verify the sealed R238 `manifest.json` SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`, every child hash, and original PHP-generated HTML equality before testing. Browser runner: 5 widths × JS on/off, all visible links and summaries, exact three prior failing targets, 44px min, native hash navigation via keyboard/touch, SourceDrawer Enter/Space, sole free investigation CTA, no unapproved commerce link, no horizontal overflow or unexpected requests, 160px reflow stress, print reset, negative control. Screenshots at 390/1440 × JS/no-JS are deterministic after resetting to fresh documents. Extra Chromium CDP probe checks **accessible names** for three internal evidence links plus offline PerformanceObserver LCP/CLS samples; this is **NOT axe-core** and is **NOT** WCAG certification or a field Core Web Vitals test.

## Release-gate honesty

**BUILT/TESTED locally**, **NOT LIVE/NOT approved**. No installed WordPress/Assembler, real HTTP/CSP/CDN, browser UI zoom, physical-device/screen-reader, genuine axe-core, independent QD, hosted CI or field p75 LCP/CLS acceptance. Source/media rights remain unapproved for paid promotion; inherited R198 ancestry reconciliation unresolved; founder production approval required. Do not merge the draft stack or claim earnings. Original NASA Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA advertising rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .

See `CONVERSION-BRIDGE.md` for the one consent-respecting, unactivated visitor-to-offer hypothesis. Grok controls creator scripts/distribution; Praxxis performs external creator QA; Claude owns commerce/measurement production engineering.
