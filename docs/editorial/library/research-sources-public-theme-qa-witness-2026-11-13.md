# Final Vestige Library · public-theme QA witness (13 November 2026)

**Scope:** Public WordPress Library Research Sources page **#1338** only. Do not use staging draft #2354 as a count-only replacement. No WordPress, newsletter, social, subscriber, media or template mutation is authorized by this document.

## Verified authoritative evidence — 2026-11-13

- Fresh authenticated WordPress **edit-context** readback: page **#1338**, `status=publish`, last modified **2026-11-03T22:12:43** (site-local); 3 core HTML blocks. First HTML block has **60** `article.fv-rs-card` entries. Third HTML block contains **30** further entries in a separate **no-JS fallback container** `#fv-rs-batch003` (actual visual visibility must still be checked against the live theme), which the script moves to category grids when JS runs.
- All **90 saved cards** have **90 distinct titles and 90 distinct primary card hrefs**, with category counts **declassified 12; accountability 24; engineering 21; archives 25; navigation 8**. The source did not change in this run.
- Published initial header/search/filter text still advertises **60**. The supplemental JS updates many labels to 90 after loading but embeds an incorrect category total (`accountability:23`, `archives:26`). A visitor without JavaScript sees the 30 fallback cards but stale 60-label text. Do not remove the fallback while repairing labels.
- Published SEO description already says **Ninety**; `jetpack_seo_noindex=false`.
- Newsletter `get_settings` on 2026-11-13 returned `email_new_posts_by_default=false`. Recent Jetpack sends show some prior opted-out sends. This **does not verify** a per-page first-publish `_jetpack_dont_email_post_to_subs=true` nor automatic-social suppression; explicitly confirm both in supported publish controls.

## New test tool and synthetic smoke test (not production proof)

A read-only Playwright Chromium script, `library_public_qa.py`, plus original fictional fixtures and an interactive HTML release witness were produced in the November 13 Library Studio run. The Python script is site-scoped to **https://finalvestige.com/free-resources/research-sources/** for network runs (file fixtures must be explicitly opted into), uses no credentials or mutation endpoints, captures **320/390/768/1440** screenshots with JavaScript on/off, checks 90 cards/unique URLs, category totals, labels, overflow, search of a supplemental record, filter counts and keyboard input focus, and writes an offline JSON report.

Local **fictional corrected fixture:** **8/8** viewport/mode executions pass, with export/interaction checks. Local **fictional stale fixture:** **4/8** pass; the four no-JavaScript executions correctly flag the stale `60` headline/search/category labels. This **does not** mean live WordPress QA passed.

The separate interactive HTML witness passed local 320/390/768/1440 overflow, checkbox/JSON export and JS-error smoke checks; all are local, synthetic, and not WordPress-theme screenshots.

## WordPress screenshot-service requests — links, NOT verified pixels

The WordPress screenshot endpoint reports `ready` with `capture_shows=site` at four widths, but the actual image bytes were inaccessible in this tool runtime:

- [320 px](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffree-resources%2Fresearch-sources%2F?vpw=320&vph=2200&w=1200&requeue=true)
- [390 px](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffree-resources%2Fresearch-sources%2F?vpw=390&vph=2200&w=1200&requeue=true)
- [768 px](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffree-resources%2Fresearch-sources%2F?vpw=768&vph=2200&w=1200&requeue=true)
- [1440 px](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffree-resources%2Fresearch-sources%2F?vpw=1440&vph=2200&w=1200&requeue=true)

Neither screenshot-service URLs nor local fixtures count as inspected *production pixels*. The browser QA owner under **#1589** must verify the actual current theme (including mobile overlays, header, keyboard focus, no page-wide overflow, filter/search, and 30 supplemental entries). Preserve evidence and date.

## Guarded release requirements

1. Re-read #1338 immediately before any edit; compare the current content fingerprint with the candidate guarded patch. Reject drift. Fix only 11 exact labels/count strings, preserving all 90 cards/URLs/rights notes and the separate fallback.
2. Verify **public JS-on, JS-off, 320/390/768/1440** against the actual theme; inspect screenshot *pixels* and browser console/network, not only screenshot URLs.
3. Confirm the publishing mechanism can explicitly suppress first-publish email and social publicize. The authenticated **WP page connector allowlist does not expose** `_jetpack_dont_email_post_to_subs`; default newsletter settings alone are not sufficient.
4. Only after those gates pass, do the minimal authorized WordPress edit. Confirm edit-context readback + anonymous public page + metadata + search/keyboard + links.
5. Correct the separate Library parent **#77** source-count card in its own minimal scoped edit. Keep all existing page paths and cards.

**Current decision: HOLD LIVE MODIFICATIONS**. Only release control evidence and tooling have advanced.

Source trail: [Library](https://finalvestige.com/free-resources/) · [Research Sources](https://finalvestige.com/free-resources/research-sources/) · [Editorial Standards](https://finalvestige.com/editorial-standards/) · [Issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) · [Visual QA blocker #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) · [count-only PR #2318](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2318).

All new diagram/text/test fixtures are original; no third-party archival images, documents or rights-restricted media were copied. No new spending.
