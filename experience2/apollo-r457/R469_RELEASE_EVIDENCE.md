# Apollo Experience 2.0 — R469 staging-only custody sprint

## Scope and problem

Predecessor: R468 draft PR #3077 (`review/apollo-r468-custody-pairing-20261118`), final predecessor SHA `1a0ad3ad08c818a8cd5ab28a66265e4a67529c58`. Changes here are **only** under `experience2/apollo-r457/`. Frozen homepage #49, independent Research Desk #158, main, WordPress, analytics and Grok/Praxxis TASK-008 are untouched. Nothing in this package is installed, merged, or approved for production.

R468 bound six NASA candidate records to IDs, dates, statuses and URLs, but a valid identifier could still silently inherit another photograph's credit, explanatory role, evidentiary limit or verification note. Also the unverified `KSC-20170124-PH_KLS01_0129` candidate lookup was a clickable NASA link and would appear among apparently actionable PDF citations despite independent catalogue acceptance remaining on HOLD.

## Change and implementation

1. `fv457_claim_custody_contract()` pins SHA-256 of each record's UTF-8 JSON array `[role, credit, boundary, source_check]` in human-reviewable record-ID order. `fv457_valid()` now validates both R468 identity metadata and R469 explanatory provenance. An editorial correction MUST intentionally revise the contract and rerun all tests. This is a same-file consistency safeguard, **not** independent verification of NASA facts or rights.
2. `fv457_source_link_eligible()` allows accepted direct NASA image-detail URLs and the verified **article** URL for `S67-19766` while not implying that portrait ID is accepted. It withholds the unresolved 0129 *candidate lookup* from both native details hyperlink and printed PDF link annotations. The candidate ID and precise HOLD language remain plainly readable, including without JavaScript and in print; no evidence record is removed.
3. No external media, geocoordinates, speculative relation edges, tracking, affiliate/merchant links, WordPress writes, new business offer or other CTA added. The sole next action remains the complete free Apollo investigation.

NASA source proof / media boundary: Apollo 204 Review Board `https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/` (probable arc, no conclusive singular ignition point); NASA Media/Brand Guidelines `https://www.nasa.gov/nasa-brand-center/` and `https://www.nasa.gov/nasa-brand-center/advertising-guidelines/` (no implied endorsement; restrictions on identifiers and publicity rights). Access to a NASA source does not establish commercial promotional permission.

## Executed reproducible checks (LOCAL; not hosted)

- PHP `-l` PASS for source gallery and evidence plates.
- New R469 adversarial source review: **26/26 bad claim mutations rejected** (role, credit, boundary, source-review note for each of six records, plus two semantic swaps); **13/13 positive custody, hold, source, rendering and single-CTA assertions**.
- Inherited R466 optional integrity gate **9/9 PASS**; R467 source/accessibility contracts **26/26 PASS**; R468 source pairing **13/13 invalid pairings rejected**; R468 local Chromium **14/14 contexts PASS**.
- New R469 Playwright: **14/14 real Chromium local PHP-injected contexts** at 320/360/390/768/1024/1440/1920px, JavaScript on/off, 390px touch, keyboard filter activation, reduced motion, 768px forced colors, zero JavaScript exceptions and no horizontal overflow.
- Chromium-generated PDF after an active filter: **eight distinct working-context NASA destinations**, including direct records, the verified NASA article, chronology/plate reports; **one FV free investigation destination**. The candidate 0129 URL is **not** a PDF URI link; its labelled HOLD is retained as text. This is structural link-presence verification, not live network resolution of every link.
- Four responsive screenshots + normalized PDF + JSON results reproduced in **two consecutive executions with identical SHA-256 hashes**. `qa/r469_archive_gate.py` builds a reproducible ZIP with fixed metadata/entry ordering.

### Known acceptance gaps — explicit HARD HOLD

- Browser navigation to localhost / file / data URLs returns `ERR_BLOCKED_BY_ADMINISTRATOR` in this runtime. Playwright `set_content` measures neither navigated LCP nor real navigated CLS; field p75 LCP/INP/CLS unmeasured.
- Genuine pinned axe-core library unavailable here; DOM semantics assertions **are not** axe. Hosted WordPress staging, independent NVDA/VoiceOver, independent QD and CI green on exact head are unverified.
- Two NASA source associations remain on HOLD: `S67-19766` ID mapping and `KSC-20170124-PH_KLS01_0129` candidate catalogue identity/date/credit. Rights for a paid original educator dossier, checkout/fulfillment, live campaign asset ID, qualified-human cohort traffic, confirmed leads, paid orders, fees and refunds are not authenticated.
- No acceptance without founder-specific approval; never auto-merge or deploy.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer and funnel | Blocker | Change or controlled experiment | Result | Owner |
|---|---|---|---|---|
| Original rights-cleared Apollo teacher dossier → paid checkout | No validated SKU, media rights, verified checkout or fulfillment | Defer paid CTA; require founder/Claude product and payment proof first | HOLD | Founder / Claude |
| Grok Apollo long-form → qualified Evidence Atlas landing | Live Grok asset ID, UTM mapping and human visits unverified | Single source-backed Atlas destination; request asset-specific mapping from Grok through existing Praxxis workflow | UNKNOWN | Grok / Praxxis |
| Atlas source custody → complete free investigation | Unverified catalogue candidate incorrectly presented as actionable; explanatory claims vulnerable to silent swap | Withhold one unsupported hyperlink, pin six claim records, preserve print/no-JS and exactly one contextual free CTA | LOCAL PASS / HOSTED HOLD | Apollo QA / independent QD |
| Confirmed paid orders → net revenue/1k qualified sessions | Merchant orders, refunds/fees, 7/30-day sessions missing | Do not infer revenue from CTA events; Claude may reconcile existing consented measurement | NOT COMPUTABLE | Claude commerce |

**Flagship fit:** Apollo 1 inward-opening hatch / documented fire investigation for an educator/history research audience. Offer a source-bounded chronology and free investigation, never a sales overlay within the tragedy narrative. Once sellability is proven, separately evaluate a rights-cleared original teacher dossier; hypothesis is improved source trust and qualified progression, not confirmed conversion uplift.

Cross-reference #150, #820, #818. No homepage PR #49 changes, no Research Desk #158 branch edits, no Grok publication/queue overwrite, no affiliate activation, no email, no spend.
