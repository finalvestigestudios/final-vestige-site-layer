# R300 · Preparedness metadata + CSS custody, frozen lineage and conversion gate
Date: 2026-11-11 PT · Issue #136 / charter #818 / conversion coordination #820
Status: **DRAFT / HARD HOLD / NO MERGE / NO PUBLICATION**

## Source authority and bounded change
Base: R299 draft PR #2093 exact HEAD `6eaeb0046e9190472fc7ebf2b9671fd4eb03a262`. Only this R300 review guard, its tests, and this audit are added; no original manuscripts, source registers, metadata, stylesheet, tools, WordPress exporters, public content, merchant offers, social posts, analytics or nav are changed.

Independent authenticated GitHub REST tree read of R299 found all **35 original article .meta.json** blobs and `preparedness/assets/preparedness.css` (Git blob `e354395cdb7985eb2fe16b99ca9fd66c9885557e`). Earlier R299 pinned six practical tools and nine JS files, but **did not pin these 36 native-builder inputs**. An attacker/accidental edit could change article descriptions, review flags, interpretation or CSS presentation, regenerate the exported HTML, and pass byte equivalence to the newly changed source. R300 closes that witness gap by fixing the exact source identity of all 36 inputs.

The independently pinned R200 manifest (Git blob `5822f9dfde21d1f3bdfc26658769d852c639438c`) provides the frozen 35 article metadata blob identifiers. For 23 metadata files the R299 integrated OID equals R200; for 12 files the R299 head has a different authenticated OID, explicitly carried as override, **not silently equated to the frozen file**. The override comparison emits unadjudicated provenance entries and no publication or QD approval.

Source guard `r300_metadata_css_pin_hold.py` requires pinned R299 validator blob `f1ba7018ac34f48e286119aa1dad38e2a669eca8` and R200 manifest before any successful path, rejects symlink ancestors/files, missing/extra metadata, mismatched bytes and CSS changes, and composes the earlier exact 41-export audit. All successful mechanical checks return `DRAFT_HARD_HOLD`, **never PASS, LIVE or VERIFIED SAFE**; missing witness means `INVALID_HARD_HOLD`. The CSS hash is a source-level pin only, not a cross-browser display proof.

## 35-article lineage (Git object comparisons, not editorial approvals)
- 35 unique article metadata files and 35 article body files present in authenticated R299 tree.
- Body OIDs differ from frozen R200 in **14** articles; meta OIDs differ in **12**.
- **9** articles differ in both; **5** body-only; **3** metadata-only; **18** identical in both.
- 12 metadata discrepancies are visible in R300 output and remain human-unadjudicated. Existing 14 body deltas remain in R299's report.
- The seven Claude cluster branches compared with their *correct* R200 custody SHAs on November 11: **7/7 identical, zero commits ahead/behind or changed paths**. Earlier R293/R294 divergent-head reports used the wrong pre-R200 baselines; do not repeat that error.

## Current review dependencies
- Independent safety QA PR #157: draft, HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (power drill/medication caution, review gate).
- Synthetic fixture PR #169: draft, HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Its upgrade fixture is now isolated in a temp copy, but `test_register_fragments_cannot_duplicate_ids` still uses `ROOT / 'sources' / 'fragments' / '_dup_test.json'` in the actual working tree; independent QA owns remediation and end-to-end execution.
- Homepage lead PR #1689: `f55c36b6598eec558dd8bb24e4c8988becc51be0`, unchanged by Preparedness.
- Article #7 hazardous water; Article #15/Tool #104 emergency dispatch, child privacy, printing, no-JS and accessibility; historic foods and agency citation disagreements remain HARD HOLD. No advice is declared medically or technically safe.

## Test receipts and limitations
- Locally executed exact committed R300 source/test files match Git blob OIDs (recorded in Issue #136).
- New R300 adversarial unit tests: **60/60 PASS**, including 35 separate per-article metadata mutation tests.
- R295–R299 inherited tests: **314/314 PASS**; combined **374/374 PASS** on synthetic/prototype fixtures.
- Python compilation PASS; intentionally incomplete authenticated checkout produces `INVALID_HARD_HOLD` and nonzero exit.
- Full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py` and all authentic 41 WP draft exports are **NOT EXECUTED/VERIFIED**. Container cannot resolve GitHub DNS for clone. Connector API reads do **not** constitute a full repository checkout.
- Independent QD, food/medical safety, privacy, WCAG/browser/print, citation URLs and rights reviews are **NOT COMPLETE**. No public changes.

## Offer → funnel step → blocker → acceptance experiment → evidence → owner
1. **Existing official-resource Preparedness page → family-plan reader:** currently safe public entry `https://finalvestige.com/preparedness/` links official free planning references, while original guides stay under review. Verify mobile reach, absence of misleading CTAs, current agency links. **READ-ONLY PUBLIC PAGE CONFIRMED, CAMPAIGN ATTRIBUTION NOT VERIFIED** · Preparedness QA.
2. **Existing published Grok family-reunification asset → source page:** authenticated matching `asset_id`, permissible mobile link and matching destination currently unavailable; verify via TASK-008, do not initiate content/posting. **NO VERIFIED MATCH** · Grok/Praxxis.
3. **Free guide → Tool #104 optional practical card:** no-JS / printed filled-form mismatch, private child-information scope and 911 wording need qualified safety + browser review. **HARD HOLD** · independent Preparedness QA.
4. **Free guide → ONE optional paid practical pack:** no rights-cleared, FV-owned/licensed, purchasable and audience-fitting Preparedness SKU with verified delivery established. Legacy Triage listing under Vested Wisdom is **NOT ACCEPTED** as FV inventory. Require product authorization, truthful claims, checkout/delivery tests and refund/disclosure terms. **NOT APPROVED** · Founder/Commerce.
5. **Qualified human sessions → relevant CTA → verified lead/purchase → refunds/fees → net revenue:** no verified session-to-order join; keep outbound/lead/checkout events separate from paid conversion, 7/30-day cohort net/1000 qualified sessions **NOT COMPUTABLE** · Claude analytics + Commerce.

Release ownership remains Founder and independent QD. This PR is a review-only custody extension and cannot lift any safety or business hold.
