# Final Vestige Investigations — Bohemia v49o source, image and publication audit

**Cycle:** 2026-11-16, 22:30 Pacific. **Status:** HOLD / NOT APPROVED FOR PUBLICATION. **WordPress writes:** none. **Social/newsletter:** none. **Incremental paid spending:** $0.

## Scope and collision check

Continuing **The Spillway That Kept Its Names**, without starting a duplicate investigation. Work in the dedicated [Bohemia issue #2832](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/2832). [Issue #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) is **Caernarvon 1927**, not this manuscript. Shared [QA issue #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) covers authenticated WordPress screenshots; do not modify that area's ownership, #2151 or the homepage. The currently published WordPress Investigations/Journal list was checked against draft #2488, and [Editorial Standards](https://finalvestige.com/editorial-standards/) was read through authenticated WordPress page #17 (published; last modified September 9, 2026). Public web fetching received access/rate failures, not evidence of a site outage.

## New source and what it actually says

The Louisiana Joint Legislative Committee on the Budget / Cash Management Review Board posts **Act 361 of 2017** monthly **Escrow Fund Reporting** spreadsheets as PDFs.

1. **September 30, 2021 statement**, [official document](https://jlcb.legis.la.gov/Docs/2021/oct/October%202021%20RTC%20Act%20361%20of%202017%20monthly%20report%20-%20September.pdf), **printed page 4 / PDF zero-index page 3**: original page image inspected in the live PDF viewer on November 16, 2026. The relevant row identifies **Agency ISIS #431 — Department of Natural Resources, Office of the Secretary**, revenue org **1107**, expense org **4311**; purpose: advance-cost money received from **Bohemia Spillway claimants** for land-return claim review and administration. The beginning and ending monthly balance are each **$48,087.59**. Deposit and withdrawal cells for *that month* are blank.
2. **March 31, 2018 statement**, [official document](https://jlcb.legis.la.gov/Docs/2018/apr/RTC%20-%20April%202018%20-%20Act%20361%20of%202017%20Monthly%20Report.pdf), **printed page 4**: published PDF indexed table inspected and cross-compared; same claimant-cost account and **$48,087.59** at the month opening and closing, with dashes in movement cells. Original page screenshot request timed out; this is **extracted-text verification only**, not a visual pass.
3. Additional indexed monthly reports from 2019, 2020 and the 2021 sample repeat the same account and amount; no complete monthly series was audited. Searches for a verifiably later (2022–2026) report did not recover a later original-source statement for this account. **Do not claim that $48,087.59 is the 2026 balance.**

**Inference limits:** The document describes **applicant administrative-cost advances**, **not the Haspel & Davis settlement**, not a mineral-royalty reserve, and not court-registry payments. Two snapshots showing the same amount do not prove inactivity throughout the intervening years. The row does not name claimants, identify refund obligations, contain bank statements, show subsequent account closure, show beneficiaries receiving royalties, or establish any wrongdoing. Its parenthetical legislative-history description is an agency row label, not proof that the physical Bohemia Spillway was canceled.

**Analytical advancement:** Keep the three money trails separate: **(a) DNR 1107 applicant-cost escrow, (b) Orleans Levee District historical royalty revenue, and (c) court-ordered awards, court registry and settlement disbursements**. Correctly classifying the new $48,087.59 prevents artificial inflation of restitution totals and identifies a concrete unexamined 1107 general-ledger/refund-record route.

## Revised manuscript

[Reader Edition v49o](./bohemia-spillway-reader-cut-v49-2026-11-16.md) adds **“An escrow for the cost of applying”** immediately before the governmental royalty-accounting chapter: three new analytical paragraphs and a new graphic, with full numerical source entry **#67** and inline references. The two dates, agency, amount, account purpose and uncertainty are integrated in flowing prose rather than written as a sensational missing-money accusation.

Independent GitHub readback verified the file after commit **`a366531131d78e0419fb3ed8b69b1214558c104f`**. Automated numeric link audit: **67 numbered bibliography entries / 178 narrative numeric citation references / zero missing numbered targets**. This is structural integrity, **not** a substitute for full independent legal copy edit.

## Original artwork and rights ledger

[The Same Word. Different Money.](./assets/bohemia-escrow-distinction-v49o.svg) is an **original first-party vector** (Final Vestige Studios Investigations Editorial Research, created November 16, 2026, copyright Final Vestige Studios, all rights reserved). It uses no archival photograph, copyrighted third-party graphic, external script, network asset, paid service or AI reconstruction. Its source and factual limitations are in the SVG `<metadata>`, `<title>`, and `<desc>`.

- **Credit:** Original Final Vestige Studios evidence graphic, November 16, 2026; source: Louisiana Joint Legislative Committee on the Budget, September 30, 2021 statement, page 4.
- **Alt:** “The 2021 government escrow report lists $48,087.59 for DNR Bohemia claimant application-cost advances; it does not measure separate mineral-royalty judgment payments or beneficiary distributions.”
- **Caption:** “The same word, different money. Louisiana's September 2021 escrow report lists a $48,087.59 **DNR claimant-processing advance-cost** balance. The row neither establishes today's balance nor measures mineral-royalty restitution.”
- **Visual QA:** Matching authored SVG was rasterized with CairoSVG at **390px and 640px**; both resulting images were visually inspected for legible text, complete labels, readable cautions, no clipping and sound contrast. **Isolated artwork PASS**; not an authenticated WordPress production-theme screenshot and not a WordPress media upload. Re-read GitHub SVG **blob `50d613bb38b560e2416b608b118fd5372931db1f`** and confirmed title/description/metadata and absence of script/image/foreignObject/external href. Source-control asset commit **`34dcc0cf7cb557b54a2d214ffffea970ef001d52`**. The locally rasterized source was byte-checked against the GitHub asset: after removal of the file-final newline introduced by the local render fixture, its Git blob SHA-1 is exactly **`50d613bb38b560e2416b608b118fd5372931db1f`**, matching the independent repository readback. Thus 390px and 640px isolated pixel checks apply to the committed source.

Existing documentary WordPress media records authenticated this cycle: **#2484** NASA Earth Observatory / Joshua Stevens / USGS Landsat 8, February 13, 2023; **#2485** USDA Farm Service Agency NAIP / NASA Earth Observatory, September 20, 2007. Both retain credit, caption and alt text in WordPress. A new anonymous public byte load of both image URLs was attempted, but the web fetcher could not access them; **visitor rendering remains NOT VERIFIED**, not necessarily broken.

## WordPress state and release decision

Authenticated WordPress readback at end of cycle: **post #2488** is **draft**, site-local modified **2026-11-16T02:44:46**, featured media **#2484**, `jetpack_seo_noindex=true`, `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`; no mutation, staging, category change, mail send or publication. No current WP preview screenshots.

**HOLD gates:**
1. Independent specialist legal/editorial signoff across the original restitution statutes, liability and payment classifications; original settlement and claimant-level accounting, satisfaction and distribution records are still missing.
2. Original 2005 board financing, June 2005 settlement / August 15 installment, Bourgeois Bennett schedules and DNR escrow **1107** account opening, 2018–2026 monthly reconciliations, refund records or bank evidence.
3. Authenticated production-theme WordPress preview inspection at **390px and 1440px**, exact staged revision and responsive layout, image credits/alt, all link targets and source list.
4. Actual anonymous visitor JPEG byte loads of both documentary photos; publish first time only with `_jetpack_dont_email_post_to_subs=true` and automatic social sharing disabled, and independently inspect final live URL. Do not overwrite the shared theme or #2151.

**Distribution lane, not released:** The $48,087.59 administrative-cost-vs-royalty distinction could support Grok's *separate* source-linked explainer **only after publication and legal approval**. No social posts have been created.
