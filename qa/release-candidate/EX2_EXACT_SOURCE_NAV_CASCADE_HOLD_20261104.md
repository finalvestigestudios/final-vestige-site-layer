# EXACT-SOURCE QA: mobile nav stylesheet cascade and sticky-rail occlusion (HOLD)

**2026-11-04 PT.** Parent candidate PR #936 at exact head `72e5b4685f403621fb27eefdba6ffff5845aaafa`. Separate draft branch. This document **does not** authorize WordPress production, merge, plugin install or CI/QD approval.

## Reproduced defects on actual source

The original `flagship.css` hides the old `.fv-hf__nav` at <=920px, but a **later-loaded** `chronicle.css` rule reintroduces `display:flex` at the same breakpoint. The new native mobile Explore therefore appears **alongside** duplicate legacy navigation. The existing committed full-source nine-width Playwright gate independently **FAILED at seven of nine widths** (320, 360, 390, 420, 600, 768, 920); 921 and 1440 passed.

A second independent browser defect: sticky chapter rail `z-index:65` covered the first Explore destination while masthead had `z-index:2`. `is_visible()` missed this because it does not prove hit-target accessibility. Reproduced in exact source at 320, 390 and 920.

## Corrective implementation

1. `chronicle.css`: remove obsolete mobile-only desktop-nav override and associated dead mobile desktop-nav declarations; retain chronicle chapter layout.
2. `flagship.css`: scope masthead stacking elevation to mobile (80), above chapter rail (65), without changing desktop stacking.
3. `tests/verify_mobile_explore_browser.py`: center-point `document.elementFromPoint` check for **every** opened Explore route, not only Focus CTA; fail on occlusion.

## Executed evidence (local Chromium, actual committed source files)

- Exact immutable source reconstruction: **14/14 GitHub blob SHA matches** before modification; three updated blobs verified against upload.
- Legacy parent exact-source gate: **2/9 PASS, 7/9 FAIL** for duplicate desktop+mobile nav.
- Negative control 1, old `chronicle.css`: **7/9 FAIL**, as expected.
- Negative control 2, fixed cascade but old masthead stacking: **7/9 FAIL** (Investigations covered), as expected.
- Proposed two fixes: **9/9 PASS** at 320,360,390,420,600,768,920,921,1440; JavaScript **disabled**, reduced motion on.
- Actual source with all six stylesheets + all four scripts: **10 widths, zero duplicates after vs seven duplicates before**, both JS enabled and disabled; Focus CTA unobstructed; no horizontal document overflow or uncaught JS exceptions in the local run.
- Existing chapter-keyboard source gate **21/21 PASS**. Existing Focus masthead source gate **9/9 PASS** across 320–1920px.
- Visual PNGs, before/after measurement JSON, regression receipts and reproduction script supplied to founder separately as local review ZIP; PR code contains executable regression test.

## Preservation / rights and commercial boundary

No chapters or original sources changed. The native Investigations/Public Record/Library routes and 52-page Focus link remain identical. Apollo WP #473 (78,346-byte metadata), Franklin WP #474 (466,043-byte metadata) unchanged; NYPL #1258 5,553,669-byte original remains editorial fallback pending capture-specific rights. **WordPress metadata is not proof of image transfer bytes or re-use rights.** No new imagery, fonts, scripts, affiliate offers, analytics or payments.

**Offer → Funnel → Blocker → Change → Evidence → Owner:** Free Focus Fieldbook → first-screen evidence discovery → duplicate nav + inaccessible Explore first route → scoped cascade/stacking repair + hit-target admission → full exact-source 2/9 to 9/9 with two negative controls → interim homepage engineer. Claude retains attribution/commerce; Grok/Praxxis remain acquisition. No sales or confirmed leads measured.

## Outstanding release gates

**HOLD:** This is offline exact-source Chromium, **not** WordPress/Assembler staging, Jetpack acceptance, complete-document axe/WCAG 2.2 AA, physical 200% zoom, real archival-media transfer, Lighthouse/field CWV, independent QD or founder release approval. WordPress.com Personal has no native staging clone; free Playground/isolated developer site remains the staging route. Frozen PR #49 and Apollo #158 must remain untouched. No merges, deploys, CMS writes, subscriptions or spending.
