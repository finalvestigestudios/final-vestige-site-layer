# R86 — Actual Research Desk × Evidence Atlas × NASA Source Concordance (STAGING HOLD)

**Scope:** Apollo 1 / Experience 2.0 only. New isolated source-controlled review artifact, NOT a production site page, WordPress plugin, photograph gallery or rights clearance. Stacked on R85; never edit or merge homepage PR #49, homepage lead branches, original Research Desk PR #158, or live WordPress content/settings.

## Why this sprint
R85 independently evaluated the six source/rights records, but a workbench displaying correct data does not itself establish that the **actual native WordPress Research Desk and Evidence Atlas** render matching NASA destinations. R86 closes that audit gap. It treats R37 crosswalk, R79 manual NASA-page metadata and R55 pending-rights profile as immutable source registers, then independently parses the actual six Research Desk template articles and generates/parses the Evidence Atlas articles. Each catalog and NASA photo link must match the source **within its corresponding article**, not merely appear somewhere on the page. All six Research Desk native rights drawers must also retain the matching record ID.

The command fails closed before generating any output if any source link, catalog, card identity, drawer association, image reuse counter or atlas custody register has drifted. The actual Desk and generated Atlas source bytes are hashed in the receipt. The result is an additional **integrated reviewer matrix** and six detailed source/rights crosswalk cards, not a replacement for either component. It uses native details and anchor links for keyboard/no-JS access, a scrollable responsive comparison table, print-readable NASA URLs, no external JS or photo assets and zero speculative map edges.

**Important distinction:** “3-register/2-component parity PASS” means links and catalog identities match. It is not image-rights clearance, individual photo identity proof, historical-causation evidence, NASA approval or release authorization. The S67-19766 crew portrait remains provisional; its exact day in January 1967 remains unknown. Two January 24, 2017 records cannot be assigned an intra-day sequence.

## Offline reproducibility

```sh
python -m unittest discover -s experience2/evidence-atlas/tests -p test_concordance_r86.py -v
python experience2/evidence-atlas/tools/build_concordance_r86.py /tmp/r86-concordance
python experience2/evidence-atlas/tests/package_concordance_r86.py --built /tmp/r86-concordance --out /tmp/R86_A.zip
python experience2/evidence-atlas/tests/package_concordance_r86.py --built /tmp/r86-concordance --out /tmp/R86_B.zip
cmp /tmp/R86_A.zip /tmp/R86_B.zip
```

Dedicated exact-head GitHub CI runs these tests, produces a reproducible SHA-256-manifested ZIP and uses **actual Playwright Chromium** at 320, 390, 768, 1440 and 1920px in both JS-enabled and no-JS contexts, with native Enter activation, anchored table navigation, 44px link targets, no remote requests, no images/geo, horizontal overflow, pinned axe-core, reduced-motion and forced-colors checks, 390/1440 screenshots, lab LCP/CLS receipts and native A4 PDF verifying six printed NASA source URLs and catalog identities.

The performance numbers from file:// Chromium staging are **not** hosted WordPress/production Core Web Vitals. Automation cannot replace manual assistive-tech and physical-device acceptance.

## Release decision: HOLD
- All 6 photographic-reuse assessments pending; no NASA photos reproduced.
- Provisional S67-19766 catalog-to-photo association is not confirmed by the linked NASA image-detail PIA field.
- Separate hosted WordPress.com staging compatibility, independent QD, real NVDA/VoiceOver, physical device/zoom and founder release approval remain undone.
- No merges, paid services, WordPress write calls or production deployments authorized.

Background sources: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/image-article/apollo-1-crew-honored/ . The NASA-linked page dates the *portrait* only to January 1967; this work never converts the 2017 publication date into a 1967 photographic day.
