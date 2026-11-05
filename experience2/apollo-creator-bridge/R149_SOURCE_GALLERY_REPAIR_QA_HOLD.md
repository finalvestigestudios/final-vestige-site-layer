# Apollo R149 — gallery correction, accessible context status, source-derived regression

**2026-11-05 — BUILT / NATIVE-TESTED / CHROMIUM MODEL-TESTED / STAGING HOLD.** Scope: Experience 2.0 Apollo 1 only. Governance: #150, #820, #818. Stacked on R148 draft PR #1140; never touch homepage PR #49, Research Desk PR #158, Grok's queue, commercial systems or WordPress settings/content.

## Current real WordPress source (read-only connector)

- Page **2017**, published at https://finalvestige.com/apollo-1-evidence-atlas/; reported WordPress modified **2026-11-04T17:09:24**.
- **Raw Gutenberg source length:** 96,274 Unicode characters, SHA-256 `cdaca5ae9d10534a067a8f4095a1362eb1078af48694238860d7f470233849bc`.
- Selector `const photos = $(box, '[data-fvx-chrono-photo]');` occurs once; the array-capable `$$` selector occurs zero times. The 3 real gallery records each occur once, with 4 recorded chronology markers at +0, +6, +11.3 and +14.7 seconds.
- Single existing **Read the full investigation** CTA resolves in source to https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . NASA Board report and three photograph source links were found in the raw source.
- The current script's gallery branch expects `photos.length === 3` and `photos.forEach`. With single-element `querySelector`, that branch cannot execute; gallery photos do not switch. **This is a verified source-code defect, not a claim of independently observed production browser interaction.**
- Source-derived, **unpatched**, read-only excerpt of the actual chronology, CSS and JS is versioned in `fixtures/r149_published_chronology_source_excerpt.html`. It is **not the whole WordPress-rendered page**, excludes WP/Assembler/Jetpack integration and does not prove image delivery.

## Actual source-controlled fix

`r149_gallery_release_candidate.py` requires exact unpatched selector/status, all four markers, all three archival figures, all four NASA-source references, disclaimer and existing article CTA. It refuses a different source, duplicate patch or overwritten output. With a caller-supplied independent raw-export SHA-256, it creates **separate local review HTML + staging-hold manifest** and never touches WordPress.

Two strictly scoped changes: 
1. Replace `$(box, '[data-fvx-chrono-photo]')` with `$$(box, '[data-fvx-chrono-photo]')` (3 contextual photographs can switch).
2. Add `role="status" aria-live="polite" aria-atomic="true"` to the existing optional gallery-position announcement. All evidence-source links, historical copy, original image source/credits, chronology markers, and existing reader CTA remain byte-for-byte unchanged.

Exact proposed **raw Gutenberg** review length **96,327 characters**, SHA-256 **`7a03805dc717c89e9703f86139a56e6cd1098f4aa2f2793a2bceb9154f90106a`** as independently derived in read-only WordPress source analysis. Patch reversibility is exact. The earlier gallery-only R147 hash `39dd5adcfe1a4ad1d501a1a94d760b1037111a487908698e649ecaa5103334e7` is **not** the same output; R148's pinned receipt must not be reused to approve R149.

## Tests and truthful limitations

- Native Python **13/13 PASS** with committed SHA-matched source and tests (using Python 3.13 in the local working environment). Adversarial cases: duplicate selector, missing photographic record, missing NASA Board source, changed chronology mark, wrong article URL, changed disclaimer, self-approval/overwrite, stale hash and second application.
- Chromium **144.0.7559.96**, local controlled model fixture: **123/123 PASS**, six widths 320/360/390/768/1440/1920; before-selector negative control, after gallery at 0/6/11.3/14.7; live-region status, keyboard, responsive overflow, and no-JS original captions. **Seven screenshots**, SHA-256 captured; second independent local run produced identical JSON checks and identical screenshot byte digests. The model is **NOT** the source-derived WordPress excerpt.
- A genuine read-only source excerpt is committed for the next real Chromium pass, but **that excerpt was NOT executed in the local browser in this sprint**. No full exported WordPress page was exercised.
- **axe-core NOT RUN** (not installed). Actual-page WCAG, LCP/CLS, real image fetch and WordPress runtime integration: **NOT VERIFIED**. Production release gate remains CLOSED.
- Photographic records were source-linked, **not individually cleared for commercial goods**. NASA prohibits falsely implying endorsement; rights/publicity review remains mandatory before any paid reuse. See https://www.nasa.gov/nasa-brand-center/.
- No new paid offer, affiliate integration, measurement script, tracking, subscribers, merchant configuration, social post, CMS mutation, deployment or spend.

## Reproduce locally (offline, never connects to WordPress)

```bash
cd experience2/apollo-creator-bridge
python -m unittest -v test_r149_gallery_release_candidate.py
python r149_gallery_browser_regression.py --input fixtures/r149_published_chronology_source_excerpt.html --out /tmp/fv-r149-published-excerpt-qa
# If independently exported full raw WP content + SHA-256 are available:
python r149_gallery_release_candidate.py --input /path/raw-gutenberg.html --expected-sha256 cdaca5ae9d10534a067a8f4095a1362eb1078af48694238860d7f470233849bc --output /tmp/apollo-r149-review.html --manifest /tmp/apollo-r149-manifest.json
```

Run browser test with locally installed Playwright and `FV_CHROMIUM=/path/chromium` as needed. **Never present the excerpt/model as live browser, axe or CWV evidence.** Run real WP staging after sanctioned integration and exact-head hosted CI / QD independent review, then obtain founder release approval.

## Conversion bridge (one contextual action, no unrelated commerce)

**Hypothesis:** Educators arrive from a Grok long-form Apollo 1 investigation, inspect the documented chronology and source drawer, follow **Read the full investigation**, and only after a genuinely verified, rights-cleared merchant listing exists encounter a relevant classroom casefile offer. The educator casefile remains a **hypothesis, not an authorized SKU or observed sale**. No purchase CTA is introduced to the narrative.

Commercial metric governance: distinct Grok asset_id/UTMs → qualified human landing session → CTA click → independently confirmed lead (if any) → independently verified order → refunds/fees → net revenue/1,000 qualified humans in 7/30-day cohorts. All conversion figures currently **NOT VERIFIED**, so the KPI is **NOT COMPUTABLE**. Grok owns distribution, Praxxis creator QA, Claude website/analytics engineering; Apollo lane owns isolated evidence-experience code/QA only.

**Release decision: STAGING HOLD.**
