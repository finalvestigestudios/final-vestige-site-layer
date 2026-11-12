# R314 — Article #15 / Tool #104 dual-surface emergency messaging and privacy custody (HARD HOLD)

**Preparedness only | #136; conversion coordination #820 | 2026-11-12 PT**  
**DRAFT / NO MERGE / NO CMS / NO PUBLICATION. Qualified review and independent QD are not complete.**

## Exact authenticated upstream inputs
R313 parent commit: `c6b7cd8dc37cff7ab00100fdc6aee977e42816d9`. The new R314 validator pins these original, still-unmodified Git blobs:
- Article #15 `family-communication-plan.body.html`: `8ac8bd7dba3be15d477c15737e54d83364d72527`; metadata `dcad79faa8e0e6f1aef6db03e9e6e9451e19d8d3`.
- Tool #104 `family-reunification-card.body.html`: `be8698ac5d020476ff649d85813810e2000c6f98`; metadata `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`.
- JS `tools/reunion_card.js`: `b1a09b1eda1ae26f081de65b400a37bc19538035`.
- Inherited R313 gate: `209457045d1d44a18a26c1e2e31ddb8541bad49c`.

## Source-backed redlines requiring editorial and qualified assessment
1. **Both opening emergency notices:** "call 911 for anything life-threatening" is too narrow for immediate police/fire/ambulance assistance; Tool #104 additionally says to use texts rather than calls for everything else. Reconcile first with [911.gov](https://www.911.gov/calling-911/) and [911.gov FAQ](https://www.911.gov/calling-911/frequently-asked-questions/); availability of text-to-911 varies by jurisdiction. The source citation tokens remaining present are not safety approval.
2. **Both privacy surfaces plus Tool #104 SEO metadata:** Article #15 says the tool "keeps what you type on your own device"; Tool #104 asserts "It is not sent or saved. Closing the tab clears it"; its metadata claims "Nothing is stored." Static JS inspection alone cannot establish WordPress runtime storage/network behavior, third-party scripts, browser caching, print spool or clearing on tab close. Require actual signed-out browser, network, caching, tab/session and child privacy witnesses.
3. **No-JavaScript contradictory instruction:** Tool #104 displays a `<noscript>` warning saying "The form below still works and prints" while another `<noscript><style>` hides `#rc`. A blank printable card fallback exists, but that does not validate form accessibility or actual printing at common page sizes.
4. **Unsourced comparative child outcome:** Article #15 asserts a child given one script "is calmer" than a child warned about hazards. This comparative psychological effect requires evidence or removal in qualified editorial review. [CDC child reunification guidance](https://www.cdc.gov/children-and-school-preparedness/before-during-after/reunification.html) is useful planning context, not support for that exact comparative statement.
5. **Claim/context custody:** Archive retains all original citation markers, editorial reading depth, distinct `family-reunification-card` Tool #104 and `reunification-plan` Tool #102 identities. Do not automatically merge later Shelter descendants or assume source reuse equals qualified evidence.

## Fail-closed implementation
The new R314 gate checks the five original source hashes plus inherited R313 module hash; compares each surface's citation IDs to its metadata, route relation, editorial/safety draft states, visible emergency note, metadata/privacy language, child comparison, and no-JS contradictions; emits reproducible SHA-256 note witnesses. It explicitly returns `publication_authorized=false`, `independent_qd_pass=false`, `medical_safety_verified=false`, `actual_41_exports_verified=false`, and `paid_order_verified=false`. Even corrected synthetic copy stays **COPY_REVIEW_HARD_HOLD**.

**Execution scope:** 51 new adversarial unit tests + 297 inherited R310–R313 = **348 locally passing exact Git-blob-matched committed-scope synthetic tests**, plus Python compilation and missing-checkout rejection. No complete authenticated native checkout, `validate.py`, `build.py`, full repository suite, actual 41 generated WordPress exports, signed-out 320/390px/desktop browser/print tests, or qualified safety/QD. Do not report a native PASS.

**Current branch checks:** all 7 canonical Claude heads identical to frozen R200; Shelter descendants separately +6/+9 commits, unreconciled. QA PR #157 remains open draft. PR #169 remains open draft; one test still writes `_dup_test.json` in the source-tree directory. Homepage lead #1689 is a draft and was not touched.

## ONE conversion-first offer/funnel acceptance
| Offer → funnel step | Blocker → change/experiment | PASS/FAIL evidence → owner |
|---|---|---|
| Existing Grok family-contact post → public free archive `/preparedness/` | Authenticate a REAL published `asset_id` and permissible link placement, check landing intent + mobile accessibility | **UNVERIFIED** — Grok/Praxxis TASK-008 |
| Public free official resources → optional FREE #104 card | Correct dual-surface emergency/privacy copy, confirm print/no-JS/child-data, independent source/QD review; never gate life-safety instructions | **HARD HOLD** — Preparedness editorial/QD |
| Free guide → optional relevant PAID FV-owned practical pack | Inventory Products 001–015; verify ownership/licensing, purchase availability, approved price, delivery, merchant/returns and consent before paid CTA | **NO VERIFIED SELLABLE PREPAREDNESS SKU** — Founder/Commerce |
| `asset_id` qualified sessions → relevant CTA → confirmed lead (optional) → paid merchant order → refunds/fees → realized net | Join privacy-respecting first-party campaign evidence to independent settled merchant records, 7/30d cohorts and tiny-sample warnings | **NET REVENUE / 1,000 QUALIFIED HUMAN SESSIONS NOT COMPUTABLE** — Claude/Commerce |

**Draft free-resource CTA only (not live):** "Make a family contact plan together. Start with the free official-source Preparedness Archive." No paid CTA, retired water freebie, forced email gate, newly deployed trackers, or social task changes.

**Other preexisting hard holds preserved:** 10 substantive article bodies + 12 metadata revisions; USDA food source variant; two unqualified historical safety `approved` labels; #7 hazardous-water issues; six-tool number collisions; complete native 41 exports and human source/privacy review.