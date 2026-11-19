# R475 — E467 CDC child-card source and claim-scope reconciliation

**Preparedness-only reviewer artifact · Issue #136 / business #820 / charter #818 · DRAFT / HARD HOLD / NO PUBLICATION · 2026-11-18 PT.**

## New integration finding and precise change

Editorial E466 had authenticated the CDC *Backpack Emergency Card* catalog entry, **not** the PDF. Editorial E467 subsequently fetched and visually inspected the **actual one-page 2020 CDC PDF**. Both its **Child's Backpack Card** and **Guardian's Wallet Card** are child-specific and contain child name, date of birth, address, school, medical/allergy and emergency-contact fields. The guardian card also has a healthcare-specialist field. An optional FV *minimal adult general-contact note* is **not** the CDC guardian wallet card. Do not silently rewrite E466's catalog-only historical witness: it is a dated custody record; E467's later direct PDF inspection is a separately pinned later observation.

- E467 independent memo: https://github.com/finalvestigestudios/final-vestige-site-layer/blob/28e10b233eb110b03603b6c8f3e4a8868d41d5f0/preparedness/editorial-reviews/E467_ARTICLE15_CDC_2020_GUARDIAN_WALLET_PDF_VISUAL_HARD_HOLD.md ; Git blob `68de3215599eddf04b1f63a75558da203a5969c7`.
- CDC 2020 one-page PDF: https://stacks.cdc.gov/view/cdc/139829/cdc_139829_DS1.pdf ; original source date July 14, 2020 (CDC Stacks catalog), not a 2025 page.
- CDC current child-card guidance dated December 16, 2025: https://www.cdc.gov/children-and-school-preparedness/keeping-safe/index.html . It lists child name, DOB, medical/allergy and family/school/emergency contacts but **does not explicitly list a home address**. Absence does not imply prohibition or permission.
- CDC school preparedness dated December 24, 2025: https://www.cdc.gov/children-and-school-preparedness/before-during-after/index.html . School contacts and authorized pickup matter; an independently printed card is not pickup authorization.
- FERPA school-emergency disclosure rules do not certify security/privacy of a lost parent-created paper card.
- **Original Article #15 and Tool #104 remain untouched:** blobs `8ac8bd7...` and `be8698a...` (full pinned IDs in JSON crosswalk). Both are draft / safety pending. Tool #102 is a separate tool.

## Engineering deliverable

Read-only `tools/r475_cdc_card_source_scope_gate.py` and immutable-review `reviews/r475_cdc_2020_2025_child_card_claim_crosswalk.json` pin nine original and independent editorial evidence IDs; separate 2020/2025 URL, dates, reading depth and asserted field sets; distinguish both CDC child-specific printed cards from FV's optional minimal contact-note concept. The validator blocks citation-source substitution, overreading a source, invented child-address rules, school-pickup claims, FERPA compliance, false QD/privacy/native-build approval, fictional product/social/settlement flags and loss of the original four Git blob pins. It checks the original files and independent E467 memo SHA when a complete authenticated checkout and independent memo copy are supplied, **always exiting 2**, never granting QD PASS. It writes no user, child or site data.

**Tests:** run `python -m unittest discover -s preparedness/tests -p 'test_r475*.py' -v`; for the inherited isolated R472–R475 subset run `python -m unittest discover -s preparedness/tests -p 'test_r47*.py'`. Both are synthetic structural tests. Qualified child safety/medical/accessibility review is outside their scope.

### Blockers and release checks

| Gate | State / owner |
|---|---|
| Reviewed and authorized purpose-specific card copy; school/childcare/clinician input | UNADJUDICATED / Preparedness QD |
| Rights and claim crosswalk registration for **new** CDC sources (no fake original cite IDs) | UNADJUDICATED / Preparedness QD |
| Live JS data storage/transmission behavior and printed card disclosure | NOT VERIFIED / Claude engineering |
| Mobile keyboard, print, actual 200% zoom and AT | NOT VERIFIED / Qualified QA |
| Full native 35-article `validate.py`, `build.py`, actual WP/private-preview exports, all previous citation gates | NOT EXECUTED in isolated file-only environment |
| Independent QA #157 and fixture PR #169/#2205 | Remain separate, review-only, unmerged |
| Food Article #11 twelve exposures, five disputed source records, nine forks, 17 divergences, 32 shared-URL groups | HUMAN ADJUDICATION OPEN |
| Qualified human QD, founder release | HARD HOLD |

## Conversion-first explicit acceptance (no offer invented)

| OFFER → FUNNEL | BLOCKER → CHANGE/EXPERIMENT | EVIDENCE / OWNER |
|---|---|---|
| **One verified existing FV Preparedness owned pack** → real paid order | No authenticated live payable SKU, cleared rights, merchant checkout, delivery, refunds or settlements; founder/commerce must privately verify before paid CTA | HOLD / Founder-Commerce |
| **An already published Grok family-contact/reunification asset** → **existing free /preparedness/** | No independently verified immutable asset_id, real spoken hook, rights, permalink or signed-out mobile destination; Praxxis independently check Grok's **existing** asset only, never create/overwrite a creator task | UNMATCHED / Grok-Praxxis |
| Free, original Article #15 → optional clearly labeled **free** Tool #104 | Child privacy/card purpose, CDC crosswalk, source/citation and PDF/print safety hold; avoid suggesting original unreleased Tool #104 to visitors | HARD HOLD / Preparedness-QD |
| Qualified human session → relevant CTA → consented confirmed lead (when applicable) → independently verified paid order → refunds/fees → realized net revenue | No attributable 7/30-day session denominator, consent-valid confirmed leads or merchant reconciliations; reuse Claude's measurement contract, **no additional tracking script** | NOT COMPUTABLE / Claude-Commerce |

Track 7-/30-day cohorts, net revenue per 1,000 **qualified human sessions**, confirmed orders, refunds/fees and tiny-sample uncertainty when actual records exist. Views, CTA clicks, checkouts and email signups are not paid purchases.

**No original draft overwrite, source-register edit, public archive/catalog, WordPress, navigation, analytics deployment, social post, email, vendor charge, merchant/affiliate activation, purchase claim or QD approval.**
