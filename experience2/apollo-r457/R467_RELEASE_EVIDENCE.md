# R467 — Context-specific NASA source drawers + accessible archive navigation

**Staging-only Experience 2.0 candidate.** Additive branch from Apollo R466 #3065; all changes inside experience2/apollo-r457/. No edits to homepage PR #49, Research Desk PR #158, Claude production/analytics or Grok/Praxxis Drive task queue. Not installed in WordPress.

## Implementation
- Twelve native source disclosures now identify their particular archival ID, event date or evidence claim in the summary itself; repeated generic disclosure labels were insufficient for a reader navigating source headings.
- One intra-page keyboard skip link moves directly to the six-record catalogue. A focusable, per-instance list ID is linked to every one of the five keyboard/touch filter buttons with aria-controls. Two gallery instances have unique IDs.
- CSS remains SHA-256 integrity-pinned. Updated optional EvidencePlate PHP module is SHA-256 pinned as well. Missing enhancement modules preserve the core evidence; modified assets are rejected.
- Existing six archival references (four NASA ID accepted, two archival ID/URL mapping holds), three ChronologyRail moments, three EvidencePlates, one original free investigation CTA, printable source URLs, no-JavaScript content and rights boundaries retained. No photograph, NASA branding, invented map pin or commercial image license.

## Reproduction / evidence (2026-11-18 PT)
Run from the experience2/apollo-r457 directory:
1. php -l apollo_rights_gallery.php && php -l evidence_plates.php
2. python qa/r467_contract_gate.py
3. python qa/r466_integrity_gate.py
4. python qa/r466_evidence_gate.py
5. python qa/r467_http_browser_gate.py

Local test report: PHP lint passed; **R467 source contract 26 assertions passed**; inherited optional module gate **9 assertions passed**; inherited EvidencePlate Chromium/PDF **112 checks passed**; new responsive browser test **14 contexts passed** (320, 360, 390, 768, 1024, 1440, 1920; JS enabled/disabled). All five full-page screenshots reproduced with identical SHA-256 across two runs; PDF links checked (9 distinct NASA destinations, 1 full free investigation destination), and PDF generated with fixed metadata reproduced byte-identically across two runs. These are overlapping forms of assurance, not unique-user traffic or conversion evidence.

Important **HOLD_NOT_RUN**: navigation from Chromium was blocked with ERR_BLOCKED_BY_ADMINISTRATOR even for localhost/data/file, so the new browser runner exercised page.set_content for interactions. It does **not** fabricate navigated LCP/CLS. The optional axe script requires a real locally supplied pinned axe-core file; none was available, so genuine axe-core = HOLD_NOT_RUN. No installed WordPress staging, Assembler theme/caching test, screen-reader manual test, independent QA or field Core Web Vitals. Production release is HARD HOLD.

## Conversion-first, source-linked experiment

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|
| Original Apollo classroom dossier → verified paid order | No rights-cleared purchasable SKU, merchant checkout proof, fulfillment, refund ledger | Founder + Claude independently approve real offer *before* any paid CTA | COMMERCIAL HOLD; no paid sales | Founder/Claude |
| Grok's Apollo long-form/Shorts → qualified Atlas arrival | Published immutable asset_id, exact destination/UTM and human sessions unverified | Grok preserves content ownership; Praxxis independently reviews genuine published link; Claude validates approved landing and existing consent-safe measurement | UNKNOWN; no social post or visit claimed | Grok/Praxxis/Claude |
| Atlas source comparison → one free investigation | Repeated generic source drawers and lengthy keyboard travel may reduce research trust | R467 adds contextual source names and direct in-page navigation; test against approved staging and assistive tech | LOCAL PASS; HOSTED/axe/MANUAL HOLD | Apollo QA/QD |
| Qualified session → confirmed lead (if chosen) → verified order → net receipts/1000 | No first-party verified sessions, confirmed leads, merchant orders, refunds/fees or 7/30-day cohorts | Claude uses existing approved measurement; distinguish click from purchase; no duplicate scripts | NOT COMPUTABLE | Claude Commerce |

Intended user journey: **verified Grok Apollo documentary → Apollo Evidence Atlas → free source-backed educator inquiry → [full original investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → separately verified/approved original educator product**. No commerce inserted in historical claims.

NASA sources: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) and [2017 tribute](https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/). Two archive identifier associations remain HOLD, including S67-19766 and KSC-20170124-PH_KLS01_0129. NASA source accessibility does not itself license astronaut likenesses, photograph reuse for products, or NASA endorsement. This PR does not address those permissions.

**Release gate:** approved staging host, real axe, navigated LCP/CLS, independent screen-reader and QD acceptance, verified rights and commerce, green exact-HEAD CI, and explicit founder authorization. No deployment, WordPress write, affiliate activation, social posting, email or spend.
