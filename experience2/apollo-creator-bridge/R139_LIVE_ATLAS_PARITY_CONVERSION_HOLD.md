# Apollo R139 — Published WordPress Atlas parity and conversion QA

2026-11-05 — STAGING HOLD. Source of truth: #150; commercial attribution: #820; charter: #818. Draft stacked on PR #1078. No changes to homepage PR #49, Research Desk PR #158, WordPress, Grok TASK-008 or merchants.

## Read-only production discovery

A WordPress read-only pages-list and pages-get establishes published WordPress page ID 2017, title Apollo 1: The Evidence Atlas, URL https://finalvestige.com/apollo-1-evidence-atlas/, last-modified field 2026-11-04T17:09:24. Separately published post ID 434, The Hatch Opened Inward, is at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/. The Atlas points to the full investigation. The older Apollo URL in R138 is a synthetic TEST FIXTURE; never use it in public campaigns. WordPress published metadata does NOT prove real HTTP browser acceptance or approval of this standalone staging work.

## Findings from actual WordPress page source

Ran the exact GitHub R139 gate against the WordPress pages-get HTML (96,184 characters). Six uniquely identified evidence records, 37 NASA source anchors including the Apollo 204 Review Board, and zero unresolved internal fragment references detected. Three NASA-branded photographs are already embedded using Final Vestige WordPress uploads; all three have alt text and intrinsic dimensions in source. No individual commercial-use/rights-review receipts were provided to this lane. This is a review warning, NOT a conclusion that the existing editorial uses are unlawful. No speculative map pins were found.

CRITICAL CONVERSION GAP: There is NO worksheet anchor to #classroom-preview and NO target element with that ID in the published Atlas. The staging prototype's free worksheet route is therefore not live there. Existing on-page next actions include Begin the evidence and Read the full investigation, which must not be mislabeled as the worksheet. No Payhip/checkout anchor was seen. No verifiable Apollo educator SKU, fulfilled purchase or attributed net revenue established.

The WordPress source includes one inline script and two inline style blocks; this is not a browser accessibility, performance or policy verdict. The page was not tested in an unrestricted browser.

## Implemented staging audit

R139_published_atlas_parity_gate.cjs accepts a read-only WordPress metadata/content snapshot, checks expected page URL/ID/status, six record IDs, NASA source link, missing/broken fragments, image structure, media-review uncertainty, free worksheet path and checkout link candidates. It emits only safe aggregate counts, source-gate blockers and STAGING_HOLD status. Even a caller-provided positive media rights flag cannot grant clearance. Test via: node --test experience2/apollo-creator-bridge/test_r139_published_atlas_parity_gate.cjs.

No WordPress content copied into the repository; this module does not fetch, post, collect visitor data, load photos or assert merchant sales. To repeat the real-page audit, acquire an authorized read-only WordPress pages-get snapshot for ID 2017, then supply its data to auditPublishedAtlas(data,{independentlyReviewedLandingUrl:'https://finalvestige.com/apollo-1-evidence-atlas/'}). Independently verify live browser navigation.

## Controlled creator-to-commerce route

Flagship: Apollo 1, The Hatch Opened Inward. Audience: grades 6–9 history/science educators and homeschool teachers. Grok owns videos/Shorts, sources, asset IDs and distribution; Praxxis owns independent creator review. After actual Grok publication proof, the reviewed actual Atlas URL may be a creator destination; this alone is not qualified human traffic.

One relevant nonintrusive next action is the already available Read the full investigation link, until a real, accessible free worksheet destination is deployed and approved; do NOT create a broken #classroom-preview CTA. An original, rights-cleared teacher-ready evidence kit is a hypothesis, not a verified sellable offer; withhold paid CTA until Payhip SKU, rights, delivery, refunds and founder approval are independently documented. Reuse #820 UTM and existing approved measurement only. Never treat clicks, visits or leads as sales.

## Priority plan — OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

1. Proposed educator dossier → paid order: no accepted Apollo SKU. Audit actual Payhip product, license, rights, delivery, refunds before checkout link. BLOCKED. Claude/Growth + Founder.
2. Grok long-form → real Atlas: old candidate URL synthetic. Bind only to WP-observed ID 2017 URL and independently verify live browser and Grok asset. WP metadata OBSERVED; public navigation/Grok NOT VERIFIED. Apollo QA + Grok/Praxxis.
3. Atlas → free resource: worksheet fragment absent. Design accessible no-JS link only after real worksheet destination is verified. SOURCE PARITY FAIL. Apollo QA + Claude site lead.
4. NASA gallery → provenance/trust: three WordPress-hosted NASA images present, rights receipts not supplied. Perform item-level editorial and promotional-use review, then browser QA. REVIEW OPEN. Research/rights editor.
5. Confirmed order → realized net revenue: missing independent purchase/refund/fee evidence. Reuse #820 7/30-day qualified-human-session cohort scorecard. NOT COMPUTABLE. Claude/Analytics.

No new tracking scripts, external media reuse, geo pins, map edges, purchases, posts, CMS writes, or production releases. Browser Chromium continues returning ERR_BLOCKED_BY_ADMINISTRATOR in this environment. Native exact-head CI, unrestricted Playwright/axe, 320–1920 responsive checks, LCP/CLS, independent editorial/rights review, Assembler compatibility and founder signoff remain release requirements.
