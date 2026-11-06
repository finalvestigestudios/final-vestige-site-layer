# Apollo R168 — pinned WordPress source custody + forced-colors gallery repair (DRAFT / HOLD)

Parent: #150. Conversion governance: #820 / #818. Base: R167 draft branch at `d9465234d512696f2aec6cebc55f038768e0f3b9`. **No production or WordPress staging write is authorized.**

## Actual WordPress source witness, read-only, November 6, 2026

Read `wpcom_mcp_pages_get(site=finalvestige.com, id=2017, context=edit)`; page `/apollo-1-evidence-atlas/`, modified `2026-11-05T18:19:45`. Raw editor content: **96,288 JavaScript characters / 96,302 UTF-8 bytes**. SHA-256: `6948f3d62d91d08c27a3a4b71122fef6ef37bdd333c31f81c27db4ad95ce5e4c`. Nine opening/nine closing Gutenberg Custom HTML blocks; one original inline script. The old `t < 6 ? 0 : (t < 11.3 ? 1 : 2)` photo controller remains. R167 marker absent. Three source citations present inside the gallery: NASA S66-58038 (1966 training), S67-15717 (Jan. 1967 processing), KSC-20170124-PH_KLS01_0129 (2017 preserved hatch). This is **editor-source evidence, not installed-page visual acceptance**.

`wp_source_custody_gate.py` will generate a *local-only* preview only when supplied raw edit-context content matches the attested UTF-8 SHA-256, byte count, block/script counts, historical controller signature and exactly one of each NASA record within the gallery. It delegates the historical fix to R167 and inserts a scoped R168 CSS override inside the final existing Gutenberg block. Any drift causes **HOLD**, never auto-rebase, fallback citation substitution, or publication. Output manifest marks `approved_for_publish=false`. Production branch and original page stay unchanged.

## Visually observed correction

A real Chromium screenshot under `forced-colors: active` exposed a blank white text rectangle for the selected archival button when CSS used `Highlight/HighlightText`. R168's `ButtonFace/ButtonText` state and double border restore a readable 390px selected label without altering the chronology or NASA citations. Pixel regression on the center of the selected button: **209 dark pixels after fix vs 0 under deliberate old-color negative control**. This is an emulated high-contrast browser, not physical Windows High Contrast acceptance.

## Local exact-source QA (not WordPress acceptance)

Run from `experience2/apollo-r168`, with inherited `../apollo-r166` Python modules imported through the prescribed PYTHONPATH (or copy these three R168 files alongside the R167 modules for standalone audit):
`PYTHONPATH=.:../apollo-r166 python -m unittest -v test_wp_source_custody_gate`.

Dependencies: Python 3.11+, `playwright`, `Pillow`, installed Chromium (`CHROMIUM_PATH` optional). The test imports R167 `test_wp_block_pack.original()` as a **controlled Gutenberg fixture** and supplies a fixture-specific SHA witness. A separate negative test proves that this fixture is rejected by the *real* pinned WordPress witness. Two independent local runs: **4/4 unittest methods PASS** each; six source drift negative cases plus mismatched witness rejected; **12 Chromium contexts** per run at 320/360/390/768/1440/1920px with JS off/on, emulated touch, reduced motion and forced colors. Keyboard Home, CTA/link count preservation, chronology independence, three NASA citations, overflow and no-JS photo visibility tested. Six screenshots had identical SHA-256 between runs. Pixel negative control passes (209 vs 0). No observed page errors.

**Not executed:** actual WordPress staging browser, genuine axe-core, real image/CDN delivery, CSP, NVDA/VoiceOver, real LCP/CLS, exact GitHub-head hosted CI. No claimed production accessibility or commercial conversion.

## Editorial and revenue discipline

Primary NASA Apollo 204 investigation: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . Original image provenance: https://www.nasa.gov/image-detail/amf-s66-58038/ ; https://www.nasa.gov/image-detail/amf-s67-15717/ ; https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129 . Archival photographs are context, **not timestamped fire evidence**; no invented Atlas pin. NASA usage / identifiable-person rights are not cleared for paid advertising here.

Creator-led long-form Apollo traffic -> this cited Atlas -> **one relevant next action: Read original investigation**. A paid Apollo educator dossier is **not verified as an existing rights-cleared product**, therefore no purchase link, affiliate offer, fake SKU, or new tracking. Hypothesis only: clearer historical custody and readable mobile source controls can increase qualified readers continuing to the investigation, but this is NOT observed revenue. Before a later commercial CTA: verify SKU, rights, Payhip checkout, delivery, refund terms and matching visitor intent; reconcile independent paid orders and qualified UTMs in 7/30-day cohorts under #820. Grok owns scripts/distribution, Praxxis creator review, Claude release/analytics; founder must approve deployment. No traffic or sales claim made.

## Remaining release gate

Use the exact real WordPress editor export; confirm pinned source hash and review any new revision manually. On isolated staging, test Gutenberg serialization, CSP, NASA selected `currentSrc` and CDN, genuine axe, screen readers, 200–400% zoom, real-page LCP/CLS, and end-to-end navigation. Keep all original content and citations. Independent QA + founder/Claude production approval required; homepage PR #49 and original Research Desk PR #158 remain frozen.
