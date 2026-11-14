# FV Investigations — Bohemia v3.6 method and artwork audit
**Run date:** 2026-11-14, Pacific. **Editorial decision:** HOLD; do not publish. **Scope:** Existing companion draft; no WordPress edit. **Cost:** $0.

## Coordination and collision checks
- Live Editorial Standards inspected: https://finalvestige.com/editorial-standards/ . Primary evidence, disagreement visibility and documentary rights standards remain operative.
- Live Journal inspected: https://finalvestige.com/blog/ . Landing page reports 66 investigations; recent entries are not Bohemia. The guessed /investigations/ path was inaccessible. The Journal remained readable.
- Authenticated WP posts-list searched `Bohemia` across published/draft/pending items: returned no Bohemia-titled post; the separately scoped `Caernarvon` draft #2151 is the only match. Exact readback: status `draft`, modified site-local `2026-11-12T12:44:30`, meta `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`; did not modify.
- GitHub issue #1463 (active investigation) and #1589 (production preview QA hold) read, plus recent issue comments and editorial drafts. No shared template, homepage, other agents' posts or branch was changed.
- Manuscript prior state v3.5; new v3.6 work confined to `docs/editorial/bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md`, and a uniquely named SVG.

## Primary/source checks, interpretation
1. **John A. Lopez et al., 2014**, “Examination of Deltaic Processes of Mississippi River Outlets—Caernarvon Delta and Bohemia Spillway in Southeastern Louisiana,” *GCAGS Journal* vol. 3, pp. 79–93; actual publisher original PDF https://www.gcags.org/Journal/2014.GCAGS.Journal/GCAGS.Journal.2014.vol3.p79-93.Lopez.et.al.pdf . **Actual page images inspected** for printed pp. **88, 89, 90 and 91** (PDF page indices 9–12). Printed p. 88 describes 317 points / 184 depth / 141 velocity / 104 dry; pp. 89–90 detail canals, road and mapped infilling; p. 90 reports USACE **2.5 mi² land loss 1932–2001**, USGS **2.99 mi² net land loss 1932–2010**, merged **3.4 mi² mapped loss**, separately USGS **1.08 mi² gain**, and bulk of loss in 1956–1973 and 1973–1975. Printed p. 91 distinguishes channelized flows and causation/maintenance hypotheses.
2. **Pontchartrain Conservancy**, “Bohemia Spillway,” current institutional research summary https://scienceforourcoast.org/bohemia-spillway . **Official HTML inspected 2026-11-14**: program since 2007; channelized 2011 flow, rare canal infilling, low land-loss rates after 1975 and geology as competing explanation. This is source **[55]**, not an independent measurement of the present-day landscape.
3. **Michael Hopkins, State of the Coast 2023 conference abstract** (existing entry [53]): rooted-vegetation mapping **2008–2021** for Mardi Gras Pass outfall, a different metric and area from 2014 Bohemia mapped land classification. Avoid forced arithmetic comparison.

**New editorial interpretation:** physical canal infilling can coexist with net loss when geography, land cover metrics, periods and mapping algorithms differ. It does not prove exclusive Mississippi-sediment origin, ownership resolution, post-2021 land gain, exact 2026 vegetation cover or beneficiary compensation. Neither the three historical mapped loss figures nor the distinct gain number is additive.

## Writing
- Recovered existing v3.5 draft via exact GitHub contents read before write; added narrative section **“The canal the marsh took back”** ahead of **“When the marsh did not grow in a straight line.”** Integrated [8], [53], and newly documented [55]; no claims from uninspected press images, interviews or field visits.
- Updated manuscript to **v3.6**, now **55 sequential source-ledger entries**. Source [55] is the official research institution; an exact-source caveat is preserved.
- GitHub update commits: narrative **`ec2689209e17243e9942b88a5c6d1f1c58c1c0a7`**, subsequent visual-QA annotation **`9a1bed0927b387edfb751358788be07a42aed956`**.

## Original visual provenance and QA
- Unique SVG: `docs/editorial/assets/bohemia-land-change-methods-1932-2010-2026-11-14.svg`. **Creator:** FV Investigations Studio. **Date:** 2026-11-14. **License/rights:** original studio-authored graphic for FV editorial reuse; no copied map pixels, archive photos, logos, remote fonts or borrowed image assets. **Primary data:** Lopez et al., 2014, printed p. 90. **Caption/alt:** recorded inline with the manuscript's Evidence figure.
- SVG committed `9fd6745455b21cfc41be45118b3b2a969143f343`, **Git content blob `459aa134daf1eca37c16a9812852e161918e8c65`**.
- SVG retrieved independently using GitHub connector, XML inspected for accessible title/description and absence of remote `image`/HTTP dependencies.
- Identical SVG source recreated locally for render. A trailing newline alone differed; running `git hash-object` on the source with that final newline omitted produced **exactly `459aa134daf1eca37c16a9812852e161918e8c65`**.
- Rendered PNGs via CairoSVG at **390 × 500** and **780 × 1000**, opened and visually inspected both: headings, numbers, dates, attribution and measurement caveat legible; no clipping/overlaps. Working paths: `/mnt/data/fv_investigations/bohemia-land-change-methods-390.png`, `...-780.png`; these are not WordPress uploads.
- **No authenticated live WordPress-theme render** or screen-size 1440 proof; the graphic is not cleared for live use until integrated-theme testing.

## Publication gate
**No WordPress changes, no new post, no mail, no social distribution, no shared template edits.** Caernarvon #2151 stays draft and unchanged. Companion draft not published. Open evidence: original claimant-level titles/check registers; 2015 levee-district escrow closing execution; post-2021 DNR advance-cost ledger and transfers; image-rights review for any borrowed documentary photographs; final legal/copyediting pass and production-theme responsive QA for actual article. Public claims of recent marsh gain remain unsupported.

Potential separate Grok angle **after** editorial clearance: “The canal the marsh took back,” comparing visualized 1932–2010 land-loss methods without calling it proof of present-day restoration or implying payments were withheld. Do not distribute now.
