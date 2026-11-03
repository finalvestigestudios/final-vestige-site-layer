# Apollo R89 — Integrated Evidence Review Gate (STAGING HOLD)

**Branch-only source-controlled preview. No WordPress site/content/settings writes, plugin installs, merges, deployment or release authorization.** Built on independent Apollo R88 (#756); original Research Desk PR #158 and homepage PR #49 remain frozen and untouched.

## New substantial integration

R89 builds one offline, source-verifiable review package containing (1) a new provenance hub with six source-bound route groups; (2) the actual R88 interactive Reading Room with complete no-JS evidence plates; (3) the R87 photograph-date ChronologyRail; and (4) R85's individual photographic-rights review board. Every hub record deep-links to the *same* verified NASA source on all three components.

The generator first re-verifies the actual Research Desk and generated Evidence Atlas against the frozen R37, R79 and R55 official-NASA source/rights registers (via R86/R87/R88). It refuses to build on catalog/date/URL/rights drift. The final static HTML is independently parsed: all six official source URLs must appear once in each view; 24 per-record destinations must resolve; local cross-document and same-page fragments must resolve; no photographs, invented geographic coordinates, external scripts or unauthorized external destinations are accepted. A failed validation creates no destination files. The deterministic zip includes all review pages, styles, scripts, receipts, implementation sources, and SHA-256 manifest with fixed ZIP metadata.

The hub works without JavaScript and has native keyboard-operable source disclosures, full official NASA links, 48px targets, print-specific styling, accessible focus and forced-colors/reduced-motion fallbacks. R88 comparison remains progressive enhancement only. All records remain readable when JavaScript is unavailable. The six sources are **not a fire-event chronology**: the portrait's S67-19766 association is provisional, January 1967 has no verified day, and the two January 24 2017 tribute photos are unordered.

## Exact reproducibility (repository root)

    PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experience2/evidence-atlas/tests -p test_review_hub_r89.py -v
    PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tools/build_review_hub_r89.py /tmp/apollo-r89-a /tmp/apollo-r89-a.zip
    PYTHONDONTWRITEBYTECODE=1 python experience2/evidence-atlas/tools/build_review_hub_r89.py /tmp/apollo-r89-b /tmp/apollo-r89-b.zip
    cmp /tmp/apollo-r89-a.zip /tmp/apollo-r89-b.zip

Exact-head GitHub Actions provides pinned Playwright/Chromium and axe-core, tests 320/390/768/1440/1920 at JS/no-JS, cross-page real anchor navigation, Enter-operated disclosures, screenshot hashes, forced colors, reduced motion, WCAG tagged axe audits, local LCP <=2.5s and CLS <=0.1, and a real Chromium print PDF retaining all six official source URL prefixes and hold warnings. Lab timing is **not** hosted WordPress Core Web Vitals.

## Unresolved release blockers

NASA photograph-specific reuse rights remain **0/6 assessed**; catalog S67-19766 not independently confirmed on the NASA page. Hosted WordPress.com compatibility in an authorized isolated environment, human NVDA/VoiceOver and actual phone/tablet testing, independent QA, actual hosted Core Web Vitals, intermittent nested-Gutenberg LCP investigation and founder visual/release approval remain open. No rights or production permission inferred by this build. **HOLD.**
