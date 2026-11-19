# Apollo Experience 2.0 — R470 optional-asset quarantine (staging only)

Parent: #150. Revenue/attribution coordination: #820 and business charter #818. Stacked on Apollo R469 PR #3082, not frozen homepage PR #49 or independent Research Desk PR #158. No WordPress, tracking, checkout, social, or production writes.

## Problem and fix

Before R470, an intact NASA catalogue with an altered optional CSS or JavaScript asset was replaced wholesale with a generic investigation link. This erased six source cards, three chronology moments, three EvidencePlates and evidence limitations from the browser/PDF presentation. A bad asset still must never run; however, it need not erase safe server-rendered content.

R470 validates optional assets independently. Altered CSS is omitted along with JS; altered JS is omitted while intact CSS remains. Missing assets retain progressive-enhancement behavior. In any quarantine mode, the reader receives a plain-language status notice, all six source cards, three chronology moments, three EvidencePlates, source review limits and the single free investigation CTA. Controls stay hidden, and no altered asset bytes are emitted. Unverified `KSC-20170124-PH_KLS01_0129` remains unlinked. This change does not grant media rights or turn research leads into accepted NASA records.

## Exact implementation custody (Git blob SHA-1)

- `apollo_rights_gallery.php`: `f341de9e889a5fc12fdc2c5680617d14b1b22ecc`
- `qa/r467_contract_gate.py`: `a8871489794778a5efdabcc3479ce46327c9c316`
- `qa/r470_quarantine_gate.py`: `8b389af6cb47660264749332a3e98814523737aa`
- CSS and JS remain byte-identical to the inherited R469 assets, pinned with SHA-256 in PHP.

## Local executed evidence

- PHP syntax: PASS.
- R470 Playwright genuine local Chromium: 70/70 contexts across 320, 390, 768, 1440 and 1920px; JS on/off; seven clean/missing/altered CSS/JS modes; keyboard, 390px touch, reduced-motion and forced-colors; no horizontal overflow or emitted attack sentinels.
- R470 tampered-both PDF: eight unique independently retrievable NASA/article/chronology source URLs and one contextual free investigation link; held catalogue lead remains unlinked; five-page PDF visually inspected.
- Inherited gates: R466 component integrity 9/9, R467 source control 26/26, R468 pairing 13/13 plus output assertions, R469 claim mutation 26/26 plus 13 positive invariants. R468 and R469 Chromium smoke: 14/14 contexts each. Suites overlap; do not add totals.
- Eight local screenshots and normalized PDF were reproduced on repeated executions with identical file hashes after screenshot focus/hover stabilization. Exact screenshots and manifests are in the reproducible R470 QA archive, not checked in as binary files.

## Blocked acceptance and revenue gates

Real browser navigation to localhost, file and data URLs returned `ERR_BLOCKED_BY_ADMINISTRATOR` in this environment; `set_content()` is NOT hosted WordPress acceptance. Genuine axe-core, navigated LCP/CLS, manual VoiceOver/NVDA checks, independent QD and exact-head green CI remain unavailable. Do not invent performance data. Founder must approve any actual release. Two archival identifier/source questions and marketing/astronaut-likeness licensing remain held. No confirmed Grok asset_id, qualifying human-session attribution, authenticated sellable educator SKU, delivered checkout, paid order or net revenue verified.

## Conversion-first owner handoff

**Offer → Funnel step → Blocker → Change/experiment → Evidence → Owner:** Original rights-cleared Apollo educator dossier → documentary-to-Atlas source exploration → an altered optional asset previously removed research proof → preserve provenance in native HTML and source PDF → local PASS / hosted HOLD → Apollo QA. Founder/Claude must confirm a product, rights and payment/fulfillment path before any paid CTA. Grok/Praxxis own creator asset review and approved asset_id; Claude owns consent-aware session/CTA-to-merchant measurement and verified net-revenue denominator under #820. No unrelated commerce is inserted into the historical research narrative.

NASA source anchors: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ ; source access is not licensing or agency endorsement.

**RELEASE: HARD HOLD.** No merge, deploy, WordPress write, emails, ad/affiliate activation, paid service or social publication.
