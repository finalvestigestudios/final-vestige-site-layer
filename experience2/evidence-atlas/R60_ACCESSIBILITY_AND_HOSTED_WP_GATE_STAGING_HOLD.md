# R60 — original Research Desk hit-target remediation and authentic WordPress/axe gate (STAGING HOLD)

**Scope:** Experience 2.0 Apollo 1 / Research Desk / Evidence Atlas, isolated branch based on R59 PR #568. No homepage PR #49 or homepage lead branch edits; no edits to Research Desk PR #158 or its original SHA-pinned bytes. No WordPress/CMS writes, deploys, speculative geo pins, NASA photo binaries or new paid services.

## Verified issue and correction

In real Chromium rendering of the original five-file R38 Research Desk alongside the source-built Atlas, source links and native `<summary>` controls were approximately **21 px high** (at 320, 390 and 1440 CSS px). The suite-level CSS now gives the twelve NASA/source links, twelve native source-finding/provenance disclosures and two footer links **44px minimum hit heights**. The original summary `display:list-item` and disclosure markers are intentionally preserved. An explicit high-contrast `:focus-visible` outline is provided. These changes apply exclusively inside the Apollo staging suite and only to **screen** media; the R59 full-source printed custody remains unchanged. Suite stylesheet cache version is `0.0.60-staging`; original Atlas version/pins and R38 files stay unchanged.

## Reproducible local acceptance

```sh
python -I -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q
python -I experience2/evidence-atlas/test_atlas.py -q
python experience2/evidence-atlas/tests/browser_r60_real_source_accessibility.py --output qa-r60
```

The browser runner imports the R59 exact-source, original-PHP cohost fixture: all five original Research Desk Git-blob pins and the Atlas build and template SHA must pass before any browser assertions. It checks 320, 360, 390, 428, 768, 1024, 1440 and 1920 widths with JS on/off; keyboard activation, preservation of the native disclosure marker, CDP Accessibility-tree names, touch, 44px hit areas, real six-record source/print custody, console/network, overflow, reduced motion and reproducible screenshots. CDP accessibility-tree checks are **NOT** axe-core certification.

## Authentic hosted WordPress acceptance — not yet performed

A reviewer with an **existing approved private WordPress/Assembler staging page** can run the same runner in read-only mode, supplying both a locally obtained real axe-core JS distribution and its independently verified SHA-256:

```sh
python experience2/evidence-atlas/tests/browser_r60_real_source_accessibility.py \
  --output qa-r60-wp --wp-url 'https://PRIVATE-STAGING-ONLY/apollo-test/' \
  --axe-file /local/trusted/axe.min.js --axe-sha256 THE_VERIFIED_64_HEX_DIGEST
```

This is a hard gate: with no pinned bundle or no private staging page, **do not claim an axe pass or authentic WordPress pass**. The hosted runner makes read-only page requests, verifies all three CSS handles in the document head (plus both original component scripts), runs WCAG2 A/AA, 2.1 AA and 2.2 AA axe tags, and checks interactions across 16 configurations. No WordPress login, credential writing, media fetching or settings changes. Hosted p75 Core Web Vitals and independent screen-reader acceptance remain distinct release gates.

## Known release blockers

- No available isolated genuine WordPress/Assembler page or WordPress core in the test environment; local WP API simulator is not sufficient.
- No independently pinned axe-core bundle available to execute; CDP AX-tree tests do not substitute for axe.
- No screen-reader/assistive-technology manual acceptance, hosted field p75 LCP/CLS/INP or independent quality review.
- No successful exact-head CI certification; report actual GitHub status separately.
- Six NASA photograph rights reviews remain pending, zero photographs embedded; the `S67-19766` catalog-to-photo association remains unconfirmed.
- DO NOT merge, install, publish or deploy this prototype without the governed approval process.

## Source and chain of custody

Read Issue #150, original Research Desk PR #158, R59 PR #568. The original R38 and Atlas files are source-locked. The only runtime behavior change in this branch is suite-scoped CSS plus its cache version. The primary linked historical authority remains NASA's Apollo 204 Review Board report; source dates are not fire-event chronology. Retrospective 2017 photographs are correctly labeled retrospective, not contemporary 1967 accident pictures.
