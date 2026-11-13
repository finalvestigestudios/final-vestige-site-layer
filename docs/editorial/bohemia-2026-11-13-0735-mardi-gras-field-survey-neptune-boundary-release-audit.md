# FV Investigations — 13 November 2026, ~07:35–07:55 Pacific — source, image and release audit

**Status: research and manuscript draft advanced; release HOLD; no WordPress publication.** This audit belongs to ongoing GitHub Investigations issue #1463 and must not be mistaken for the shared site QA ticket #1589. No homepage, shared template, newsletter or social-post action.

## Preflight

- Authenticated WordPress site `finalvestige.com` confirmed active. Public Journal/Investigations topic list scanned and **no already-published Bohemia story identified**. Editorial Standards page #17 read in current production; it demands primary sources, verified quotes and numbers, qualified claims, image provenance, and corrections.
- The existing Caernarvon Investigations **draft #2151** was independently fetched via authenticated WordPress edit context. Status **draft**, modified **2026-11-12T12:44:30 site-local**, featured media 2148, categories [257245, 232815]. Meta: `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`, `jetpack_post_was_ever_published=false`. No changes made.
- GitHub issue **#1589** confirms release requires *actual editor-authenticated 390px and 1440px current-production-theme inspection* for draft #2151, exactly 82 blocks/43 sources for existing snapshot, and document QA. Structural/API checks and original figure screenshots do not replace authenticated theme QA. This run did not publish #2151.
- Active companion v1.8 was read from `docs/editorial/bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md`, SHA `c1dcc0128eab188d140c18cd88d1d1e8df7907e5`, before modifications.

## New source [39]: original 2024 field survey, visually checked

**Adam Songy and Michael Hopkins, Pontchartrain Conservancy, `Summary of Observed Channel Dimensions of Mardi Gras Pass in the Bohemia Spillway, Southeast Louisiana: January 2024 Update`, February 2024**; 14-page publisher-authored technical PDF at:
https://mississippiriverdelta.org/wp-content/blogs.dir/75/files//MGPass_Jan_2024.pdf

Actual PDF page images **zero-based pages 0, 9, 10, 11 and 13** inspected on 2026-11-13, especially **Table 2 at PDF page 11 / printed page 12**; source is an applied field report, not a peer-reviewed claim of future equilibrium.

- Survey counts **45 transects**. Survey **January 2023 vs January 2024**, **mean width 263 feet in both years**.
- Mean **cross-sectional area 6,247 square feet in 2023 and 6,201 in 2024** (net −46 ft²; **about −0.7%**); a comparison across 2023/2024 *surveys*, not directly measured annual freshwater discharge, marsh acreages, navigation safety or permanent channel stability.
- Some shallow/vegetated reaches required interpolated bathymetric levels.
- **Source's own ambiguity:** Table 1 contains a suspected carry-over “January 2023 survey” heading even in its January-2024 report; the conclusion verbally labels a bottom-elevation change from −23.8 to −23.6 ft as a “decrease” despite the arithmetic sign. The manuscript uses **Table 2** rather than relying on ambiguous Table 1 labels or that verbal direction.
- **Source conflict handling:** the report speculates an approach to equilibrium; FV **does not** claim long-term equilibrium from this short window or conflates it with the larger **Neptune Pass**.

## New geographic source [40], evidence limit and correction

**Restore the Mississippi River Delta, “View From Above: Neptune Pass,” 2023-05-19:** https://mississippiriverdelta.org/view-from-above-neptune-pass/ . Webpage inspected 2026-11-13. The coastal advocacy coalition places **Neptune Pass just south of the Bohemia Spillway**; NASA separately documents Neptune Pass as its own distributary: https://science.nasa.gov/earth/earth-observatory/the-widening-of-neptune-pass-151089/ . Source #40 provides orientation but is **not a cadastral boundary survey**, title instrument or proof that Neptune's banks are part of the private Bohemia restitution tracts. V1.8's loose “within the Bohemia reach” description was corrected to “farther downriver, near Buras,” explicitly **not the same place as Mardi Gras Pass**. Do not transform 2023 geography into disputed parcel ownership facts.

An advocacy website's 2024-labeled article appeared to contain material likely modified after initial posting, and also claims subsequent Corps stabilization; **excluded from evidence of 2025–26 construction completion or performance**. Still no Corps as-built, acceptance certificate or postwork hydraulic time series.

## Manuscript update and verification

- **v1.9** committed to same original manuscript path, Git commit **`90a8158931ef04d647a3949e16be27c9501f3737`**; independently fetched from GitHub afterward, blob SHA **`754fc3d5a4309d97eda9065c1f0e465fca95d3b6`**.
- About **9,319 whitespace-count manuscript article words**; **40 sequential source-ledger entries** [1]–[40]. No prior source entry renumbered. Added original 2024 two-date study and geographical distinction plus cautious language and new blockers. No interviews, exclusive archive visits, field measurements or rights permissions asserted.

## Original source-derived graphics (no historical-photography claims)

Both original diagrams newly drawn by **Final Vestige Studios, 2026-11-13**, from [39], © FV:
- Desktop SVG `docs/editorial/assets/bohemia-mardi-gras-2024-survey-comparison-2026-11-13.svg`, final blob SHA **`80144c38a89b2306e2ca579d51f68d566044f826`**, commit `d1eb92e8a61a02f971de85c05e63c95f0c928102`, viewBox 1120×650.
- Art-directed mobile SVG `docs/editorial/assets/bohemia-mardi-gras-2024-survey-comparison-mobile-2026-11-13.svg`, blob SHA **`067310a55505ad250a5f348ad64f84457ce4e79e`**, commit `590ffb4ac7950a0308be6702d3bd760f23047e57`, viewBox 600×820.

**Figure headline revised** from a potential permanence insinuation, “The pass did not keep widening,” to restrained **“Two surveys, little change”** in both exact committed assets. Both SVGs have full `<title>` / `<desc>`, viewBox and inline vector elements, **no external image, script, hotlink or third-party graphical objects**. Both GitHub files independently re-fetched and structurally checked against figures 263 / 6,247 / 6,201 / 0.7 / 45 and their final SHA.

**Responsive render QA:** The **exact mobile Git blob** reconstructed locally byte-for-byte (local `git hash-object` = `067310a55505ad250a5f348ad64f84457ce4e79e`), rasterized with CairoSVG at **390 pixels**, and visually examined. Result: chart title, year labels, units, −0.7% caveat and source footer are readable. Desktop SVG has source/hash/structural QA **but no actual independently inspected pixel rendering** as of this audit. Neither diagram is an AI historical reconstruction; they are original report-derived comparative bars with non-proportional text labels and chart scales. A 390px standalone image is **not** a 390px WordPress production-theme inspection.

**Caption:** “Pontchartrain Conservancy's January 2023 and 2024 survey of 45 Mardi Gras Pass transects found an unchanged mean width of 263 feet and a small change in estimated mean channel cross-sectional area from 6,247 to 6,201 square feet (−0.7%). The two surveys do not establish future channel stability or discharge.”
**Alt text:** “Original comparison figure: Mardi Gras Pass January 2023 and 2024 mean widths both 263 feet; cross-sectional area 6,247 to 6,201 square feet, roughly 0.7 percent lower. Based on Songy and Hopkins 2024 survey of 45 transects.”
**Rights:** © Final Vestige Studios. Research data cited above; vector design original. No archival image, publisher diagram, photo or logo copied. No WordPress asset upload made.

## Release gates and next research

1. **Caernarvon #2151:** logged-in post preview theme proof at **390px and 1440px** for current exact SHA; official USACE and USGS document reader checks, link/image/credit/alt and overflow QA per #1589. Only after verified pass should the post owner publish with explicit `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false` in the first publish request and independently read back public HTML/media.
2. **Bohemia:** exact legislative session-law scans (1984, 1985, 1992, and 1920s original acquisition/legislative instruments), title records and payee-level accounting, signed 2023 management memorandum, accessible 2024/25 Corps EAs and current as-built conditions, NASA asset-specific full-res rights, plus editorial structure/copyedit. The 2024 field report does not resolve all publication gates.
3. **Visuals:** desktop original SVG still requires full rendered visual proof, then approved WordPress-local media, responsive caption/alt and 390/1440 theme QA for the final manuscript; no images hotlinked or uploaded yet.
4. **Coordination:** relay the report and exact files to ongoing #1463. Social coordination to Grok later, **only after an article actually publishes**; do not distribute a draft.

**Status:** source-checks and GitHub writes succeeded; no WordPress updates, no social posts, no subscriber mail or newsletter sends, no shared template or homepage modifications. No paid service used, $0 new spending.
