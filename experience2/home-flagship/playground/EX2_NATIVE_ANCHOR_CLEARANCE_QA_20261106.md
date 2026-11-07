# EX2 Flagship — native anchor clearance, exact-source Chromium (2026-11-06)

**Status: draft / release HOLD.** Parent: #1320 at `b33d18792ec51256db4a3e082cf6aa85471fc0fc`. Frozen #49 is not changed. This is a narrow but substantive correction to the existing **seven-chapter** candidate, not a new design or another chapter.

## Verified functional defect

Prior CSS declared a `:where(#fv-hf-...)` 74px chapter scroll margin, but higher-specificity earlier ID selectors gave key chapters only 16–26px of native fragment clearance. The sticky reading rail covers approximately 38–45px of the top viewport. Native chapter links scrolled destination headings underneath that rail **even with JavaScript disabled**. The main **Enter the evidence room** hero action points to the affected destination.

**Before:** exact-source local Chromium native anchor test, 7 widths × JavaScript off/on × 6 destination chapter anchors = **84 interactions**: **80 obscured / 4 clear**. Typical `390px` destination top 16px versus sticky rail bottom 45px (**−29px** clearance).

**After:** same source-based offline browser scenarios: **84/84 clear**, minimum measured clearance **34.5px**; at 390px typical target top 80px versus rail bottom 45px (**+35px**). The scoped override uses ID specificity and `scroll-margin-top: calc(var(--fv-trail-top, 0px) + 80px)` for all seven chapter targets, including the hero heading.

## Reproduction and evidence

Run `python experience2/home-flagship/playground/verify_anchor_clearance_browser.py --blueprint experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json --output /tmp/ex2-anchor-review` with Python Playwright and Chromium. The committed verifier runs the exact Blueprint's nowdoc HTML/CSS/JS in an **isolated static browser**, compares baseline (remove only this scoped fix) and candidate, exercises native links, checks hash, viewport overflow and 12px minimum clearance, and writes JSON and first-screen screenshots.

Local extended study also confirmed 7 widths, 2 script modes, the 72/72 public Margins fragments, 5 unchanged Focus destinations, 2 archive images and pinned Assembler commit. No new history, media assets, affiliate placements or analytics.

## Release distinction

**BUILT**: source-level CSS correction and committed browser verifier. **TESTED**: 168 total baseline/candidate source-based Chromium anchor interactions, with 80 failures before and no failures after, plus negative control. **NOT TESTED**: real WordPress Playground/Assembler rendering, independent axe/WCAG 2.2 AA, image response bytes, actual no-JS Jetpack signup, Safari, field Core Web Vitals, Lighthouse, or purchases. These remain fail-closed release gates. This source test is **not** actual staging.

## Sources / permissions and conversion

Apollo asset is existing WordPress media #473, NASA image S67-19766 (metadata 78,346 bytes, 1041×810); Franklin media #474 is the 1847/1848 Victory Point record displayed via a Commons public-domain reproduction (metadata 466,043 bytes, 960×1526). These are **metadata and editorial credits only**; bytes/rights still require independent review. NYPL asset #1258 remains excluded. All 72 original source-preserved public Margins records remain present.

**Offer → funnel → blocker → experiment → evidence → owner:** Free 52-page Focus Fieldbook → historical hero/evidence navigation → hidden destination headings impaired context and source-trust flow → native scroll-margin correction → 80/84 navigation failures before, 0/84 after in isolated Chromium → homepage engineering + independent Site QA. Claude owns tracking, signup and sales measurement; Grok/Praxxis own campaign acquisition; founder retains release rights. **No verified additional lead, order, affiliate conversion or net revenue.**

WordPress.com Personal plan has no native clone; free isolated WordPress Playground is still required for complete seven-chapter WordPress-native acceptance. No production WordPress writes, installs, merges, emails, spend or activation.
