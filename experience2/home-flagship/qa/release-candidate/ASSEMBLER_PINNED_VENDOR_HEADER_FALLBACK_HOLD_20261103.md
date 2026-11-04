# EX2 Assembler navigation follow-up: exact installed-theme header fallback
**2026-11-03 16:14 PT — DRAFT / NO PRODUCTION RELEASE**

## Concrete evidence, not an inferred green test
- Parent draft PR #862 exact baseline SHA `85ec529774b2a22f7b06a4f2e9728f476638af7f`. The original full-width five-viewport candidate remains source-controlled at parent PR #856 `a55fb0602fe24c0a7bc9eb6b6cfe377280eaaa66`.
- Real WordPress/Assembler Chromium run [41736939617](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41736939617) established **serious axe list** violations at 768/1440/1920, outside flagship root.
- The first native WordPress repair run [41743965479](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41743965479) measured default 768px `ul.wp-block-navigation__container > ul` and a serious `list` violation. It correctly stopped on header source mismatch without modifying the live site.
- The subsequent real hosted run [41744662962](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41744662962) also stopped before local repair: `Unexpected header navigation block shape; wrapped=0 closing=0 selfclosing=0`. **This contradicts the assumption that the value returned by `get_block_template(..., 'wp_template_part')` always contains the executable navigation block.** Exact reason for the mismatch is unverified. The observed official downloaded archive *does* contain one self-closing nav block in `parts/header.html`; hosted archive report pinned its SHA-256 as `3b983fa0d9d6ce9b2bc1024e215d9d63d9ecba2ad11f881ec59e87a40c28c2aa`. Its `patterns/header.php` also contains navigation syntax; do not assume source equivalence between pattern and template part.
- The hosted environment is **disposable Playground**, not production WordPress.com, not the published customized Final Vestige header.

## Isolated proposal (no live edits)
- Keep PR #862's before-state screenshot, actual DOM list topology, and complete-document axe violation **mandatory**. Its guard refuses public hostnames and non-Assembler theme before any local WordPress database write.
- Only when the **resolved WordPress header** contains no recognizable nav, and its source is `theme`, read the installed theme's `parts/header.html` through a canonicalized, same-theme path. Require the independently recorded **exact SHA-256** above and **exactly one** supported navigation block. Otherwise abort. Theme ZIP changes fail closed until a newly reviewed digest is recorded. Neither GitHub nor WordPress production receives the original header contents.
- Build a normal `wp_navigation` record and `wp_template_part` override only inside the isolated local Playground instance. Preserve official installed theme files unchanged. Record whether the resolved header or pinned vendor part was used, plus both source hashes.
- Run real WordPress before/after then complete original five-width/full-document axe/browser/no-JS suite. A successful local after-state cannot be called an **unmodified vendor Assembler** pass or a production navigation fix. The actual live header is customized and **does not use the Playground default page-list fallback**.
- This code does not mask the axe rule, alter Chromium DOM/CSS after render, touch WP production, merge PRs, or approve release.

## Evidence status
This branch has source-level guards and unit-test additions; **a real exact-head hosted WordPress/Assembler result is required** to confirm whether the native template override renders and whether full-document axe clears. Keep release HOLD on any unrun, failed, or incomplete test. Future qualification still needs actual 72 Margins records, Jetpack, keyboard/touch, physical 200% zoom, reduced-motion, image-rights review, measured Lighthouse/CWV, independent QD and founder authorization.

**No publish, deploy, plugin activation, production CMS write, paid upgrade, or modification to frozen #49.**
